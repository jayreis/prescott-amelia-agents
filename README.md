# Prescott & Amelia — AI Email Marketing Department

Two Claude Code sub-agents that run an email marketing department end to end:

- **Prescott** — senior strategist. Reads weekly performance data, writes the
  Monday narrative, and writes creative briefs.
- **Amelia** — senior designer/builder. Turns Prescott's briefs into
  production-ready HTML emails, screenshots them, and opens an Asana review
  task automatically.

This is the actual system I use to run my own freelance email marketing
practice, stripped of real client data and credentials so it's safe to run
against your own accounts. It connects to Google Sheets (for reporting),
Asana (for review), and Klaviyo/Omnisend (as the ESP).

I'm sharing it because it's genuinely useful, and because it's a better
demonstration of what I can build than a portfolio page is. If you use it and
build on it, I'd love to hear about it.

— Jason Reis, [jasonareis.com](https://jasonareis.com)

---

## What's in here

```
prescott/           Prescott's identity, rules, tools, and reference docs
amelia/              Amelia's identity and design/copy standards
shared/              Config + auth utilities both agents depend on
clients/             Per-client data — only example-brand/ is real (a schema reference)
```

- `prescott/CLAUDE.md` / `amelia/CLAUDE.md` — each agent's full identity, voice, and standing rules
- `prescott/tools/` — the Python scripts that actually do the work (Klaviyo/Omnisend API clients, HTML renderer, Asana deploy pipeline, weekly report reader)
- `prescott/playbooks/Lifecycle Revenue Playbook v3.md` — the strategic framework Prescott reasons from
- `prescott/sops/` — how the human+AI workflow is governed (approval gates, what AI is/isn't authorized to do on its own)
- `shared/universal_rules.md` — copy rules both agents follow (no em dashes, no emoji, no invented facts, etc.)

## Prerequisites

- [Claude Code CLI](https://claude.com/claude-code)
- Python 3.11+
- A Google account, an Asana account, and a Klaviyo and/or Omnisend account for whichever client(s) you're connecting

## Quick start

```bash
git clone <this-repo>
cd prescott-amelia-agents
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
cp clients/example-brand/.env.example clients/example-brand/.env
```

Then open the repo in Claude Code and paste the setup prompt below — it will
walk you through the rest interactively rather than you hand-editing five
different config files.

---

## Setup prompt — paste this into Claude Code after cloning

```
I just cloned the Prescott & Amelia repo. Walk me through connecting it to my
own accounts, one step at a time — don't just dump a checklist, actually do
the setup with me:

1. Google Sheets — help me create a Master Email Client Reporting Sheet with
   these tabs, and confirm my sheet matches what shared/brand_config.py and
   prescott/tools/*.py expect to read:
     - "Clients" — columns: Client Name, Platform, ESP Private API Key,
       Active (TRUE/FALSE, must be column D), optionally Brand Accent Color,
       Brand Dark Color, Brand Light Text Color, Asana Section ID (To Do)
     - "rawdata" — Week Start, Client, Platform, Campaign Revenue, Flow
       Revenue, Total Revenue, Open Rate, CTR, New Subs, Unsubs,
       Net List Growth, Bounce Rate
     - "flow_performance" — Week Start, Client, Platform, Flow Name, Revenue,
       Open Rate, CTR, Unsubscribes, Delivered, Performance Flag
     - "Ops Log", "Monday Report", "Flow Audit Tracker" — used by
       prescott/tools/ops_logger.py, check that file for the exact columns
       each expects
   Then help me set up Google OAuth: create a Desktop app OAuth client in
   Google Cloud Console, save the JSON as config/credentials.json, put my
   sheet's ID in .env as MASTER_SHEET_ID, and run
   `python3 shared/google_auth.py --reauth` to do the first-time browser login.

2. Asana — help me get a Personal Access Token from
   app.asana.com/0/my-apps, find my Asana user GID (for
   ASANA_DEFAULT_ASSIGNEE in .env), and find the project ID + "To Do" section
   ID for wherever I want email review tasks to land. Put the token and
   project ID in clients/example-brand/.env (or my real client's .env).

3. Klaviyo and/or Omnisend — help me generate a private API key for my
   account and add it to the right .env file (or the Master Sheet's "ESP
   Private API Key" column, which takes priority).

4. Once everything's in place, run a smoke test for each connection:
   - python3 prescott/tools/prescott_weekly.py --client "example-brand"
   - python3 prescott/tools/klaviyo_client.py "example-brand" flows   (if using Klaviyo)
   - python3 prescott/tools/omnisend_client.py "example-brand" campaigns   (if using Omnisend)
   Tell me what each error means if something isn't wired up yet, and fix it
   with me rather than just reporting the failure.

5. Ask me my real client's name/slug and rename the example-brand folder
   structure (clients/example-brand/, prescott/briefs/example-brand/) to
   match, then update CLIENT_BRAND / CLIENT_CONFIG entries in
   prescott/tools/amelia_render.py and amelia_deploy.py — or better, tell me
   how to skip those entirely by adding the Brand Accent/Dark/Light Text
   Color and Asana Section ID columns to my Clients tab row instead.

Don't proceed to any real API call until you've confirmed with me that the
relevant key/ID is actually filled in — ask, don't assume a placeholder is real.
```

---

## Using the agents day to day

Once connected, address them by name in Claude Code:

- **"Hey Prescott, run the Monday report for example-brand"** → pulls last
  week's data, writes the performance narrative, drafts 2-3 campaign briefs
- **"Hey Amelia, build the brief in prescott/briefs/example-brand/"** → reads
  the brand guide, fills the design fields, renders HTML, deploys to Asana
  for review

See `prescott/sops/human_in_the_loop_framework.md` for exactly which
decisions the AI makes on its own vs. which ones always come back to you —
nothing sends to a client without two rounds of human approval (Gate 1:
calendar direction, Gate 2: the individual rendered email).

## What's *not* included

This repo ships the reusable engine — API clients, the HTML renderer, the
weekly report reader, the deploy pipeline. It does not include the
heavily bespoke dashboard-building scripts I run for my own multi-client
roster (per-client Google Sheet dashboard rebuilds with custom charts) —
those are wired to one specific sheet layout per client and wouldn't be
useful to you as-is. The `prescott/tools/ops_logger.py` module shows the
pattern if you want to build your own.

## License

MIT — see LICENSE. Use it, fork it, adapt it for your own practice.
