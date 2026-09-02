# AI Department Operations Manual
## Internal Reference

**Prepared by:** Jason Reis
**Document type:** Internal operations — not for client distribution
**Version:** 1.0

---

## Overview

This department operates a human-led, AI-augmented workflow built around three agents and one human strategist. This document explains what each agent is, what they do, how the week runs, and where the operator (referred to below as "Jay") sits in the chain at all times.

This is not a system that replaces strategic thinking. It is a system that removes the mechanical overhead so the operator can focus exclusively on the decisions that require experience, judgment, and client knowledge.

---

## The Team

### Jay — Strategist / Account Owner
Jay is the strategist, the client relationship owner, and the final decision-maker on everything that touches a client. He defines what the email program is trying to accomplish, approves everything before it reaches clients, and is accountable for every send. The AI system works for him — not around him.

### Benson — Chief of Staff / AI Architect
Benson manages the AI infrastructure — the hooks, scripts, automations, and agent coordination that make the system run. He holds cross-agent context, handles anything that doesn't belong to Prescott or Amelia, and is Jay's primary operational partner.

**Voice:** British male (`bm_george`)

### Prescott — Senior Email Marketing Strategist
Prescott runs the email strategy operation. Every Monday he pulls the prior week's performance data across all active clients, produces a performance narrative, and writes 2-3 campaign briefs per client that are ready for Amelia to execute. He manages the campaign calendar, flags flow issues, and tracks segmentation health.

Prescott does not communicate with clients. He prepares everything Jay uses to make decisions and communicate with clients.

**Voice:** American male (`am_michael`)

### Amelia Laurent — Senior Visual Designer / Email Production
Amelia handles all email design and production. She works exclusively from briefs Prescott has written and Jay has approved. She reads the client brand guide before every project, invokes design intelligence before rendering, produces the HTML, validates all assets, and deploys to the appropriate ESP. She also auto-updates Asana task status and the client's reporting sheet.

Amelia does not make strategic decisions. She executes the approved brief to the highest possible production standard.

**Voice:** British female (`bf_emma`)

---

## The Weekly Workflow

### Monday — Data & Strategy Day

**Morning (automated):**
- Prescott runs `prescott_weekly.py`
- Pulls prior week's data from the Master Google Sheet: campaign revenue, flow revenue, open rates, CTR, list growth, bounce rate — per client
- Compares current week vs. prior week to identify trends, not just snapshots
- Produces per-client performance narratives and 2-3 campaign briefs

**Jay's Monday review:**
- Reviews Prescott's narratives and flags
- Reviews draft briefs — edits, approves, or sends back
- Approves or adjusts the campaign calendar for the upcoming weeks
- Makes any flow or segmentation decisions flagged by Prescott

---

### Tuesday–Friday — Build & Deliver

**Once Jay approves a brief:**
- Brief goes to Amelia
- Amelia reads client brand guide
- Amelia designs and renders the email
- Fully rendered preview goes to Jay for review (Gate 2)
- Jay approves and submits to client via Asana
- Client approves before any activation

**Ongoing:**
- Prescott monitors flow performance and surfaces anomalies
- Benson handles infrastructure, tool maintenance, and any system issues

---

## The Two Client-Facing Gates

Nothing reaches a client without passing through both gates.

**Gate 1 — Calendar Approval**
Before any brief is written or any design work begins, Jay shares the 2-month campaign calendar with the client for directional approval. The client confirms the strategic direction. No build starts without this.

**Gate 2 — Email Approval**
Every individual email — fully rendered with subject line, preheader, and all assets — is submitted to the client for approval before activation. Nothing sends without explicit client sign-off.

These gates are non-negotiable. They exist to protect both the client and the operator.

---

## Platform Coverage

| Platform | Deployment |
|---|---|
| Klaviyo | Full API integration — Amelia deploys directly |
| Omnisend | Full integration |
| Constant Contact | Full integration |

All agency-built assets across all platforms are prefixed with `NX - ` for instant identification (adjust the prefix to your own convention — see `shared/universal_rules.md`).

---

## System Infrastructure

| Component | Purpose |
|---|---|
| Whisper PTT | Speak prompts instead of typing (optional) |
| Kokoro TTS | Agents speak responses aloud (optional) |
| Nightly maintenance | System health checks, log writes |
| Klaviyo / Omnisend clients | Direct API access to client accounts |

---

## What This Department Is and Is Not

**This is:**
- A human-led operation where Jay makes every strategic call
- An AI-augmented workflow that handles data, production, and execution mechanics
- A system designed to give one strategist the bandwidth to run multiple client accounts at a quality level a traditional team couldn't sustain

**This is not:**
- An AI system that runs independently
- A replacement for strategic expertise
- A shortcut that bypasses client review and approval

The department exists because Jay built it. It performs because Jay runs it.

---

*This document should be updated any time the workflow, agent roster, or client list changes significantly.*
