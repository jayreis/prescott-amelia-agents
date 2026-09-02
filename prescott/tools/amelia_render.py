#!/usr/bin/env python3
"""
amelia_render.py — Renders a JSON brief into a complete HTML email.

Amelia fills in a JSON brief -> this script handles all HTML generation.
No LLM needed for layout, CSS, or structure.

Usage:
    python3 amelia_render.py --brief /path/to/brief.json

Output:
    HTML file saved to the client's campaigns/ folder.
    Prints the amelia_deploy.py command to run next.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))

from jinja2 import Environment, FileSystemLoader
from brand_config import get_client_row
from config import CLIENTS_BASE_PATH


def to_ns(obj):
    """Recursively convert dicts to SimpleNamespace so Jinja2 attribute access works
    without conflicting with Python dict methods like .items()."""
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: to_ns(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [to_ns(i) for i in obj]
    return obj

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
CAMPAIGNS_BASE = CLIENTS_BASE_PATH
TOOLS_DIR = Path(__file__).parent


# ── Legacy client brand config ───────────────────────────────────────────────
# Fallback only, for clients onboarded before brand colors moved into their
# config sheet (see brand_config.get_client_row). Prefer giving the brand's
# Clients tab row Brand Accent/Dark/Light Text Color columns instead — this
# dict only needs an entry if you'd rather hardcode a brand's colors here.
# One example entry is provided below; replace it with your own brand(s) or
# delete it once your sheet has the Brand Accent/Dark/Light Text columns.

CLIENT_BRAND = {
    "example-brand": {
        "accent": "#FF6900",     # CTAs, badges, icon fills
        "dark":   "#222C37",     # structure, section backgrounds
        "light_text": "#FFFFFF",
    },
}


# ── Icon library — CSS/HTML only, no SVG ─────────────────────────────────────
# Klaviyo and many email clients strip inline SVG. All icons are rendered as
# accent-coloured table cells with unicode characters — no SVG, no path data.

def _icon(char, accent):
    """Return a 32×32 accent-coloured circle containing a unicode character."""
    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        f'width="32" style="width:32px; border-collapse:collapse;">'
        f'<tr><td align="center" width="32" height="32" '
        f'style="width:32px; height:32px; background-color:{accent}; '
        f'color:#ffffff; font-family:Arial,Helvetica,sans-serif; '
        f'font-size:16px; font-weight:bold; line-height:32px; '
        f'text-align:center; border-radius:4px;">{char}</td></tr></table>'
    )

def make_icons(accent):
    return {
        "shield":        _icon("&#10003;", accent),   # ✓ checkmark
        "eye":           _icon("&#9679;",  accent),   # ● circle
        "check":         _icon("&#10003;", accent),   # ✓ checkmark
        "star":          _icon("&#9733;",  accent),   # ★ star
        "truck":         _icon("&#8594;",  accent),   # → arrow right
        "tool":          _icon("&#9670;",  accent),   # ◆ diamond
        "certification": _icon("&#10003;", accent),   # ✓ checkmark
        "clock":         _icon("&#9632;",  accent),   # ■ square
        "chart":         _icon("&#8593;",  accent),   # ↑ arrow up
        "lab":           _icon("&#9670;",  accent),   # ◆ diamond
    }


# ── Render ────────────────────────────────────────────────────────────────────

def render(brief_path):
    with open(brief_path) as f:
        brief = json.load(f)

    client_slug = brief["campaign"]["client"]

    try:
        row = get_client_row(client_slug)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if row and row.get("Brand Accent Color", "").strip():
        brand_config = {
            "accent":     row.get("Brand Accent Color", "").strip(),
            "dark":       row.get("Brand Dark Color", "").strip(),
            "light_text": row.get("Brand Light Text Color", "").strip() or "#FFFFFF",
        }
    elif client_slug in CLIENT_BRAND:
        brand_config = CLIENT_BRAND[client_slug]  # legacy fallback
    else:
        print(f"ERROR: No brand config found for '{client_slug}'. Add Brand Accent/Dark/"
              f"Light Text Color columns to its config sheet (see brand_config.py), or "
              f"add an entry to CLIENT_BRAND in amelia_render.py.")
        sys.exit(1)

    icons = make_icons(brand_config["accent"])

    design = brief["design"]

    def _included(section_data):
        """Return False if the section is explicitly opted out with include:false."""
        if isinstance(section_data, dict):
            return section_data.get("include", True) is not False
        return True

    # Tiles may be a list (normal) or a dict {"include": false} — always pass a list
    raw_tiles = design.get("tiles", [])
    tiles_list = raw_tiles if isinstance(raw_tiles, list) else []

    # Build template context — convert all dicts/lists to SimpleNamespace
    # so Jinja2 attribute access (e.g. features.items) works without
    # conflicting with Python dict built-in methods
    context = {
        "campaign":  to_ns(brief["campaign"]),
        "brand":     to_ns(brand_config),
        "hero":      to_ns(design["hero"]),
        "intro":     to_ns(design["intro"]),
        "cta_block": to_ns(design["cta_block"]),
        "tiles":     to_ns(tiles_list),
        "icons":     icons,
    }

    # bottom_hero is optional — only include if not disabled
    bottom_hero_data = design.get("bottom_hero", {})
    if _included(bottom_hero_data) and bottom_hero_data.get("cta_url"):
        context["bottom_hero"] = to_ns(bottom_hero_data)

    # Optional sections — skip any with include:false
    for section in ("features", "stats", "split", "lifestyle"):
        if section in design and _included(design[section]):
            context[section] = to_ns(design[section])

    # Render template
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("email_body.html.j2")
    html = template.render(**context)

    # Output path
    campaign_name = brief["campaign"]["name"]
    out_dir = CAMPAIGNS_BASE / client_slug / "campaigns"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"Email_{campaign_name}.html"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nRendered -> {out_path}")

    # Print the deploy command (raw dict — brief not converted here)
    c = brief["campaign"]
    offer = c.get("offer", "None") or "None"
    print("\n-- Next step: run amelia_deploy.py --")
    print(f"""python3 {TOOLS_DIR}/amelia_deploy.py \\
    --client {client_slug} \\
    --html "{out_path}" \\
    --subject "{c['subject_line']}" \\
    --preheader "{c['preheader']}" \\
    --segment "{c['segment']}" \\
    --send-date "{c['send_date']}" \\
    --campaign-type "{c['campaign_type']}" \\
    --offer "{offer}" """)
    print()

    return str(out_path)


def main():
    parser = argparse.ArgumentParser(description="Amelia render — JSON brief → HTML email")
    parser.add_argument("--brief", required=True, help="Path to JSON brief file")
    args = parser.parse_args()

    if not os.path.exists(args.brief):
        print(f"ERROR: Brief not found: {args.brief}")
        sys.exit(1)

    render(args.brief)


if __name__ == "__main__":
    main()
