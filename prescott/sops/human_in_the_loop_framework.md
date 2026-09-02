# Human-in-the-Loop Framework
## Internal Reference

**Prepared by:** Jason Reis
**Document type:** Internal operations — not for client distribution
**Version:** 1.0

---

## Purpose

This document defines exactly where AI operates autonomously and where the operator's judgment ("Jay" below) is required at every stage of the email marketing workflow. It exists to make one thing unambiguous: the AI system is the engine. Jay is the driver. Every client-facing decision, every send, every strategic call has a human being accountable for it.

---

## The Core Principle

AI handles speed, consistency, and data processing at a scale no individual can match. Jay handles strategy, brand judgment, client relationships, and every decision that actually affects what a client sees or receives.

Neither works without the other. That is by design.

---

## Decision Map — Who Handles What

### 1. Data & Reporting

| Task | Handler | Notes |
|---|---|---|
| Pull weekly performance data from client platforms | AI (Prescott) | Automated Monday workflow |
| Calculate campaign revenue, flow revenue, open rates, CTR, list health | AI (Prescott) | Pulled from Google Sheet rawdata tab |
| Identify trends, flags, and performance signals | AI (Prescott) | 2-week comparison, not just snapshots |
| Interpret what the data means for this client, this week | **Jay** | AI surfaces; Jay decides what it means |
| Decide what action to take based on data | **Jay** | Non-delegable |
| Write performance narrative for client dashboard | AI (Prescott) | Jay reviews before client sees it |

---

### 2. Strategy

| Task | Handler | Notes |
|---|---|---|
| Draft campaign calendar (2-month horizon) | AI (Prescott) | Based on playbook + client data |
| Finalize and approve campaign calendar | **Jay** | Gate 1 — client does not see until Jay approves |
| Identify segmentation opportunities | AI (Prescott) | Flags and recommendations only |
| Approve segmentation logic before execution | **Jay** | Jay confirms before any segment is used in a live send |
| Identify flow gaps or underperforming flows | AI (Prescott) | Surfaced in weekly narrative |
| Decide which flows to rebuild, pause, or prioritize | **Jay** | Non-delegable |
| Develop offer strategy (discount depth, timing, exclusions) | **Jay** | AI can model scenarios; Jay decides |

---

### 3. Creative Production

| Task | Handler | Notes |
|---|---|---|
| Write creative brief (goal, segment, offer, subject lines, tone) | AI (Prescott) | Jay reviews before brief goes to Amelia |
| Approve brief before design begins | **Jay** | No design work starts without brief sign-off |
| Design email (HTML, layout, visual direction) | AI (Amelia) | Works from approved brief only |
| Review rendered email before client sees it | **Jay** | Gate 2 — nothing goes to client without Jay's review |
| Approve final email for client submission | **Jay** | Non-delegable |

---

### 4. Client Communication

| Task | Handler | Notes |
|---|---|---|
| Prepare client-facing materials (calendar, previews, reports) | AI (Prescott/Amelia) | Drafted by AI, reviewed by Jay |
| Present strategy, respond to client questions, manage relationships | **Jay** | AI does not communicate with clients directly |
| Make strategic recommendations to clients | **Jay** | AI informs; Jay recommends |
| Handle client concerns, escalations, or course corrections | **Jay** | Non-delegable |

---

### 5. Deployment

| Task | Handler | Notes |
|---|---|---|
| Build campaign in ESP (Klaviyo, Omnisend, Constant Contact) | AI (Amelia) | Follows approved brief and design |
| Verify send list, subject line, and send time before activation | **Jay** | Final human checkpoint before anything goes live |
| Activate send | **Jay** | Jay triggers the send or explicitly authorizes it |
| Monitor post-send performance | AI (Prescott) | Automated; flags surfaced to Jay |

---

## What AI Is Explicitly Not Trusted to Decide

- Whether to send an email to a client's full list
- Offer depth or discount strategy
- Whether a campaign is brand-appropriate
- How to respond to a client concern
- Whether a performance signal represents a real problem or normal variance
- Anything that requires knowing what is happening inside the client's business

---

## Why This Model Works

The AI system processes a full week of multi-client performance data, identifies patterns across every metric, drafts briefs, and builds email production at a speed and consistency no traditional two-person team could match. That speed only has value if human judgment is making the right calls at the right moments.

Jay's role is not to do what AI does slowly. His role is to do what AI cannot do at all — make the strategic calls, maintain the client relationships, and ensure everything that leaves this department reflects a standard the operator can stand behind.

---

*This document should be reviewed and updated any time the workflow or agent capabilities change.*
