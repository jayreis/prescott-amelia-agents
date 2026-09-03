# Finished Example — Abandoned Checkout Email

This is what the brief -> render pipeline actually produces, with no client
account, no Google Sheet, and no API keys required. It's here so you can see
the finished product before you connect anything.

## What's in this folder

- **`brief.json`** — `prescott/briefs/example-brand/AbandonedCheckout_Email1.json`
  with its one placeholder filled in and its `image_url` fields pointed at
  [placehold.co](https://placehold.co) instead of `example-brand.com` (which
  doesn't resolve). Everything else — copy, structure, section flags — is
  untouched from what Prescott would actually leave in a brief.
- **`rendered_email.html`** — the exact output of running the real production
  script against that brief:
  ```bash
  python3 prescott/tools/amelia_render.py --brief examples/finished-email/brief.json
  ```
  This is the same `amelia_render.py` that runs against real client briefs.
  Nothing about the HTML generation is mocked or simplified for this example.
- **`screenshot.png`** — what that HTML looks like rendered, captured the same
  way `amelia_deploy.py` captures the screenshot that gets attached to the
  Asana review task (Gate 2 review artifact).

## What normally happens next

In a real run, `amelia_deploy.py` takes this same HTML, screenshots it,
creates (or updates) an Asana task with that screenshot attached, and logs the
send to the client's reporting sheet. That step needs an Asana token and
project ID, which is why it isn't reproduced here — but the HTML and
screenshot in this folder are identical to what that step would attach.

## Why this brief specifically

It's deliberately the plainest brief in the repo: no discount, no urgency, no
social proof. That's on purpose — it shows the pipeline's default output with
nothing dressed up, so you can see the actual floor of what "no design work
required, just fill in the brief" gets you. Read `amelia/CLAUDE.md` for the
six-question self-critique gate Amelia runs before any brief like this one is
considered done.
