# How This System Thinks

The README tells you how to wire this up. This doc explains why it's built
the way it's built — useful if you're newer to email marketing or to running
an agency-style operation, since the shape of the system encodes a lot of
opinions that aren't spelled out anywhere else.

If a term below is unfamiliar, check `GLOSSARY.md` first.

## Why two agents instead of one

Prescott and Amelia are split on purpose, along a real professional line:
**strategy vs. execution.**

Prescott decides *who* gets an email, *why*, and *what it needs to
accomplish*. Amelia decides *how it looks and reads* to accomplish that. This
mirrors how a real email marketing team works — a strategist and a designer
are different skill sets, and collapsing them into one role (or one prompt)
tends to produce emails that are well-designed but strategically thin, or
well-targeted but visually generic.

The practical effect: Amelia is never allowed to invent who an email goes to
or why it's being sent. Prescott is never allowed to skip straight to layout
decisions. If you're using this as a learning reference, that's the habit
worth picking up even without the software: always write the brief before
you open the design tool.

## Why the handoff is a JSON file, not a conversation

Prescott writes a `campaign` block (goal, segment, subject line, offer).
Amelia fills in a `design` block (images, copy blocks, layout choices) in the
same file. See `examples/finished-email/brief.json` for a filled example.

A structured file instead of a freeform instruction does two things:

1. **It forces completeness.** Prescott can't hand off a brief that's missing
   a segment or a goal, because the field is just sitting there empty and
   Amelia's rules require asking one precise question when `campaign` fields
   are missing (see `amelia/CLAUDE.md`).
2. **It's auditable.** Every brief that ever existed is a file on disk. You
   can look at a brief from three months ago and see exactly what was
   requested, versus trying to reconstruct it from a chat transcript.

## Why there's a rendering script instead of an LLM writing HTML

`amelia_render.py` generates the actual HTML from a Jinja2 template — no LLM
involvement in producing markup. Email HTML is a genuinely hostile rendering
environment (Outlook, Gmail, and Apple Mail all interpret CSS differently),
and a template that's been proven to render correctly across clients is worth
more than a fresh HTML generation every time. The LLM's job is filling in the
*content* of the template (copy, image choices, layout flags) — not
re-inventing table-based email markup on every run. This is also just faster
and cheaper: no reason to spend a model call regenerating boilerplate that a
script does deterministically.

This is a general pattern worth noticing throughout the repo: anything
mechanical and repeatable is a Python script (`prescott/tools/`). Anything
that requires judgment, taste, or strategy is the agent's job. See
`shared/universal_rules.md` and the SOPs in `prescott/sops/` for where that
line gets drawn explicitly.

## Why two approval gates, not one

**Gate 1 (calendar)** confirms strategic direction before any design work
starts. **Gate 2 (email)** confirms the finished, rendered email before it
goes to the client's ESP.

Splitting them matters because they catch different kinds of mistakes. Gate 1
catches "we're solving the wrong problem" before anyone spends time building.
Gate 2 catches "this specific execution is wrong" (a broken image, an off-
brand tone, a typo) after the work exists but before it can do any damage. A
single combined gate tends to either rubber-stamp everything (reviewer is
tired of re-litigating strategy every time) or become a bottleneck (every
small creative tweak requires a full strategy re-approval). See
`prescott/sops/human_in_the_loop_framework.md` for the full decision map of
what AI does autonomously vs. what always comes back to a human.

## Why the self-critique gate exists (Amelia, Step 5b)

Before any email is considered finished, Amelia answers six yes/no questions
against her own output (visual hierarchy, offer clarity, copy weight, brand
feel, mobile, one message — see `amelia/CLAUDE.md`). This isn't decoration.
It's the same function a second set of human eyes would serve on a small
team that can't actually afford a second designer to review every send. It
catches the kind of error a first pass tends to miss because the person who
built it is too close to it — over-explaining an offer that was already
obvious, or leaving in a hero + CTA block that repeats the same message
twice.

## Where to look next

- `examples/finished-email/` — a real brief through the real render script,
  end to end, so you can see the output before connecting any accounts.
- `prescott/sops/ai_department_operations_manual.md` — the weekly operating
  rhythm this system runs on.
- `prescott/playbooks/Lifecycle Revenue Playbook v3.md` — the strategic
  framework Prescott reasons from. This is the actual "textbook" in this
  repo if you're trying to learn the strategy, not just the tooling.
