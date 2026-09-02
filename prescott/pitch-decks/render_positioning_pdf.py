#!/usr/bin/env python3
"""
render_positioning_pdf.py
Converts positioning.md to a styled PDF.
"""

import asyncio
from pathlib import Path

import markdown as md_lib
from playwright.async_api import async_playwright

HERE     = Path(__file__).parent
MD_PATH  = HERE / "positioning.md"
PDF_PATH = HERE / "positioning.pdf"
HTML_TMP = HERE / "_render_tmp.html"

CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
        font-size: 10.5pt;
        line-height: 1.7;
        color: #1a1a1a;
        background: #ffffff;
    }

    .page-wrap {
        max-width: 740px;
        margin: 0 auto;
        padding: 52px 60px 68px;
    }

    /* Cover */
    .cover {
        border-bottom: 3px solid #1a1a1a;
        padding-bottom: 26px;
        margin-bottom: 34px;
    }
    .cover h1 {
        font-size: 24pt;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 6px;
        color: #0d0d0d;
    }
    .cover h2 {
        font-size: 13pt;
        font-weight: 400;
        color: #444;
        border: none;
        margin: 0;
        padding: 0;
    }

    /* Intro paragraph (before first h2) */
    .intro {
        font-size: 11pt;
        color: #333;
        margin-bottom: 28px;
        line-height: 1.75;
    }

    /* Section headings */
    h2 {
        font-size: 13.5pt;
        font-weight: 700;
        color: #0d0d0d;
        margin: 34px 0 10px;
        padding-bottom: 5px;
        border-bottom: 1.5px solid #ddd;
        page-break-after: avoid;
    }
    h3 {
        font-size: 11pt;
        font-weight: 700;
        color: #1a1a1a;
        margin: 20px 0 6px;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 13px;
    }

    ul, ol {
        margin: 6px 0 14px 22px;
    }
    li {
        margin-bottom: 5px;
    }

    strong { font-weight: 700; }
    em { font-style: italic; color: #333; }

    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 26px 0;
    }

    /* Pull-quote style for the key bold principle lines */
    .pull {
        border-left: 4px solid #1a1a1a;
        padding: 10px 16px;
        margin: 16px 0;
        background: #f7f7f7;
        font-style: italic;
        color: #222;
    }

    /* Footer meta block */
    .meta {
        margin-top: 32px;
        padding-top: 14px;
        border-top: 1px solid #ddd;
        font-size: 9pt;
        color: #666;
        line-height: 1.8;
    }

    @media print {
        body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        h2, h3 { page-break-after: avoid; }
    }

    @page {
        size: Letter;
        margin: 0.85in 0.9in;
    }
"""


def build_html(md_text):
    lines = md_text.split('\n')

    # Extract H1 and subtitle (H2 immediately after H1)
    title = ""
    subtitle = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            body_start = i + 1
        elif line.startswith('## ') and title and not subtitle:
            subtitle = line[3:].strip()
            body_start = i + 1
            break

    body_md = '\n'.join(lines[body_start:])

    converter = md_lib.Markdown(extensions=['tables', 'fenced_code'])
    body_html = converter.convert(body_md)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<div class="page-wrap">
  <div class="cover">
    <h1>{title}</h1>
    <h2>{subtitle}</h2>
  </div>
  {body_html}
</div>
</body>
</html>"""
    return html


async def render_pdf():
    md_text = MD_PATH.read_text(encoding='utf-8')
    html = build_html(md_text)
    HTML_TMP.write_text(html, encoding='utf-8')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{HTML_TMP}")
        await page.wait_for_timeout(1200)
        await page.pdf(
            path=str(PDF_PATH),
            format="Letter",
            margin={"top": "0.85in", "bottom": "0.85in", "left": "0.9in", "right": "0.9in"},
            print_background=True,
        )
        await browser.close()

    HTML_TMP.unlink()
    print(f"PDF saved → {PDF_PATH}")


if __name__ == "__main__":
    asyncio.run(render_pdf())
