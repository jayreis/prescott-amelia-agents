# Glossary

Terms used throughout this repo, especially in `prescott/playbooks/Lifecycle
Revenue Playbook v3.md`, `prescott/CLAUDE.md`, and `prescott/audit-templates/`.
If you're new to email marketing, read this before those — they use these
terms without redefining them.

## Email marketing fundamentals

**ESP (Email Service Provider)** — the platform that actually sends the
emails and stores subscriber data. This repo integrates with Klaviyo,
Omnisend, and Constant Contact.

**Campaign** — a one-time email sent to a chosen segment on a specific date
(e.g. a Friday sale announcement). Contrast with a flow.

**Flow** (also called an automation) — an email or sequence of emails
triggered automatically by a subscriber's behavior (e.g. abandoning a cart,
signing up, making a purchase), not sent manually on a calendar date.

**Segment** — a subset of subscribers grouped by a shared trait or behavior
(e.g. "purchased in the last 30 days," "opened 3+ emails," "never purchased").
The opposite of a segment is a full-list send — see "full-list blast" below.

**List** — the full pool of subscribers for a client, before segmentation.

**Preheader** (also "preview text") — the line of text an inbox shows next to
or below the subject line, before the email is opened. Extends the subject
line; should never just repeat it.

**Full-list blast** — sending to every subscriber regardless of segment.
Prescott treats this as close to a code smell — see his "professional pet
peeves" in `prescott/CLAUDE.md`.

## Flow types referenced in this repo

**Welcome series** — the flow a new subscriber enters after signing up.
Benchmark in the playbook: 3-4 emails over 5-10 days.

**Browse abandonment** — a flow triggered when someone views a product page
but doesn't add anything to cart.

**Cart abandonment** — a flow triggered when someone adds an item to cart but
doesn't reach checkout.

**Checkout abandonment** (also "abandoned checkout") — a flow triggered when
someone starts checkout (email/info captured) but doesn't complete the order.
Usually carries more urgency than cart abandonment since the buyer got
further. This is the flow used in `examples/finished-email/`.

**Replenishment flow** — a flow timed around when a consumable product is
likely running out, prompting a reorder.

**Winback / re-engagement flow** — targets subscribers or customers who have
gone quiet, trying to bring them back before they're suppressed or churned
entirely.

## Metrics

**Open rate** — % of delivered emails that were opened. Least trustworthy
metric on this list (affected by Apple Mail privacy protections, which
auto-open emails for image caching) — see the playbook's metric hierarchy,
where it's ranked last and explicitly "contextual only."

**CTR (click-through rate)** — % of delivered emails that got at least one
click. Read as an intent signal — someone who clicks is telling you something
opens alone don't.

**Conversion rate** — % of clicks (or sends) that resulted in a purchase.

**RPS (revenue per send)** — total revenue divided by number of emails sent.
The playbook's #2 metric, right under total revenue — it catches the case
where revenue is up but you're just sending more emails, not sending better
ones.

**AOV (average order value)** — average $ per order.

**LTV (lifetime value)** — total revenue a customer is expected to generate
over their full relationship with the brand, not just one order.

**Bounce rate** — % of sends that failed to deliver. A hard bounce (bad
address) is worse for deliverability than a soft bounce (temporary issue like
a full inbox).

**List health / deliverability** — a general term for whether your sends are
reliably reaching the inbox (vs. spam/promotions folder) — driven by bounce
rate, complaint rate, and engagement trends over time.

**Net list growth** — new subscribers minus unsubscribes minus suppressions,
over a given period.

## Strategy terms specific to this repo's playbook

**Discount ladder** — the idea that every discount a brand offers (welcome
offer, cart abandonment offer, seasonal sale, VIP tier) should sit in a
defined hierarchy. If a flow's automatic discount is deeper than a campaign's
manual one, subscribers learn to wait for the flow instead of buying at
full campaign price — see Prescott's "offer cannibalization" failure mode in
`prescott/CLAUDE.md`.

**Attribution window** — the time period after a click (or send) during which
a resulting purchase is credited to that email. Needed because flows and
campaigns can overlap within hours of each other, and without a defined
window, the same sale can get double-counted or nobody gets credit.

**Brand maturity tier** — the playbook's framework for sizing strategic advice
to a brand's revenue stage ($1-3M / $5-30M / $50M+), because the right advice
at one stage actively hurts a brand at another. See
`prescott/playbooks/Lifecycle Revenue Playbook v3.md` Section 3 and
`prescott/audit-templates/prospect_audit_checklist.md` Section 10.

**Suppression** — deliberately excluding a segment from a send — e.g.
suppressing campaign sends to someone currently in the first days of a
welcome flow, so they don't get double-messaged.

## This repo's specific terms

**Brief** — the JSON file Prescott writes and Amelia builds from (see
`prescott/briefs/{client}/`). Contains a `campaign` block (goal, segment,
subject line, offer) and a `design` block (images, copy blocks, layout).
See `examples/finished-email/` for what a filled-in brief becomes.

**Gate 1 / Gate 2** — the two mandatory human approval checkpoints before
anything reaches a client. Gate 1 is calendar-level (does the client agree
with the 2-month direction). Gate 2 is per-email (does the client approve
this specific rendered email before it sends). See
`prescott/sops/human_in_the_loop_framework.md`.

**Revenue case** — the four-line `RECOMMENDATION / WHY / ESTIMATED IMPACT /
HOW TO MEASURE` block Prescott is required to attach to every strategic
recommendation. See "Revenue Case Standard" in `prescott/CLAUDE.md`.

**Session context / prebake** — a cached file (`prebake_session.py`) combining
a client's brand guide, image library, and pending briefs into one file so
Amelia doesn't have to re-read three separate sources on every build.

**NX prefix** — the naming convention (`NX - Welcome Series`, etc.) applied to
every campaign, flow, list, and segment created in a client's ESP, so
agency-built assets are instantly identifiable. Rename it to your own
convention — see `shared/universal_rules.md`.
