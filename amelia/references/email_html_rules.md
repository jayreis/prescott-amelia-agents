# Email HTML Rules & Technical Constraints

Load this file before writing any HTML for an email.

---

## Non-Negotiable HTML Rules

1. **No `<!DOCTYPE>`, `<html>`, `<head>`, `<title>`, or `<meta>` tags.** Email clients strip the head section entirely. The template starts directly with a `<style>` block (media queries only) followed by the outer `<table>`.
2. **All CSS must be inline via `style=""` attributes.** No exceptions. The only CSS allowed in a `<style>` block is `@media` queries — they physically cannot be inlined.
3. **Emails must be short.** Maximum structure: Hero + 1-2 content sections + closing CTA. If a section does not earn its place, set `include: false`.
4. **Value proposition + CTA above the fold, always.** The first ~600px on mobile must contain: logo, headline, subhead, and primary CTA button. The subscriber must be able to understand the offer AND convert without scrolling.
5. **One email, one message, one action.** Two messages means two emails.
6. **One CTA destination per email — but repeat the button 2–3 times.** Button label can evolve down the page but all resolve to the same URL family.

---

## Technical Constraints

**Width:** 600px content area. Full-bleed background colors and images are allowed, but all content stays within a 600px centred wrapper.

**Layout:** Single column is the default. The only multi-column exceptions:
- **2×2 product grids** — must stack to single column on mobile
- **2-column comparison tables** — must also stack predictably
No other multi-column layouts are permitted.

**Mobile-first:** Assume 60–70% of opens are on mobile. Design at 600px wide; verify reads cleanly at 375px.

**Font size minimums:**
- Body copy: 14px floor, 16px preferred
- Legal / footer copy: 11px floor

**CTAs — tap height and Outlook compatibility:**
- Minimum 44px tap height on all CTA buttons (padding ensures this)
- For deployed HTML: bulletproof buttons using `<table>` wrapping `<a>` with VML conditional comments for Outlook
- In design mockups: solid rectangles with clear padding are acceptable

**Media queries:** Include `@media` classes for mobile stacking but treat the `<style>` block as best-effort — the email must look correct if the block is stripped entirely. Never rely on a media query for critical readability.

**Equal-height side-by-side cards — non-negotiable:**

1. **Background color on the outer `<td>`, never on an inner `<div>` or inner `<td>`.** The outer `<td>` stretches to the tallest column automatically.
2. **Fixed image heights on all images in the same row.** Same `height:Npx; object-fit:cover;` on every product image in a row. Never `height:auto` when images sit side by side.

For image cells in a horizontal split where text determines height: use `background-image` on the `<td>` rather than an `<img>` tag.

```css
<td background="url" style="background-image:url('...');background-size:cover;background-position:center top;background-color:#fallback;">
</td>
```

**`box-sizing:border-box !important` on every `display:block` cell — non-negotiable.**
Every cell that receives `display:block !important` in a media query must also receive `box-sizing:border-box !important`.

```css
.prod-img  { display:block !important; width:100% !important; box-sizing:border-box !important; }
.prod-info { display:block !important; width:100% !important; padding:20px 20px 24px !important; box-sizing:border-box !important; }
```

**Dark mode:** Never place a transparent-background logo where dark mode would invert it invisibly. Use solid or padded background cells behind logos.

**Image-to-text:** Hero text must be styled HTML layered over a background image — never a flat image of text.

**`width="100%"` on all images** with `max-width:600px` on the outer wrapper.

**Pure table-based layout — zero `<div>` tags.**

**Three-level mobile stacking pattern for any multi-column section:**
To stack columns on mobile, all three levels must be present in the media query — outer table, outer td, and inner td:

```css
@media only screen and (max-width:600px) {
  .outer-table { width:100% !important; }
  .outer-td    { display:block !important; width:100% !important; box-sizing:border-box !important; }
  .inner-td    { display:block !important; width:100% !important; box-sizing:border-box !important; }
}
```

Missing any one level causes columns to fail to stack in Gmail or Apple Mail.

---

## Platform-Specific Personalization Syntax

| Platform   | First Name                                      | Last Name                                        | City                          |
|------------|--------------------------------------------------|--------------------------------------------------|-------------------------------|
| Klaviyo    | `{{ first_name \| default: 'there' }}`           | `{{ last_name \| default: '' }}`                 | `{{ person.city }}`           |
| Omnisend   | `{{ contact.firstName \| default: 'there' }}`   | `{{ contact.lastName \| default: '' }}`          | `{{ contact.city }}`          |

Keep a running list of your own active clients and which platform each is on here — it saves a lookup every time a token needs checking:
- example-brand → Klaviyo

Every token must have a fallback. Never deploy a bare token with no default. Never invent a token whose data source is not confirmed in the client's ESP — flag it to Prescott.
