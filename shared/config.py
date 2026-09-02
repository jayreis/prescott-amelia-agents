"""
config.py — Repo-wide, non-client-specific configuration.

Everything here comes from environment variables (see .env.example at the repo
root). Nothing here is a real value — you must fill in your own.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Master Google Sheet — the "Clients" tab (roster + per-client ESP keys/config),
# plus the "Ops Log" / "Monday Report" / "Flow Audit Tracker" tabs used by
# ops_logger.py. See README.md for the sheet template and required tab layout.
MASTER_SHEET_ID = os.environ.get("MASTER_SHEET_ID", "")

# Google OAuth client secrets (Desktop App type) — see README.md Google Sheets
# setup section for how to create this in Google Cloud Console.
GOOGLE_CLIENT_SECRETS = Path(
    os.environ.get("GOOGLE_CLIENT_SECRETS", str(REPO_ROOT / "config" / "credentials.json"))
)
GOOGLE_TOKEN_PATH = Path(
    os.environ.get("GOOGLE_TOKEN_PATH", str(Path.home() / ".config" / "prescott-amelia" / "token.json"))
)

# Asana assignee GID — the Asana user review tasks get assigned to. Find yours
# at app.asana.com/api/1.0/users/me (or via the Asana API explorer).
ASANA_DEFAULT_ASSIGNEE = os.environ.get("ASANA_DEFAULT_ASSIGNEE", "")

CLIENTS_BASE_PATH = REPO_ROOT / "clients"
