# Brand Guide 1-Pager — Standard Format
**Prescott's Framework — applies to all new email marketing AI agents**

When you ask any email marketing agent to create a brand guide or brand guide 1-pager for a client, it must follow this exact layout and include these sections.

---

## Required Sections (in this order)

### Header
- Client logo (top-left)
- Brand/client name (large, bold)
- "Brand Guidelines — Internal Reference" label
- Website URL (top-right)

### Tagline Strip
- Primary tagline
- Secondary tagline or brand mission statement (if available)

---

### Two-Column Layout — Row 1
| Left Column | Right Column |
|---|---|
| **Brand Colors** — 3 swatches with hex code, name, and usage note | **Typography** — primary, secondary, and tertiary fonts with type classification and use case |

---

### Two-Column Layout — Row 2
| Left Column | Right Column |
|---|---|
| **Tone of Voice** — 4–5 bullet points describing how the brand communicates | **3 Brand Voice Words** — single words rendered as styled label chips |

---

### Two-Column Layout — Row 3
| Left Column | Right Column |
|---|---|
| **Brand Aesthetic** — 5 short phrases (2–3 words each) with a one-line description | **When You Think [Brand], Think** — 4–5 single words (bullet list) + **Don't Do** box — 4 phrases never to use with reason why (red-tinted background box) |

---

### Two-Column Layout — Row 4
| Left Column | Right Column |
|---|---|
| **Business Overview** — key:value pairs: Founded, Founder, Technology, Products, Manufacturing, Guarantee, Shipping, Notable Endorsement | **Target Customer** — 3–4 sentence paragraph describing the primary customer persona |

### Footer
- Client name + "Brand Guidelines" + "Internal Reference" + website URL + "Prepared by [Agent]"

---

## Format & Output
- **Format:** PDF (single page, US Letter 8.5×11)
- **Generator:** Python script using `reportlab` saved alongside the PDF in the client's `brand/` folder
- **File path:** `clients/[client-slug]/brand/[ClientName]_Brand_Guide.pdf`
- **Logo:** Download from client website, save as `brand/[client]_logo.png`

## Visual Style Defaults
- Dark charcoal header bar with brand color accent stripe underneath
- Tagline in a light gray strip below header
- Red left-side accent bars on section titles (3pt wide)
- Color swatches: rounded rectangle with thin border
- "Don't Do" section in a red-tinted background box with ✕ markers
- Footer: dark charcoal bar with brand color accent stripe on top

## How to Build It
1. Use Playwright to screenshot the client website and extract logo URL
2. Use `browser_evaluate` to extract computed CSS font families
3. Use `WebFetch` on homepage + About page to extract brand voice, messaging, and business details
4. Download logo via `curl`
5. Run `pip3 install reportlab` if not installed
6. Generate PDF using the fixed-position layout (not dynamic y-tracking — causes overlap)
7. Save generator script + PDF + logo all into `brand/` folder
8. Save brand reference markdown file (`[ClientName]_Brand_Reference.md`) in `brand/` folder for agent reference
