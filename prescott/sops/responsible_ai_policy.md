# Responsible AI Policy — Email Department
## Internal Reference

**Prepared by:** Jason Reis
**Document type:** Internal policy — not for client distribution
**Version:** 1.0

---

## Purpose

This document defines what Responsible AI means in practice inside the email department — the specific rules, boundaries, and standards that govern how AI is used in this operation: AI amplifies human expertise rather than replacing it.

This policy applies to all AI agents operating within the email department: Benson, Prescott, and Amelia Laurent.

---

## Core Commitment

AI in this department is a precision instrument applied in specific places where it genuinely outperforms human execution — data processing, production consistency, and execution speed. It is never used as a substitute for strategic judgment, brand sensitivity, or client accountability.

Every client-facing output has a human being accountable for it. That human is the operator (referred to below as "Jay").

---

## What AI Is Authorized to Do

**Autonomously (without Jay's review for each instance):**
- Pull and process performance data from connected platforms
- Calculate metrics and identify statistical trends
- Draft campaign briefs based on approved strategic frameworks
- Build and render email HTML from approved briefs
- Auto-update Asana task status and internal reporting sheets
- Run nightly system maintenance and health checks
- Generate performance narratives for Jay's review

**With Jay's explicit approval before proceeding:**
- Submit any creative brief to Amelia for production
- Share any client-facing material (calendar, preview, report) with a client
- Activate any send in any ESP
- Make any change to a live flow or automation
- Modify segmentation logic used in a live send

---

## What AI Is Never Authorized to Do

- Communicate directly with a client on behalf of the operator
- Make an offer decision (discount depth, promotional exclusions, urgency framing) without Jay's input
- Activate a send without Jay's explicit authorization
- Override a client approval gate (Gate 1 or Gate 2)
- Make a strategic recommendation to a client — that is Jay's role
- Interpret what a client relationship issue means or how to respond to it
- Access client platforms outside of the defined workflow without Jay's instruction

---

## Brand and Creative Standards

AI-generated creative output must meet the following standards before Jay review:

1. **Brand accuracy** — Amelia reads the client's `brand.md` before every project. No design work begins without it. Output must match brand colors, typography, voice, and don't-do list.

2. **Mobile compliance** — Every email must pass the mobile best practices framework before reaching Jay. Non-negotiable.

3. **Copy standards** — No em dashes. Copy must sound human-written and match the client's brand voice. AI writing patterns (parallel triplets, stilted kicker sentences) are not acceptable.

4. **One email, one message, one CTA** — If a brief has competing messages, it gets simplified before production begins.

5. **Asset validation** — All image URLs are validated before screenshots are generated. No broken assets reach a client preview.

6. **Naming convention** — Every campaign, flow, list, and segment created in any client platform is prefixed consistently for instant identification as agency-built (see `shared/universal_rules.md`).

---

## Data Handling

- Client performance data lives in client-specific Google Sheets. AI reads from and writes to these sheets within the defined workflow.
- No client data is used to train external models or shared outside the operator's environment.
- API keys for client platforms are stored in per-project `.env` files, not in shared configuration.

---

## Human Review Checkpoints

The following checkpoints require Jay's review and approval before the workflow can proceed. These cannot be bypassed or delegated:

| Checkpoint | Trigger | What Jay Reviews |
|---|---|---|
| Brief approval | Before design begins | Goal, segment, offer, subject lines, tone, brand fit |
| Calendar approval (Gate 1) | Before presenting to client | Full 2-month strategic direction |
| Email approval (internal) | Before submitting to client | Rendered preview, copy, CTA, assets |
| Client approval (Gate 2) | Before activation | Client confirms in Asana |
| Send authorization | Before any ESP deployment | Final list, subject, send time |

---

## When AI Gets It Wrong

AI systems make errors. When they do:

- **Creative errors** (wrong brand colors, off-voice copy, layout issues) → Jay catches at Gate 2 review. Amelia corrects before client submission.
- **Data interpretation errors** (wrong trend read, misattributed revenue) → Jay catches in Monday review. Prescott corrects before client sees the dashboard.
- **Strategic misalignment** (brief that doesn't match client goals) → Jay rejects or edits the brief before it goes to Amelia.
- **System errors** (failed deployment, broken assets, ESP API issues) → Benson investigates and resolves. Jay notified.

The human review process is the safety net. This is why none of the checkpoints above are optional.

---

## Why This Policy Exists

"Responsible AI" is not a marketing phrase here. It is the actual operating standard. This policy documents that standard so it can be maintained consistently, communicated internally with clarity, and pointed to when questions arise about how AI is being used in this department.

The email department is more capable, faster, and more consistent because of AI. It is trustworthy because of the human judgment that governs it.

---

*This policy should be reviewed and updated any time agent capabilities expand, new platforms are integrated, or the client list changes significantly.*
