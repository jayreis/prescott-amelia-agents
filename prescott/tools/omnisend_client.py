"""
OmnisendClient — Multi-client Omnisend API wrapper.

Mirrors the architecture of klaviyo_client.py. Resolves API keys from the
Master Google Sheet "Clients" tab (authoritative source), with fallback to
each client's local .env file.

API coverage:
  - Campaigns: list, stats (sent/opened/clicked/bounced/unsubscribed)
  - Automations: list with status and message structure
  - Contacts: count, growth by date range
  - Segments: list

What the Omnisend API does NOT expose (must be entered manually):
  - Revenue per campaign or automation (dashboard-only in Omnisend)

Usage:
    from omnisend_client import OmnisendClient

    oc = OmnisendClient("example-brand")
    campaigns = oc.list_campaigns(status="sent")
    report    = oc.weekly_report("2026-04-26", "2026-05-02")

CLI:
    python3 omnisend_client.py "example-brand" campaigns
    python3 omnisend_client.py "example-brand" automations
    python3 omnisend_client.py "example-brand" report --week 2026-04-26
"""

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

import requests

from brand_config import get_client_row
from config import CLIENTS_BASE_PATH

# ── Config ──────────────────────────────────────────────────────────────────

V3_BASE = "https://api.omnisend.com/v3"
V5_BASE = "https://api.omnisend.com/v5"

# Folder slug overrides for clients whose folder name differs from their sheet
# name. Add your own as needed.
_FOLDER_SLUGS: dict[str, str] = {}

_key_cache: dict[str, str] = {}


# ── Key resolution ───────────────────────────────────────────────────────────

def _client_slug(client_name: str) -> str:
    lower = client_name.strip().lower()
    return _FOLDER_SLUGS.get(lower, lower.replace(" ", "-"))


def _key_from_sheet(client_name: str) -> Optional[str]:
    """Resolve via brand_config — dedicated single-brand sheet first, then Master Sheet.
    Raises ValueError (propagated from get_client_row) if the matched row is inactive."""
    row = get_client_row(client_name)
    if not row:
        return None
    key = row.get("ESP Private API Key", "").strip()
    return key if key and key.lower() != "none" else None


def _key_from_env(client_name: str) -> Optional[str]:
    slug = _client_slug(client_name)
    env_path = CLIENTS_BASE_PATH / slug / ".env"
    if not env_path.exists():
        return None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OMNISEND_API_KEY="):
                val = line.split("=", 1)[1].strip()
                return val if val and val.lower() != "none" else None
    return None


def resolve_key(client_name: str) -> str:
    normalized = client_name.strip()
    if normalized in _key_cache:
        return _key_cache[normalized]
    key = _key_from_sheet(normalized) or _key_from_env(normalized)
    if not key:
        raise ValueError(
            f"No Omnisend API key found for '{client_name}'. "
            f"Add it to the ESP Private API Key column in the Clients tab."
        )
    _key_cache[normalized] = key
    return key


# ── Client class ─────────────────────────────────────────────────────────────

class OmnisendClient:

    def __init__(self, client_name: str):
        self.client_name = client_name
        self.api_key     = resolve_key(client_name)
        self._headers    = {"X-API-KEY": self.api_key}

    # ── HTTP helpers ──────────────────────────────────────────────────────

    def _get(self, url: str, params: dict = None) -> dict:
        for attempt in range(4):
            r = requests.get(url, headers=self._headers, params=params or {}, timeout=30)
            if r.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()
        return {}

    def _paginate_v3(self, endpoint: str, list_key: str, params: dict = None) -> list:
        """Cursor-based pagination for v3 endpoints."""
        results = []
        url = f"{V3_BASE}/{endpoint.lstrip('/')}"
        p = {**(params or {}), "limit": 100}
        while url:
            data = self._get(url, p)
            items = data.get(list_key) or []
            if isinstance(items, dict):
                items = [items]
            results.extend(items)
            nxt = data.get("paging", {}).get("next")
            url = nxt if nxt else None
            p = {}
        return results

    def _paginate_v5(self, endpoint: str, list_key: str, params: dict = None) -> list:
        """Cursor-based pagination for v5 endpoints."""
        results = []
        url = f"{V5_BASE}/{endpoint.lstrip('/')}"
        p = {**(params or {}), "limit": 100}
        while url:
            data = self._get(url, p)
            items = data.get(list_key) or []
            results.extend(items)
            cursor = data.get("paging", {}).get("next")
            url = cursor if cursor else None
            p = {}
        return results

    # ── Campaigns ─────────────────────────────────────────────────────────

    def list_campaigns(self, status: str = None) -> list:
        """
        List campaigns with engagement statistics.
        status: 'sent', 'draft', 'scheduled', or None for all.
        Returns list of dicts with computed open_rate, ctr, bounce_rate.
        Revenue is NOT available via API — returns None for revenue fields.
        """
        params = {}
        if status:
            params["status"] = status
        raw = self._paginate_v3("campaigns", "campaign", params)
        enriched = []
        for c in raw:
            sent      = c.get("sent", 0) or 0
            opened    = c.get("opened", 0) or 0
            clicked   = c.get("clicked", 0) or 0
            bounced   = c.get("bounced", 0) or 0
            unsubbed  = c.get("unsubscribed", 0) or 0
            complained = c.get("complained", 0) or 0
            open_rate  = round(opened / sent * 100, 2) if sent else 0.0
            ctr        = round(clicked / sent * 100, 2) if sent else 0.0
            bounce_rate = round(bounced / sent * 100, 2) if sent else 0.0
            enriched.append({
                "id":           c.get("campaignID") or c.get("id"),
                "name":         c.get("name", ""),
                "subject":      c.get("subject", ""),
                "status":       c.get("status", ""),
                "sent_at":      c.get("startDate") or c.get("sentAt", ""),
                "sent":         sent,
                "opened":       opened,
                "clicked":      clicked,
                "bounced":      bounced,
                "unsubscribed": unsubbed,
                "complained":   complained,
                "open_rate":    open_rate,
                "ctr":          ctr,
                "bounce_rate":  bounce_rate,
                "revenue":      None,  # Not available via Omnisend API — enter manually
            })
        return enriched

    def get_campaign(self, campaign_id: str) -> dict:
        data = self._get(f"{V3_BASE}/campaigns/{campaign_id}")
        c = data if "campaignID" in data else data.get("campaign", data)
        sent      = c.get("sent", 0) or 0
        opened    = c.get("opened", 0) or 0
        clicked   = c.get("clicked", 0) or 0
        bounced   = c.get("bounced", 0) or 0
        return {
            **c,
            "open_rate":   round(opened / sent * 100, 2) if sent else 0.0,
            "ctr":         round(clicked / sent * 100, 2) if sent else 0.0,
            "bounce_rate": round(bounced / sent * 100, 2) if sent else 0.0,
            "revenue":     None,
        }

    # ── Automations ───────────────────────────────────────────────────────

    def list_automations(self, status: str = None) -> list:
        """List automations. status: 'enabled', 'disabled', or None for all."""
        autos = self._paginate_v5("automations", "automations")
        if status:
            autos = [a for a in autos if a.get("status") == status]
        return autos

    # ── Contacts / List Health ─────────────────────────────────────────────

    def count_new_subscribers(self, after: str, before: str) -> int:
        """
        Count new subscribers in a date range.
        after/before: ISO 8601 strings e.g. '2026-04-26T00:00:00Z'
        """
        params = {
            "createdAt[after]":  after,
            "createdAt[before]": before,
            "status":            "subscribed",
            "limit":             1,
        }
        data = self._get(f"{V3_BASE}/contacts", params)
        return data.get("paging", {}).get("totalCount", 0) or 0

    def count_unsubscribes(self, after: str, before: str) -> int:
        """Count unsubscribes (status change) in a date range."""
        params = {
            "updatedAt[after]":  after,
            "updatedAt[before]": before,
            "status":            "unsubscribed",
            "limit":             1,
        }
        data = self._get(f"{V3_BASE}/contacts", params)
        return data.get("paging", {}).get("totalCount", 0) or 0

    def count_total_contacts(self) -> int:
        data = self._get(f"{V3_BASE}/contacts", {"limit": 1})
        return data.get("paging", {}).get("totalCount", 0) or 0

    # ── Segments ──────────────────────────────────────────────────────────

    def list_segments(self) -> list:
        return self._paginate_v5("segments", "segments")

    # ── Weekly Report ─────────────────────────────────────────────────────

    def weekly_report(self, week_start: str, week_end: str = None) -> dict:
        """
        Pull all data needed for the master reporting sheet for a given week.
        week_start: 'YYYY-MM-DD' (Monday of the week)
        week_end:   'YYYY-MM-DD' (optional, defaults to 7 days later)

        Returns dict with keys matching rawdata tab columns.
        Revenue fields return None — must be entered manually in the sheet.
        """
        start_dt = datetime.strptime(week_start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if week_end:
            end_dt = datetime.strptime(week_end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            end_dt = start_dt + timedelta(days=7)

        after  = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        before = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Campaigns sent this week
        all_campaigns = self.list_campaigns(status="sent")
        week_campaigns = [
            c for c in all_campaigns
            if c.get("sent_at") and after <= c["sent_at"] < before
        ]

        # Aggregate campaign metrics
        total_sent    = sum(c["sent"]    for c in week_campaigns)
        total_opened  = sum(c["opened"]  for c in week_campaigns)
        total_clicked = sum(c["clicked"] for c in week_campaigns)
        total_bounced = sum(c["bounced"] for c in week_campaigns)

        blended_open_rate  = round(total_opened  / total_sent * 100, 2) if total_sent else 0.0
        blended_ctr        = round(total_clicked / total_sent * 100, 2) if total_sent else 0.0
        blended_bounce_rate = round(total_bounced / total_sent * 100, 2) if total_sent else 0.0

        # List health
        new_subs  = self.count_new_subscribers(after, before)
        unsubs    = self.count_unsubscribes(after, before)
        net_growth = new_subs - unsubs

        # Campaign names for the week
        campaign_names = ", ".join(c["name"] for c in week_campaigns) if week_campaigns else ""

        return {
            "week_start":        week_start,
            "client":            self.client_name,
            "platform":          "Omnisend",
            "campaign_revenue":  None,   # Enter manually from Omnisend dashboard
            "flow_revenue":      None,   # Enter manually from Omnisend dashboard
            "total_revenue":     None,   # Enter manually from Omnisend dashboard
            "open_rate":         blended_open_rate,
            "ctr":               blended_ctr,
            "new_subs":          new_subs,
            "unsubs":            unsubs,
            "net_list_growth":   net_growth,
            "bounce_rate":       blended_bounce_rate,
            "campaign_name":     campaign_names,
            "campaign_segment":  "All Contacts" if week_campaigns and week_campaigns[0].get("allContacts") else "",
            "_campaigns_detail": week_campaigns,
        }


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OmnisendClient CLI")
    parser.add_argument("client",  help="Client name e.g. 'example-brand'")
    parser.add_argument("command", choices=["campaigns", "automations", "segments", "report", "contacts"],
                        help="Resource to fetch")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--week",   help="Week start date YYYY-MM-DD (for report command)")
    args = parser.parse_args()

    oc = OmnisendClient(args.client)

    if args.command == "campaigns":
        items = oc.list_campaigns(status=args.status)
        print(f"\n{args.client} — Campaigns ({len(items)} total)\n")
        for c in items:
            rev = f"  rev: ${c['revenue']}" if c['revenue'] is not None else "  rev: (manual entry)"
            print(f"  [{c['id'][:8]}] {c['name'][:50]:<52} {c['status']:<8} "
                  f"sent:{c['sent']:>6}  open:{c['open_rate']:>5}%  ctr:{c['ctr']:>5}%  bounce:{c['bounce_rate']:>4}%{rev}")

    elif args.command == "automations":
        items = oc.list_automations(status=args.status)
        print(f"\n{args.client} — Automations ({len(items)} total)\n")
        for a in items:
            msgs = a.get("messages", [])
            print(f"  [{a['id'][:8]}] {a['name']:<45} {a['status']:<10} {len(msgs)} message(s)")

    elif args.command == "segments":
        items = oc.list_segments()
        print(f"\n{args.client} — Segments ({len(items)} total)\n")
        for s in items:
            print(f"  [{s.get('id','')[:8]}] {s.get('name','')}")

    elif args.command == "contacts":
        total = oc.count_total_contacts()
        print(f"\n{args.client} — Total contacts: {total:,}")

    elif args.command == "report":
        week = args.week or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        r = oc.weekly_report(week)
        print(f"\n{args.client} — Weekly Report for week of {r['week_start']}\n")
        print(f"  Campaigns sent:    {len(r['_campaigns_detail'])}")
        for c in r['_campaigns_detail']:
            print(f"    - {c['name']} | sent: {c['sent']:,} | open: {c['open_rate']}% | ctr: {c['ctr']}%")
        print(f"\n  Blended open rate: {r['open_rate']}%")
        print(f"  Blended CTR:       {r['ctr']}%")
        print(f"  Bounce rate:       {r['bounce_rate']}%")
        print(f"  New subscribers:   +{r['new_subs']:,}")
        print(f"  Unsubscribes:      -{r['unsubs']:,}")
        print(f"  Net list growth:   {r['net_list_growth']:+,}")
        print(f"\n  Campaign revenue:  (not available via API — enter from Omnisend dashboard)")
        print(f"  Flow revenue:      (not available via API — enter from Omnisend dashboard)")
