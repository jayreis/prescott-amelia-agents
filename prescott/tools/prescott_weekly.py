#!/usr/bin/env python3
"""
prescott_weekly.py — Prescott's weekly performance data reader.

Pulls 2 weeks of campaign + flow data for a given client from the Master
Email Client Reporting Sheet, then prints a structured report Prescott uses
as the basis for his Monday narrative and brief writing.

Usage:
    python3 prescott_weekly.py --client "example-brand"
    python3 prescott_weekly.py --all
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

from config import MASTER_SHEET_ID


def connect():
    from google_auth import get_gspread_client
    if not MASTER_SHEET_ID:
        raise RuntimeError("MASTER_SHEET_ID is not set — see .env.example at the repo root.")
    gc = get_gspread_client()
    return gc.open_by_key(MASTER_SHEET_ID)


def parse_currency(val):
    try:
        return float(val.replace("$", "").replace(",", "").strip())
    except Exception:
        return 0.0


def parse_pct(val):
    try:
        return float(val.replace("%", "").strip())
    except Exception:
        return 0.0


def parse_int(val):
    try:
        return int(val.replace(",", "").strip())
    except Exception:
        return 0


def get_rawdata(sh, client, weeks=2):
    ws   = sh.worksheet("rawdata")
    rows = ws.get_all_values()
    if not rows:
        return []

    headers = [h.strip() for h in rows[0]]
    # Expected: Week Start, Client, Platform, Campaign Revenue, Flow Revenue,
    #           Total Revenue, Open Rate, CTR, New Subs, Unsubs, Net List Growth, Bounce Rate

    data = []
    for row in rows[1:]:
        if not any(row):
            continue
        rec = dict(zip(headers, row))
        if rec.get("Client", "").strip().lower() == client.strip().lower():
            data.append(rec)

    # Sort by Week Start descending, take last N weeks
    def parse_date(r):
        try:
            return datetime.strptime(r.get("Week Start", "").strip(), "%Y-%m-%d")
        except Exception:
            try:
                return datetime.strptime(r.get("Week Start", "").strip(), "%m/%d/%Y")
            except Exception:
                return datetime.min

    data.sort(key=parse_date, reverse=True)
    return data[:weeks]


def get_flow_performance(sh, client, weeks=2):
    ws   = sh.worksheet("flow_performance")
    rows = ws.get_all_values()
    if not rows:
        return []

    headers = [h.strip() for h in rows[0]]
    # Expected: Week Start, Client, Platform, Flow Name, Revenue, Open Rate,
    #           CTR, Unsubscribes, Delivered, Performance Flag

    data = []
    for row in rows[1:]:
        if not any(row):
            continue
        rec = dict(zip(headers, row))
        if rec.get("Client", "").strip().lower() == client.strip().lower():
            data.append(rec)

    def parse_date(r):
        try:
            return datetime.strptime(r.get("Week Start", "").strip(), "%Y-%m-%d")
        except Exception:
            try:
                return datetime.strptime(r.get("Week Start", "").strip(), "%m/%d/%Y")
            except Exception:
                return datetime.min

    data.sort(key=parse_date, reverse=True)
    return data[:weeks * 10]   # up to 10 flows × 2 weeks


def fmt_pct_change(current, prior):
    if prior == 0:
        return "N/A (no prior data)"
    change = ((current - prior) / prior) * 100
    arrow  = "▲" if change >= 0 else "▼"
    return f"{arrow} {abs(change):.1f}%"


def print_report(client, rawdata, flows):
    sep = "─" * 64
    print(f"\n{sep}")
    print(f"  PRESCOTT WEEKLY REPORT — {client.upper()}")
    print(f"  Generated: {datetime.now().strftime('%A, %B %-d %Y')}")
    print(sep)

    # ── Campaign performance ──────────────────────────────────────────────────
    print("\n[ CAMPAIGN PERFORMANCE — LAST 2 WEEKS ]\n")

    weeks_shown = []
    if not rawdata:
        print("  No data found for this client in the rawdata tab.")
    else:
        for rec in rawdata:
            week    = rec.get("Week Start", "Unknown")
            c_rev   = parse_currency(rec.get("Campaign Revenue", "0"))
            f_rev   = parse_currency(rec.get("Flow Revenue", "0"))
            t_rev   = parse_currency(rec.get("Total Revenue", "0"))
            open_r  = parse_pct(rec.get("Open Rate", "0"))
            ctr     = parse_pct(rec.get("CTR", "0"))
            new_s   = parse_int(rec.get("New Subs", "0"))
            unsubs  = parse_int(rec.get("Unsubs", "0"))
            net     = parse_int(rec.get("Net List Growth", "0"))
            bounce  = parse_pct(rec.get("Bounce Rate", "0"))

            camp_name = rec.get("Campaign Name", "").strip()
            camp_seg  = rec.get("Campaign Segment", "").strip()

            print(f"  Week of {week}")
            print(f"    Revenue      — Campaign: ${c_rev:,.0f}  |  Flow: ${f_rev:,.0f}  |  Total: ${t_rev:,.0f}")
            if camp_name:
                seg_part = f"  →  Segment: {camp_seg}" if camp_seg else ""
                print(f"    Campaign:    {camp_name}{seg_part}")
            print(f"    Engagement   — Open Rate: {open_r:.1f}%  |  CTR: {ctr:.2f}%  |  Bounce: {bounce:.2f}%")
            print(f"    List Health  — New Subs: +{new_s}  |  Unsubs: -{unsubs}  |  Net Growth: {'+' if net >= 0 else ''}{net}")
            print()
            weeks_shown.append({
                "week": week, "c_rev": c_rev, "f_rev": f_rev, "t_rev": t_rev,
                "open_r": open_r, "ctr": ctr, "bounce": bounce,
                "new_s": new_s, "unsubs": unsubs, "net": net,
            })

        if len(weeks_shown) == 2:
            curr, prev = weeks_shown[0], weeks_shown[1]
            print(f"  Week-over-week")
            print(f"    Total Revenue  : {fmt_pct_change(curr['t_rev'],  prev['t_rev'])}")
            print(f"    Open Rate      : {fmt_pct_change(curr['open_r'], prev['open_r'])}")
            print(f"    CTR            : {fmt_pct_change(curr['ctr'],    prev['ctr'])}")
            print(f"    Net List Growth: {fmt_pct_change(curr['net'],    prev['net'])}")
            print()

    # ── Flow performance ──────────────────────────────────────────────────────
    print(f"\n[ FLOW PERFORMANCE ]\n")

    if not flows:
        print("  No flow data found. Flows may not yet be active for this client.")
    else:
        seen_flows = {}
        for rec in flows:
            name  = rec.get("Flow Name", "Unknown")
            week  = rec.get("Week Start", "")
            flag  = rec.get("Performance Flag", "").strip()
            rev   = parse_currency(rec.get("Revenue", "0"))
            open_r= parse_pct(rec.get("Open Rate", "0"))
            ctr   = parse_pct(rec.get("CTR", "0"))

            if name not in seen_flows:
                seen_flows[name] = []
            seen_flows[name].append({"week": week, "flag": flag, "rev": rev, "open_r": open_r, "ctr": ctr})

        for name, records in seen_flows.items():
            latest = records[0]
            flag_display = f"  ⚠  {latest['flag']}" if latest["flag"] else "  ✓  On track"
            print(f"  {name}")
            print(f"    Revenue: ${latest['rev']:,.0f}  |  Open: {latest['open_r']:.1f}%  |  CTR: {latest['ctr']:.2f}%")
            print(f"    Flag   : {flag_display}")
            print()

    # ── Signals for Prescott ─────────────────────────────────────────────────
    print(f"\n[ SIGNALS — FOR PRESCOTT'S NARRATIVE ]\n")

    signals = []

    if rawdata:
        curr = weeks_shown[0] if weeks_shown else {}
        if curr.get("open_r", 0) < 25:
            signals.append("Open rate below 25% — subject line or deliverability issue. Review last 2 sends.")
        if curr.get("ctr", 0) < 1.0:
            signals.append("CTR below 1% — CTA strength or offer relevance may be weak.")
        if curr.get("bounce", 0) > 0.5:
            signals.append("Bounce rate above 0.5% — list hygiene review recommended.")
        if curr.get("unsubs", 0) > curr.get("new_s", 1) * 0.5:
            signals.append("Unsub rate is high relative to new subs — frequency or targeting may be off.")
        if curr.get("f_rev", 0) == 0 and curr.get("c_rev", 0) > 0:
            signals.append("Zero flow revenue — flows are not active or not converting. Priority build.")

    if not flows:
        signals.append("No flows running — all revenue is campaign-driven. Welcome + Abandoned Cart are highest-priority builds.")

    if signals:
        for s in signals:
            print(f"  → {s}")
    else:
        print("  No major flags. Program appears stable.")

    print(f"\n{sep}\n")


def get_active_clients(sh):
    ws   = sh.worksheet("Clients")
    rows = ws.get_all_values()
    active = []
    for row in rows[1:]:
        if len(row) >= 4 and row[3].strip().upper() == "TRUE" and row[0].strip():
            active.append(row[0].strip())
    return active


def main():
    parser = argparse.ArgumentParser(description="Prescott weekly data reader")
    parser.add_argument("--client", help="Client name exactly as in Clients tab")
    parser.add_argument("--all", action="store_true", help="Run report for all active clients")
    args = parser.parse_args()

    if not args.client and not args.all:
        parser.print_help()
        sys.exit(1)

    sh = connect()

    if args.all:
        clients = get_active_clients(sh)
        print(f"Running for {len(clients)} active clients: {clients}")
    else:
        clients = [args.client]

    for client in clients:
        rawdata = get_rawdata(sh, client)
        flows   = get_flow_performance(sh, client)
        print_report(client, rawdata, flows)


if __name__ == "__main__":
    main()
