"""
ops_logger.py — Shared logging utility for email automation scripts.

Appends a timestamped row to the 'Ops Log' tab and updates the 'Monday Report'
tab in the Master Google Sheet after each script run.

Usage:
    from ops_logger import OpsLogger

    log = OpsLogger()
    log.start("example-brand", "some_script.py")
    # ... do work ...
    log.success(metric1="38.2% open rate", metric2="$12,400 rev", metric3="20 campaigns")
    # or
    log.failure("Connection timeout on Klaviyo API")
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

from google_auth import get_gspread_client
from config import MASTER_SHEET_ID

_gc = None
_sh = None

def _connect():
    global _gc, _sh
    if _sh is None:
        if not MASTER_SHEET_ID:
            raise RuntimeError("MASTER_SHEET_ID is not set — see .env.example at the repo root.")
        _gc = get_gspread_client()
        _sh = _gc.open_by_key(MASTER_SHEET_ID)
    return _sh


class OpsLogger:
    def __init__(self):
        self._client  = ""
        self._script  = ""
        self._start_t = None
        self._run_date= ""
        self._run_time= ""

    def start(self, client: str, script: str):
        self._client   = client
        self._script   = script
        self._start_t  = time.time()
        now            = datetime.now()
        self._run_date = now.strftime("%Y-%m-%d")
        self._run_time = now.strftime("%-I:%M %p")
        print(f"  [OpsLog] {client} / {script} started at {self._run_time}")

    def success(self, metric1: str = "", metric2: str = "", metric3: str = "", notes: str = ""):
        self._write("SUCCESS", metric1, metric2, metric3, notes or "")

    def warning(self, notes: str, metric1: str = "", metric2: str = "", metric3: str = ""):
        self._write("WARNING", metric1, metric2, metric3, notes)

    def failure(self, error: str, metric1: str = "", metric2: str = "", metric3: str = ""):
        self._write("FAILED", metric1, metric2, metric3, f"ERROR: {error}")

    def _write(self, status: str, m1: str, m2: str, m3: str, notes: str):
        duration = round(time.time() - self._start_t, 1) if self._start_t else 0
        row = [
            self._run_date,
            self._run_time,
            self._client,
            self._script,
            status,
            duration,
            m1, m2, m3,
            notes,
        ]
        try:
            sh = _connect()
            ws = sh.worksheet("Ops Log")
            ws.append_row(row, value_input_option="USER_ENTERED")
            print(f"  [OpsLog] Logged: {status} ({duration}s)")
        except Exception as e:
            print(f"  [OpsLog] WARNING: Could not write to Ops Log — {e}")


def update_monday_report(week_of: str, client: str, data_pull: str, dashboard: str,
                         flow_audit: str, open_rate: str, click_rate: str,
                         revenue: str, flags: str, status: str):
    """
    Upsert a row in the Monday Report tab for the given client + week.
    Replaces existing row for same client+week if found, otherwise appends.
    """
    try:
        sh   = _connect()
        ws   = sh.worksheet("Monday Report")
        rows = ws.get_all_values()
        # Find existing row for this client + week
        target_row = None
        for i, row in enumerate(rows[1:], start=2):
            if len(row) >= 2 and row[0] == week_of and row[1] == client:
                target_row = i
                break

        new_row = [week_of, client, data_pull, dashboard, flow_audit,
                   open_rate, click_rate, revenue, flags, status]

        if target_row:
            ws.update(f"A{target_row}:J{target_row}", [new_row], value_input_option="USER_ENTERED")
        else:
            ws.append_row(new_row, value_input_option="USER_ENTERED")

        print(f"  [MondayReport] Updated: {client} / {week_of}")
    except Exception as e:
        print(f"  [MondayReport] WARNING: Could not update Monday Report — {e}")


def log_flow_audit(client: str, flow_name: str, flow_id: str,
                   open_rate: str, ctr: str, revenue: str,
                   findings: str, recommendations: str):
    """
    Update or insert the Flow Audit Tracker row for this client+flow.
    Sets Audit Status to 'Awaiting Approval', clears the operator-approved and
    changes-made columns.
    """
    try:
        sh   = _connect()
        ws   = sh.worksheet("Flow Audit Tracker")
        rows = ws.get_all_values()
        today = datetime.now().strftime("%Y-%m-%d")

        # Find existing row
        target_row = None
        for i, row in enumerate(rows[1:], start=2):
            if len(row) >= 2 and row[0].strip() == client and row[1].strip() == flow_name:
                target_row = i
                break

        new_row = [
            client, flow_name, flow_id, today,
            "Awaiting Approval",
            open_rate, ctr, revenue,
            findings, recommendations,
            "",  # Approved? — blank, waiting
            "",  # Changes Made Date — blank
        ]

        if target_row:
            ws.update(f"A{target_row}:L{target_row}", [new_row], value_input_option="USER_ENTERED")
        else:
            ws.append_row(new_row, value_input_option="USER_ENTERED")

        print(f"  [FlowAudit] Logged audit: {client} / {flow_name}")
    except Exception as e:
        print(f"  [FlowAudit] WARNING: Could not update Flow Audit Tracker — {e}")


def get_next_flow_to_audit(active_clients: list) -> dict | None:
    """
    Read the Flow Audit Tracker and return the next flow to audit.
    Logic:
      1. Any flow with blank Last Audited Date gets highest priority.
      2. Among audited flows, pick the one with the oldest Last Audited Date.
      3. Only considers clients in active_clients list.
      4. Skips flows with Audit Status = 'Awaiting Approval' (already pending review).
    Returns dict: {client, flow_name, flow_id} or None if nothing to audit.
    """
    try:
        sh   = _connect()
        ws   = sh.worksheet("Flow Audit Tracker")
        rows = ws.get_all_values()
        if len(rows) <= 1:
            return None

        headers = rows[0]
        candidates = []
        for row in rows[1:]:
            if not any(row):
                continue
            rec = dict(zip(headers, row + [""] * max(0, len(headers) - len(row))))
            client      = rec.get("Client", "").strip()
            flow_name   = rec.get("Flow Name", "").strip()
            flow_id     = rec.get("Flow ID", "").strip()
            last_audited= rec.get("Last Audited Date", "").strip()
            audit_status= rec.get("Audit Status", "").strip()

            if client not in active_clients:
                continue
            if audit_status == "Awaiting Approval":
                continue  # don't re-audit while pending sign-off

            candidates.append({
                "client":       client,
                "flow_name":    flow_name,
                "flow_id":      flow_id,
                "last_audited": last_audited,
            })

        if not candidates:
            return None

        # Prioritize never-audited first, then oldest audit date
        never   = [c for c in candidates if not c["last_audited"]]
        audited = sorted(
            [c for c in candidates if c["last_audited"]],
            key=lambda c: c["last_audited"]
        )

        return (never + audited)[0]

    except Exception as e:
        print(f"  [FlowAudit] Could not read tracker — {e}")
        return None
