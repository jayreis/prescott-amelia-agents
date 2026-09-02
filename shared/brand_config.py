#!/usr/bin/env python3
"""
brand_config.py — Unified per-brand config resolver.

Every brand's full config (ESP API key, brand colors, Asana IDs, calendar
reference) is resolved the same way:

  1. If clients/{slug}/.env has BRAND_CONFIG_SHEET_ID, read the "Clients" tab
     of that brand's own dedicated Google Sheet (one data row).
  2. Otherwise, fall back to the shared Master Sheet's "Clients" tab, matched
     by name. See README.md for the Master Sheet template.

Onboarding a new brand through its own dedicated sheet never requires a code
change — adding a brand to a shared multi-brand roster just means a new
Master Sheet row.

Usage:
    from brand_config import get_client_row
    row = get_client_row("example-brand")
    row["ESP Private API Key"]
"""

import logging
from typing import Optional

from google_auth import get_gspread_client
from config import MASTER_SHEET_ID, CLIENTS_BASE_PATH

# Folder slug overrides for clients whose folder name differs from their sheet
# name. Add your own here if a client's display name doesn't map cleanly to
# "lowercase-with-hyphens".
_FOLDER_SLUGS: dict[str, str] = {}

# Session-scoped row cache — avoids re-reading a sheet on every call
_row_cache: dict[str, dict] = {}


def _client_slug(client_name: str) -> str:
    lower = client_name.strip().lower()
    return _FOLDER_SLUGS.get(lower, lower.replace(" ", "-"))


def _open_clients_tab(sheet_id: str):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id).worksheet("Clients")


def get_dedicated_sheet_id(client_name: str) -> Optional[str]:
    """Read clients/{slug}/.env's BRAND_CONFIG_SHEET_ID, if this brand has one."""
    slug = _client_slug(client_name)
    env_path = CLIENTS_BASE_PATH / slug / ".env"
    if not env_path.exists():
        return None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("BRAND_CONFIG_SHEET_ID="):
                val = line.split("=", 1)[1].strip()
                return val if val and not val.startswith("<") else None
    return None


def _row_from_dedicated_sheet(slug: str) -> Optional[dict]:
    """Single-brand path — clients/{slug}/.env points at its own Sheet."""
    sheet_id = get_dedicated_sheet_id(slug)
    if not sheet_id:
        return None

    try:
        ws = _open_clients_tab(sheet_id)
        rows = ws.get_all_values()
        if len(rows) < 2:
            return None
        headers = rows[0]
        # Single-brand sheet — exactly one data row
        return dict(zip(headers, rows[1] + [""] * max(0, len(headers) - len(rows[1]))))
    except Exception as e:
        logging.warning(f"brand_config: dedicated sheet lookup failed for '{slug}' — {e}")
        return None


def _row_from_master_sheet(client_name: str) -> Optional[dict]:
    """Multi-brand path — match by name in the shared Master Sheet's Clients tab."""
    if not MASTER_SHEET_ID:
        return None
    try:
        ws = _open_clients_tab(MASTER_SHEET_ID)
        rows = ws.get_all_values()
        if not rows:
            return None
        headers = rows[0]
        name_col = headers.index("Client Name") if "Client Name" in headers else 0
        for row in rows[1:]:
            if len(row) > name_col and row[name_col].strip().lower() == client_name.strip().lower():
                return dict(zip(headers, row + [""] * max(0, len(headers) - len(row))))
    except Exception as e:
        logging.warning(f"brand_config: master sheet lookup failed for '{client_name}' — {e}")
    return None


def get_client_row(client_name: str) -> Optional[dict]:
    """
    Resolve a brand's full config row as a dict keyed by column header.
    Dedicated single-brand sheet takes priority over the Master Sheet.
    Returns None if neither source has a matching, active row.
    """
    if client_name in _row_cache:
        return _row_cache[client_name]

    slug = _client_slug(client_name)
    row = _row_from_dedicated_sheet(slug) or _row_from_master_sheet(client_name)

    if row and row.get("Active", "").strip().upper() != "TRUE":
        raise ValueError(
            f"Client '{client_name}' is inactive (Active = FALSE). "
            f"Set Active to TRUE in its config sheet to enable connections."
        )

    if row:
        _row_cache[client_name] = row
    return row
