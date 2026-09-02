#!/usr/bin/env python3
"""
prebake_session.py — Pre-bake Amelia session context

Reads brand.md + image_library.json + pending briefs for one or all active
clients and writes a compact session_context_{client}.md. Amelia reads this
one file instead of loading 3-4 separate files at the start of every build
session.

Usage:
    python3 prebake_session.py                     # bake all active clients
    python3 prebake_session.py --client example-brand
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
CLIENTS_DIR  = REPO_ROOT / "clients"
BRIEFS_DIR   = REPO_ROOT / "prescott" / "briefs"
OUTPUT_DIR   = REPO_ROOT / "prescott" / "session-context"

# List the client slugs you actively work with — matches folder names under clients/
ACTIVE_CLIENTS = ["example-brand"]


def find_brand_file(client_dir: Path):
    """Locate brand.md regardless of whether it lives at root or in brand/."""
    candidates = [client_dir / "brand.md"]
    brand_dir = client_dir / "brand"
    if brand_dir.exists():
        candidates.extend(sorted(brand_dir.glob("*.md")))
    for path in candidates:
        if path.exists():
            return path
    return None


def summarize_image_library(image_file: Path) -> list[str]:
    """Return compact lines summarising the image library by category."""
    try:
        data = json.loads(image_file.read_text())
    except (json.JSONDecodeError, OSError):
        return [f"[Could not parse {image_file}]\n"]

    lines = []
    if isinstance(data, dict):
        # Structure: { "_meta": {...}, "hero_banners": [...], ... }
        for category, items in data.items():
            if category.startswith("_") or not isinstance(items, list):
                continue
            lines.append(f"**{category}** ({len(items)} images)\n")
            for img in items:
                use_cases = ", ".join(img.get("use_cases", []))
                lines.append(
                    f"  - `{img.get('id', '?')}` [{use_cases}] — {img.get('url', '')}\n"
                )
    elif isinstance(data, list):
        for img in data:
            use_cases = ", ".join(img.get("use_cases", []))
            lines.append(
                f"- `{img.get('id', '?')}` [{use_cases}] — {img.get('url', '')}\n"
            )
    return lines


def summarize_briefs(client: str) -> list[str]:
    """Return compact lines for any pending briefs, most recent first."""
    briefs_dir = BRIEFS_DIR / client
    if not briefs_dir.exists():
        return []

    brief_files = sorted(
        briefs_dir.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if not brief_files:
        return ["No pending briefs found.\n"]

    lines = []
    for bf in brief_files[:5]:  # cap at 5 most recent
        try:
            brief = json.loads(bf.read_text())
        except json.JSONDecodeError:
            lines.append(f"- {bf.name}: [could not parse]\n")
            continue

        c = brief.get("campaign", {})
        design_filled = bool(brief.get("design", {}))
        age_days = (datetime.now().timestamp() - bf.stat().st_mtime) / 86400

        lines.append(f"### {bf.name} ({age_days:.0f}d old)\n")
        lines.append(f"- Name: {c.get('name', 'N/A')}\n")
        lines.append(f"- Send date: {c.get('send_date', 'N/A')}\n")
        lines.append(f"- Type: {c.get('campaign_type', 'N/A')}\n")
        lines.append(f"- Segment: {c.get('segment', 'N/A')}\n")
        lines.append(f"- Offer: {c.get('offer', 'N/A')}\n")
        lines.append(f"- Subject: {c.get('subject_line', 'N/A')}\n")
        lines.append(f"- Design fields filled: {'Yes' if design_filled else 'No — Amelia needs to fill'}\n\n")

    return lines


def bake_client(client: str) -> Path:
    client_dir = CLIENTS_DIR / client
    if not client_dir.exists():
        raise FileNotFoundError(f"Client directory not found: {client_dir}")

    sections: list[str] = []
    sections.append(f"# Session Context — {client}\n")
    sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    sections.append("Read this file instead of brand.md and image_library.json separately.\n")
    sections.append("It is regenerated daily by prebake_session.py — if it feels stale, re-run it.\n\n")
    sections.append("---\n\n")

    # Brand
    brand_file = find_brand_file(client_dir)
    if brand_file:
        sections.append(f"## Brand Guide (from {brand_file.relative_to(REPO_ROOT)})\n\n")
        sections.append(brand_file.read_text().strip())
        sections.append("\n\n---\n\n")
    else:
        sections.append(f"## Brand Guide\n\n[NOT FOUND in {client_dir}]\n\n---\n\n")

    # Image library
    image_file = client_dir / "assets" / "image_library.json"
    if image_file.exists():
        sections.append("## Image Library\n\n")
        sections.extend(summarize_image_library(image_file))
        sections.append("\n---\n\n")
    else:
        sections.append("## Image Library\n\n[No image_library.json found — scrape client CDN directly]\n\n---\n\n")

    # Pending briefs
    sections.append("## Pending Briefs\n\n")
    brief_lines = summarize_briefs(client)
    if brief_lines:
        sections.extend(brief_lines)
    else:
        sections.append("No briefs directory found.\n")
    sections.append("\n---\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"session_context_{client}.md"
    output_file.write_text("".join(sections))
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-bake Amelia session context files")
    parser.add_argument("--client", help="Client slug (e.g. example-brand). Omit to bake all active clients.")
    args = parser.parse_args()

    clients = [args.client] if args.client else ACTIVE_CLIENTS

    for client in clients:
        try:
            output = bake_client(client)
            size_kb = output.stat().st_size / 1024
            print(f"[OK]    {client}: {output.name} ({size_kb:.1f} KB)")
        except FileNotFoundError as e:
            print(f"[SKIP]  {client}: {e}")
        except Exception as e:
            print(f"[ERROR] {client}: {e}")


if __name__ == "__main__":
    main()
