"""
KlaviyoClient — Multi-client Klaviyo API wrapper.

Resolves API keys from the Master Google Sheet "Clients" tab (authoritative
source), with fallback to each client's local .env file. No hardcoded keys.

Usage:
    from klaviyo_client import KlaviyoClient

    kv = KlaviyoClient("example-brand")
    flows = kv.list_flows(status="live")
    actions = kv.get_flow_actions("SrLf62")

CLI (for quick debugging):
    python3 klaviyo_client.py "example-brand" flows
    python3 klaviyo_client.py "example-brand" flows --status live
    python3 klaviyo_client.py "example-brand" metrics
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

import requests

from brand_config import get_client_row
from config import CLIENTS_BASE_PATH

# ── Config ─────────────────────────────────────────────────────────────────────

KLAVIYO_BASE_URL   = "https://a.klaviyo.com/api"
KLAVIYO_REVISION   = "2025-01-15"

# Folder slug overrides for clients whose folder name differs from their sheet
# name (e.g. "Acme Co" -> "acmeco"). Add your own as needed.
_FOLDER_SLUGS: dict[str, str] = {}

# Session-scoped key cache — avoids re-reading the sheet on every call
_key_cache: dict[str, str] = {}


# ── Key resolution ─────────────────────────────────────────────────────────────

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
            if line.startswith("KLAVIYO_API_KEY="):
                val = line.split("=", 1)[1].strip()
                return val if val and val.lower() != "none" else None
    return None


def resolve_key(client_name: str) -> str:
    """Resolve Klaviyo API key for a client. Sheet → .env → error."""
    normalized = client_name.strip()
    if normalized in _key_cache:
        return _key_cache[normalized]

    key = _key_from_sheet(normalized) or _key_from_env(normalized)
    if not key:
        raise ValueError(
            f"No Klaviyo API key found for '{client_name}'. "
            f"Add it to the Clients tab of the master sheet or to "
            f"{CLIENTS_BASE_PATH}/{_client_slug(client_name)}/.env"
        )
    _key_cache[normalized] = key
    return key


# ── Client class ───────────────────────────────────────────────────────────────

class KlaviyoClient:

    def __init__(self, client_name: str):
        self.client_name = client_name
        self.api_key     = resolve_key(client_name)
        self._headers    = {
            "Authorization": f"Klaviyo-API-Key {self.api_key}",
            "revision":      KLAVIYO_REVISION,
            "Content-Type":  "application/json",
        }

    # ── Internal HTTP ──────────────────────────────────────────────────────

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Single request with automatic retry on 429 rate limit."""
        for attempt in range(4):
            r = getattr(requests, method)(url, headers=self._headers, timeout=30, **kwargs)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 2 ** (attempt + 1)))
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        r.raise_for_status()
        return r

    def _get(self, endpoint: str, params: dict = None) -> dict:
        return self._request("get",
            f"{KLAVIYO_BASE_URL}/{endpoint.lstrip('/')}",
            params=params or {}
        ).json()

    def _post(self, endpoint: str, payload: dict) -> dict:
        return self._request("post",
            f"{KLAVIYO_BASE_URL}/{endpoint.lstrip('/')}",
            json=payload
        ).json()

    def _patch(self, endpoint: str, payload: dict) -> dict:
        return self._request("patch",
            f"{KLAVIYO_BASE_URL}/{endpoint.lstrip('/')}",
            json=payload
        ).json()

    # Klaviyo enforces different max page sizes per endpoint
    _PAGE_SIZES = {
        "flows":      50,
        "lists":      10,
        "segments":   10,
        "metrics":    50,
        "campaigns":  50,
        "templates":  10,
        "profiles":   100,
    }

    def _paginate(self, endpoint: str, params: dict = None, max_results: int = 500) -> list:
        """Fetch all pages from a list endpoint, up to max_results records."""
        resource = endpoint.strip("/").split("/")[0]
        page_size = self._PAGE_SIZES.get(resource, 10)
        results = []
        url = f"{KLAVIYO_BASE_URL}/{endpoint.lstrip('/')}"
        p = {**(params or {}), "page[size]": min(page_size, max_results)}
        while url and len(results) < max_results:
            data = self._request("get", url, params=p).json()
            results.extend(data.get("data", []))
            url = data.get("links", {}).get("next")
            p = {}
        return results[:max_results]

    # ── Flows ──────────────────────────────────────────────────────────────

    def list_flows(self, status: str = None, name_contains: str = None) -> list:
        flows = self._paginate("flows/")
        if status:
            flows = [f for f in flows if f["attributes"]["status"] == status]
        if name_contains:
            flows = [f for f in flows if name_contains.lower() in f["attributes"]["name"].lower()]
        return flows

    def get_flow(self, flow_id: str) -> dict:
        return self._get(f"flows/{flow_id}/")

    def get_flow_actions(self, flow_id: str) -> list:
        return self._paginate(f"flows/{flow_id}/flow-actions/")

    def get_flow_action(self, action_id: str) -> dict:
        return self._get(f"flow-actions/{action_id}/")

    def get_action_messages(self, action_id: str) -> list:
        return self._paginate(f"flow-actions/{action_id}/flow-messages/")

    def get_flow_message(self, message_id: str, include_template: bool = False) -> dict:
        params = {"include": "template"} if include_template else {}
        return self._get(f"flow-messages/{message_id}/", params)

    def update_flow_status(self, flow_id: str, status: str) -> dict:
        return self._patch(f"flows/{flow_id}/", {
            "data": {"type": "flow", "id": flow_id, "attributes": {"status": status}}
        })

    # ── Campaigns ─────────────────────────────────────────────────────────

    def list_campaigns(self, channel: str = "email", status: str = None) -> list:
        f = f"equals(messages.channel,'{channel}')"
        if status:
            f += f",equals(status,'{status}')"
        return self._paginate("campaigns/", {"filter": f})

    def get_campaign(self, campaign_id: str) -> dict:
        return self._get(f"campaigns/{campaign_id}/")

    def create_campaign(self, name: str, list_id: str, subject: str,
                        from_email: str, from_label: str,
                        preview_text: str = "", template_id: str = None) -> dict:
        msg_attrs = {
            "channel": "email",
            "content": {
                "subject": subject,
                "preview_text": preview_text,
                "from_email": from_email,
                "from_label": from_label,
            }
        }
        if template_id:
            msg_attrs["template"] = {"data": {"type": "template", "id": template_id}}
        return self._post("campaigns/", {
            "data": {
                "type": "campaign",
                "attributes": {
                    "name": name,
                    "audiences": {"included": [list_id]},
                    "send_options": {"use_smart_sending": True},
                    "tracking_options": {
                        "add_utm": True,
                        "utm_params": [
                            {"name": "utm_source",   "value": "Klaviyo"},
                            {"name": "utm_medium",   "value": "email"},
                            {"name": "utm_campaign", "value": name},
                        ]
                    },
                    "campaign-messages": {"data": [{"type": "campaign-message", "attributes": msg_attrs}]}
                }
            }
        })

    def schedule_campaign(self, campaign_id: str, send_time: str) -> dict:
        """send_time: ISO 8601 string, e.g. '2026-05-15T10:00:00+00:00'"""
        return self._post(f"campaign-send-jobs/", {
            "data": {
                "type": "campaign-send-job",
                "attributes": {"scheduled_at": send_time},
                "relationships": {"campaign": {"data": {"type": "campaign", "id": campaign_id}}}
            }
        })

    # ── Lists & Segments ──────────────────────────────────────────────────

    def list_lists(self) -> list:
        return self._paginate("lists/")

    def get_list(self, list_id: str) -> dict:
        return self._get(f"lists/{list_id}/")

    def create_list(self, name: str) -> dict:
        return self._post("lists/", {
            "data": {"type": "list", "attributes": {"name": name}}
        })

    def list_segments(self) -> list:
        return self._paginate("segments/")

    def get_segment(self, segment_id: str) -> dict:
        return self._get(f"segments/{segment_id}/")

    def create_segment(self, name: str, definition: dict) -> dict:
        return self._post("segments/", {
            "data": {"type": "segment", "attributes": {"name": name, "definition": definition}}
        })

    # ── Metrics ───────────────────────────────────────────────────────────

    def list_metrics(self) -> list:
        return self._get("metrics/").get("data", [])

    def get_metric(self, metric_id: str) -> dict:
        return self._get(f"metrics/{metric_id}/")

    def query_metric_aggregate(self, metric_id: str, measurements: list,
                                start_date: str, end_date: str,
                                interval: str = "day", group_by: list = None,
                                filter_: str = None) -> dict:
        attrs = {
            "metric_id":    metric_id,
            "measurements": measurements,
            "interval":     interval,
            "page_size":    500,
            "timezone":     "America/New_York",
            "filter":       f"and(greater-or-equal(datetime,{start_date}),less-than(datetime,{end_date}))",
        }
        if group_by:
            attrs["by"] = group_by
        if filter_:
            attrs["filter"] = filter_
        return self._post("metric-aggregates/", {"data": {"type": "metric-aggregate", "attributes": attrs}})

    # ── Templates ─────────────────────────────────────────────────────────

    def list_templates(self) -> list:
        return self._paginate("templates/")

    def get_template(self, template_id: str) -> dict:
        return self._get(f"templates/{template_id}/")

    def create_template(self, name: str, html: str) -> dict:
        return self._post("templates/", {
            "data": {"type": "template", "attributes": {"name": name, "editor_type": "CODE", "html": html}}
        })

    def update_template(self, template_id: str, html: str = None, name: str = None) -> dict:
        attrs = {}
        if html:  attrs["html"] = html
        if name:  attrs["name"] = name
        return self._patch(f"templates/{template_id}/", {
            "data": {"type": "template", "id": template_id, "attributes": attrs}
        })

    # ── Profiles ──────────────────────────────────────────────────────────

    def list_profiles(self, filter_: str = None, max_results: int = 100) -> list:
        params = {}
        if filter_:
            params["filter"] = filter_
        return self._paginate("profiles/", params, max_results=max_results)

    def get_profile(self, profile_id: str) -> dict:
        return self._get(f"profiles/{profile_id}/")

    def upsert_profile(self, email: str, properties: dict = None) -> dict:
        attrs = {"email": email}
        if properties:
            attrs["properties"] = properties
        return self._post("profile-import/", {
            "data": {"type": "profile", "attributes": attrs}
        })


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KlaviyoClient CLI")
    parser.add_argument("client",  help="Client name, e.g. 'example-brand'")
    parser.add_argument("command", choices=["flows", "campaigns", "lists", "segments", "metrics", "templates"],
                        help="Resource to list")
    parser.add_argument("--status", help="Filter by status (flows/campaigns)")
    parser.add_argument("--name",   help="Filter by name contains (flows)")
    args = parser.parse_args()

    kv = KlaviyoClient(args.client)

    if args.command == "flows":
        items = kv.list_flows(status=args.status, name_contains=args.name)
        print(f"\n{args.client} — Flows ({len(items)} total)\n")
        for f in items:
            a = f["attributes"]
            print(f"  [{f['id']}] {a['name']:<55} {a['status']:<8} trigger: {a['trigger_type']}")

    elif args.command == "campaigns":
        items = kv.list_campaigns(status=args.status)
        print(f"\n{args.client} — Campaigns ({len(items)} total)\n")
        for c in items:
            a = c["attributes"]
            print(f"  [{c['id']}] {a.get('name',''):<55} {a.get('status','')}")

    elif args.command == "lists":
        items = kv.list_lists()
        print(f"\n{args.client} — Lists ({len(items)} total)\n")
        for l in items:
            print(f"  [{l['id']}] {l['attributes']['name']}")

    elif args.command == "segments":
        items = kv.list_segments()
        print(f"\n{args.client} — Segments ({len(items)} total)\n")
        for s in items:
            print(f"  [{s['id']}] {s['attributes']['name']}")

    elif args.command == "metrics":
        items = kv.list_metrics()
        print(f"\n{args.client} — Metrics ({len(items)} total)\n")
        for m in items:
            print(f"  [{m['id']}] {m['attributes']['name']}")

    elif args.command == "templates":
        items = kv.list_templates()
        print(f"\n{args.client} — Templates ({len(items)} total)\n")
        for t in items:
            print(f"  [{t['id']}] {t['attributes']['name']}")
