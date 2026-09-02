#!/usr/bin/env python3
"""
amelia_deploy.py — Amelia's email deploy pipeline.

Runs after an HTML email is built. Three steps, fully atomic:
  1. Screenshot via Playwright (650px viewport, full-page)
  2. Create Asana task + attach screenshot (single atomic operation — no curl, no splits)
  3. Update content calendar row Status → "Built"

Usage:
    python3 amelia_deploy.py \\
        --client example-brand \\
        --html /absolute/path/to/Email_Name.html \\
        --subject "Subject line here" \\
        --preheader "Preheader text here" \\
        --segment "Engaged 60 Days" \\
        --send-date "May 1, 2026" \\
        --campaign-type "Educational" \\
        --offer "None"
"""

import sys
import os
import argparse
import socket
import subprocess
import time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

from brand_config import get_client_row, get_dedicated_sheet_id
from config import CLIENTS_BASE_PATH, ASANA_DEFAULT_ASSIGNEE

# ── Legacy client config ──────────────────────────────────────────────────────
# Fallback only, for clients onboarded before Asana section ID and calendar
# reference moved into their config sheet (see resolve_deploy_config below).
# Prefer giving the brand's Clients tab row an "Asana Section ID (To Do)"
# column instead. One example entry is provided below — replace it with your
# own brand(s), or delete it once your sheet has that column.

CLIENT_CONFIG = {
    "example-brand": {
        "env":            str(CLIENTS_BASE_PATH / "example-brand" / ".env"),
        "calendar_id":    "TBD",  # Google Sheet ID of this client's content calendar
        "asana_section":  "TBD",  # Asana section GID for the "To Do" / review column
        "calendar_subject_col": 3,   # 0-indexed column with the campaign subject
        "calendar_status_col":  7,   # 0-indexed column with the Status field
    },
}


def resolve_deploy_config(client_slug: str) -> dict:
    """
    Resolve Asana section ID and calendar reference for a client.
    Dedicated single-brand sheet first (an "Asana Section ID (To Do)" column plus
    its own "Content Calendar" tab, fixed columns), legacy CLIENT_CONFIG dict as
    fallback for clients onboarded before this existed.

    ASANA_ACCESS_TOKEN / ASANA_PROJECT_ID always come from clients/{slug}/.env —
    never hardcoded here.
    """
    env_path = str(CLIENTS_BASE_PATH / client_slug / ".env")

    try:
        row = get_client_row(client_slug)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if row and row.get("Asana Section ID (To Do)", "").strip():
        return {
            "env":                  env_path,
            "asana_section":        row["Asana Section ID (To Do)"].strip(),
            "calendar_id":          get_dedicated_sheet_id(client_slug),
            "calendar_tab":         "Content Calendar",
            "calendar_subject_col": 2,   # fixed template column: Subject Line
            "calendar_status_col":  5,   # fixed template column: Status
        }
    elif client_slug in CLIENT_CONFIG:
        legacy = CLIENT_CONFIG[client_slug]
        return {
            "env":                  legacy["env"],
            "asana_section":        legacy["asana_section"],
            "calendar_id":          legacy["calendar_id"],
            "calendar_tab":         None,   # legacy calendars use the first sheet tab
            "calendar_subject_col": legacy["calendar_subject_col"],
            "calendar_status_col":  legacy["calendar_status_col"],
        }
    else:
        print(f"ERROR: No deploy config found for '{client_slug}'. Add an 'Asana Section "
              f"ID (To Do)' column to its config sheet, or add a legacy entry to "
              f"CLIENT_CONFIG in amelia_deploy.py.")
        sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def find_free_port(start=8892):
    port = start
    while port < 9000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free port found in range 8892-8999")


# ── Step 0: Image URL validation ─────────────────────────────────────────────

def validate_images(html_path):
    """Extract all image URLs from the HTML and verify none return 404.
    Aborts deploy if any image is broken — prevents screenshot with broken images."""
    import re
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    # Match src="..." and url('...') and url("...")
    urls = set()
    urls.update(re.findall(r'src=["\']+(https?://[^"\']+\.(jpg|jpeg|png|webp|gif))["\']', html, re.I))
    urls.update(re.findall(r"url\(['\"]?(https?://[^'\")\s]+\.(jpg|jpeg|png|webp|gif))['\"]?\)", html, re.I))
    # Flatten tuples from groups
    flat = set()
    for item in urls:
        flat.add(item[0] if isinstance(item, tuple) else item)

    if not flat:
        print("  [validate] No external image URLs found.")
        return True

    print(f"  [validate] Checking {len(flat)} image URL(s)...")
    broken = []
    for url in sorted(flat):
        try:
            r = requests.head(url, timeout=8, allow_redirects=True,
                              headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 404:
                broken.append(url)
                print(f"    404  {url}")
            else:
                print(f"    {r.status_code}  {url}")
        except Exception as e:
            broken.append(url)
            print(f"    ERR  {url}  ({e})")

    if broken:
        print(f"\n  DEPLOY ABORTED — {len(broken)} broken image(s) found above.")
        print("  Fix the URLs in the brief JSON and re-render before deploying.")
        return False

    print(f"  [validate] All images OK.")
    return True


# ── Step 1: Screenshot ────────────────────────────────────────────────────────

def take_screenshot(html_path):
    html_dir  = os.path.dirname(html_path)
    html_file = os.path.basename(html_path)
    stem      = os.path.splitext(html_file)[0]
    out_path  = os.path.join(html_dir, f"{stem}_screenshot.png")

    port = find_free_port()
    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(port), "--directory", html_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.0)

    try:
        import asyncio
        from playwright.async_api import async_playwright

        async def _shoot():
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                page    = await browser.new_page(viewport={"width": 650, "height": 900})
                await page.goto(f"http://127.0.0.1:{port}/{html_file}")
                await page.wait_for_timeout(1500)
                await page.screenshot(path=out_path, full_page=True)
                await browser.close()

        asyncio.run(_shoot())
        print(f"  [screenshot] Saved → {out_path}")
        return out_path
    finally:
        server.terminate()


# ── Step 2: Asana — atomic create + attach ────────────────────────────────────

REVIEW_CHECKLIST = """
REVIEW CHECKLIST
[ ] Subject line and preheader accurate
[ ] Brand colours correct
[ ] CTA button links to correct URL
[ ] Mobile layout verified
[ ] Unsubscribe and preferences links present
[ ] No grammar or copy errors
[ ] Segment confirmed before send"""


def asana_create_and_attach(token, project_id, section_id, subject, preheader,
                             send_date, campaign_type, segment, offer, screenshot_path):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }

    task_name  = f"[EMAIL REVIEW] {subject} | {send_date} {campaign_type}"
    task_notes = (
        f"Subject Line: {subject}\n"
        f"Preheader: {preheader}\n"
        f"Send Date: {send_date}\n"
        f"Campaign Type: {campaign_type}\n"
        f"Segment: {segment}\n"
        f"Offer / Code: {offer}\n"
        f"Recommended Send Date: {send_date}\n"
        f"{REVIEW_CHECKLIST}"
    )

    payload = {
        "data": {
            "name":       task_name,
            "notes":      task_notes,
            "projects":   [project_id],
            "assignee":   ASANA_DEFAULT_ASSIGNEE or None,
            "memberships": [{"project": project_id, "section": section_id}] if section_id else [],
        }
    }

    r = requests.post("https://app.asana.com/api/1.0/tasks", headers=headers, json=payload)
    r.raise_for_status()
    task_gid = r.json()["data"]["gid"]
    print(f"  [asana] Task created — GID {task_gid}")

    # Attach screenshot
    mime_type = "image/png"
    with open(screenshot_path, "rb") as f:
        attach_r = requests.post(
            f"https://app.asana.com/api/1.0/tasks/{task_gid}/attachments",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (os.path.basename(screenshot_path), f, mime_type)},
        )
    attach_r.raise_for_status()
    print(f"  [asana] Screenshot attached.")
    return task_gid


# ── Step 3: Content calendar update ──────────────────────────────────────────

def update_calendar(calendar_id, subject, subject_col=3, status_col=7, calendar_tab=None):
    if not calendar_id or calendar_id in ("TBD", "SKIP"):
        print(f"  [calendar] Skipped — calendar not configured for this client. Update manually.")
        return

    from google_auth import get_gspread_client

    gc    = get_gspread_client()
    sh    = gc.open_by_key(calendar_id)
    ws    = sh.worksheet(calendar_tab) if calendar_tab else sh.worksheets()[0]
    data  = ws.get_all_values()

    status_col_letter = chr(65 + status_col)   # e.g. 7 → 'H'

    matched_row = None
    for i, row in enumerate(data[1:], start=2):   # skip header, rows are 1-indexed
        if len(row) > subject_col and row[subject_col].strip().lower() == subject.strip().lower():
            matched_row = i
            break

    if matched_row:
        ws.update(values=[["Built"]], range_name=f"{status_col_letter}{matched_row}")
        print(f"  [calendar] Row {matched_row} → Status set to 'Built'.")
    else:
        print(f"  [calendar] WARNING — no row found matching subject: '{subject}'")
        print(f"             Update the Status column manually in the content calendar.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Amelia deploy pipeline")
    parser.add_argument("--client",        required=True, help="Client slug, e.g. example-brand")
    parser.add_argument("--html",          required=True, help="Absolute path to the HTML email file")
    parser.add_argument("--subject",       required=True)
    parser.add_argument("--preheader",     required=True)
    parser.add_argument("--segment",       required=True)
    parser.add_argument("--send-date",     required=True)
    parser.add_argument("--campaign-type", required=True)
    parser.add_argument("--offer",         default="None")
    args = parser.parse_args()

    client_slug = args.client.lower()
    config = resolve_deploy_config(client_slug)
    env    = load_env(config["env"])

    asana_token      = env.get("ASANA_ACCESS_TOKEN")
    asana_project_id = env.get("ASANA_PROJECT_ID")
    asana_section    = config["asana_section"]
    calendar_id      = config["calendar_id"]

    if not asana_token or asana_project_id == "TBD":
        print(f"ERROR: ASANA credentials not fully configured for {client_slug}.")
        sys.exit(1)

    html_path = os.path.abspath(args.html)
    if not os.path.exists(html_path):
        print(f"ERROR: HTML file not found: {html_path}")
        sys.exit(1)

    print(f"\nAmelia Deploy — {client_slug.upper()}")
    print(f"  Email : {os.path.basename(html_path)}")
    print(f"  Subject: {args.subject}")
    print()

    # Step 0 — validate all image URLs before screenshotting
    print("Step 0/3 — Image URL validation")
    if not validate_images(html_path):
        sys.exit(1)
    print()

    # Step 1
    print("Step 1/3 — Screenshot")
    screenshot_path = take_screenshot(html_path)

    # Step 2
    print("Step 2/3 — Asana task (create + attach)")
    task_gid = asana_create_and_attach(
        token          = asana_token,
        project_id     = asana_project_id,
        section_id     = asana_section,
        subject        = args.subject,
        preheader      = args.preheader,
        send_date      = args.send_date,
        campaign_type  = args.campaign_type,
        segment        = args.segment,
        offer          = args.offer,
        screenshot_path= screenshot_path,
    )

    # Step 3
    print("Step 3/3 — Content calendar update")
    update_calendar(
        calendar_id,
        args.subject,
        subject_col=config.get("calendar_subject_col", 3),
        status_col=config.get("calendar_status_col", 7),
        calendar_tab=config.get("calendar_tab"),
    )

    print(f"\nDone. Asana task: https://app.asana.com/0/{asana_project_id}/{task_gid}")


if __name__ == "__main__":
    main()
