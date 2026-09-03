# Contributing

This started as one person's internal freelance tooling, published so it's
useful and legible to other people rather than just a portfolio link. If
you're building on it, here's what's actually welcome.

## Good contributions

- **Bug fixes** in the tools (`prescott/tools/`, `shared/`) — broken links,
  dead code paths, edge cases in the render/deploy pipeline.
- **New reference material** that follows the existing pattern — e.g. another
  platform's mobile best practices, another audit template, additional
  `amelia/references/` standards — as long as it's specific and enforceable,
  not generic marketing advice.
- **Additional ESP integrations** beyond Klaviyo/Omnisend/Constant Contact,
  following the pattern in `prescott/tools/klaviyo_client.py` and
  `omnisend_client.py`.
- **Test coverage** for `prescott/tools/*.py` — there's very little right
  now. `tests/test_copy_rules.py` is the only example; more in that spirit
  (testing the mechanical rules, not the strategy) are welcome.
- **Documentation fixes** — broken cross-references, unclear setup steps,
  missing context a newer marketer would need. `GLOSSARY.md` and
  `HOW_IT_WORKS.md` are both intentionally incomplete; PRs that extend them
  are welcome.

## What's not a good fit here

- **Rewriting Prescott or Amelia's personality/voice.** Fork it and make it
  your own instead — that's the point of forking rather than a config flag.
- **Client-specific logic.** Anything that only makes sense for one brand's
  quirks belongs in that brand's own `clients/{slug}/` folder, not in the
  shared engine.
- **New paid dependencies or paid APIs.** This repo is meant to run for the
  cost of a Claude Code subscription plus free-tier everything else. If your
  contribution requires a paid service, say so clearly in the PR and expect
  pushback on making it a hard dependency.

## Before opening a PR

- Run `python3 -m unittest discover tests/` if you touched anything that
  produces copy or HTML.
- If you changed `shared/universal_rules.md` or either agent's `CLAUDE.md`,
  check whether `GLOSSARY.md` or `HOW_IT_WORKS.md` need a matching update —
  they're meant to stay in sync with the rules they explain.
- Keep `clients/example-brand/` as the only non-gitignored folder under
  `clients/` — it's the schema reference, not a place for real data.

## Reporting issues

Open a GitHub issue. Include what you were trying to do, what happened
instead, and whether it's the agent's behavior (a `CLAUDE.md` rule not being
followed) or a tooling bug (a script failing) — they get debugged
differently.
