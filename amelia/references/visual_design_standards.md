# Visual Design Standards

Load this file before filling any design fields or selecting images.

---

## Visual-First Design Mandate

Every email must be conceived visually before a single word of copy is placed. Layout structure, section rhythm, and visual hierarchy come first — copy fills the space the design defines, not the other way around.

**Before building any email, ask:**
> *"If I removed all the copy from this email, would it still communicate something visually?"*
> If the answer is no, the layout is not finished.

**Image-to-text ratio:** Target minimum 60% visual, 40% copy. No section may be majority raw text on a plain white or solid-colour background without a visual counterpart.

**Section visual anchors:** Every section must carry a dominant visual element — a photograph, colour block, texture, graphic treatment, or product cut-out.

**Text placement — in order of preference:**
1. Overlaid on imagery with a dark overlay for contrast
2. Set within a colour-blocked container matching the brand palette
3. Placed on a textured background (subtle grain, paper, or material texture — must be brand-appropriate and quiet)
4. Constrained to a tight callout or badge — never loose paragraphs floating on white

**Product photography treatment:** Images do not always have to be full-bleed. Product shots may be cut out and float within the section. Overlapping section edges is permitted when it reads well.

**Connected flow:** The email reads as a single designed piece, not a stack of boxes.
- A consistent colour palette threads through every section
- Section transitions bleed or bridge — no jarring hard stops
- The reader's eye travels naturally from hero to closing CTA without visual breaks

---

## Typography

- **Font stack:** `Arial, Helvetica, sans-serif` — always. Brand fonts are not email-safe.
- **Hierarchy:** Headline → subheadline → body → CTA. Never flatten this.
- **Short copy wins:** Intro paragraph 2 sentences max. Feature card body 1–2 sentences.

---

## Colour Usage

- Colours are defined in `amelia_render.py` per client — never hardcode hex values
- The hierarchy from brand.md must never be reversed:
  - Accent → CTAs, badges, highlights, icon fills
  - Dark → structure, section backgrounds
- Never use accent colour for large background areas

---

## Contrast — Non-Negotiable

Every text and background pairing must have sufficient contrast.
- White text on dark backgrounds: always safe
- Dark text on white or light backgrounds: always safe
- Never place light text on a light background, or dark text on a dark background
- Hero and lifestyle sections with photo backgrounds: always apply a dark overlay (`rgba(0,0,0,0.6)` minimum). Never render text directly over an unmasked photograph.
- When in doubt, increase the overlay opacity. A slightly darker image is always better than unreadable text.
- All pairings must pass WCAG AA (4.5:1 for normal text, 3:1 for large text).

---

## Photography — Required in Every Email

Every email must include real photography. An email with no imagery is not acceptable.
- Lifestyle shots are the preference — real people, real environments, in context
- Product shots or close-up detail/micro shots are also valid
- The hero section always has a background image. The bottom hero always has a background image.
- If the brief does not specify images, pull from `image_library.json` — match `use_cases` to the campaign type
- If `image_library.json` has no suitable image, scrape the client CDN and verify the URL returns 200 before using

**Image sourcing priority:**
1. Client CDN — always first. Check `image_library.json`.
2. CSS/SVG — texture via CSS gradients, icons via the built-in SVG icon library in `amelia_render.py`
3. Local AI — only if client photography genuinely cannot serve the need. No paid AI image APIs.

---

## Layout Variety — Amelia's Design Choices

Not every email uses every section. Use section flags intentionally:
- `features.style`: `"icon_cards"` (educational) or `"offer_badge"` (promotional)
- `stats.style`: `"numbers"` or `"testimonials"`
- `split.style`: `"checklist"` or `"benefits"`
- `stats.include`, `split.include`, `lifestyle.include`: set `false` to create shorter, simpler emails
- `hero.eyebrow`: optional campaign label above the headline — use sparingly
- `hero.overlay_opacity`: 0.65–0.85 depending on the photo's darkness

A product highlight email may skip stats. A re-engagement email may skip the split section. Variety is intentional.
