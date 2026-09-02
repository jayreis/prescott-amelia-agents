# CLAUDE.md

This repo defines two Claude Code sub-agents for running an email marketing
department: **Prescott** (strategist) and **Amelia** (designer/builder).

- Prescott's full identity, rules, and workflow: `prescott/CLAUDE.md`
- Amelia's full identity, rules, and workflow: `amelia/CLAUDE.md`
- Copy/formatting rules both agents must follow: `shared/universal_rules.md`

When the user addresses "Prescott" or "Amelia" by name, load that agent's
CLAUDE.md and act from that identity. See README.md for first-time setup
(Google Sheets, Asana, Klaviyo/Omnisend credentials) before running anything
that touches a real API.

Real client data (brand guides, image libraries, `.env` credentials) lives
under `clients/{client-slug}/` and is gitignored except for the `example-brand`
placeholder — that folder is the schema reference, not a real client.
