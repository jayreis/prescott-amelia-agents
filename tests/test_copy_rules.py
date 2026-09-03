#!/usr/bin/env python3
"""
test_copy_rules.py — Checks rendered email HTML against shared/universal_rules.md.

Run as a test suite (checks examples/finished-email/rendered_email.html):
    python3 -m unittest tests/test_copy_rules.py -v

Or point it at any other rendered email to QA it before it ships:
    python3 tests/test_copy_rules.py path/to/rendered_email.html

This is a reference implementation of the QC checklist mentioned in
shared/universal_rules.md, not a complete one. It catches the mechanical
rules — em dashes, emoji, banned marketing words, leftover lorem ipsum. It
cannot catch "invented facts" or "off-brand voice" — those require a human
who knows the brand, same as the human review gates in
prescott/sops/human_in_the_loop_framework.md describe. Use this as an
automated first pass, not a replacement for Gate 2 review.
"""

import re
import sys
import unittest
from pathlib import Path

DEFAULT_TARGET = Path(__file__).parent.parent / "examples" / "finished-email" / "rendered_email.html"

# Mirrors the banned list in shared/universal_rules.md — "No Marketing-Speak".
BANNED_WORDS = [
    "revolutionary", "game-changing", "unlock", "elevate", "seamless",
    "robust", "leverage", "empower", "synergy", "ecosystem", "innovative",
    "cutting-edge", "best-in-class", "world-class", "disruptive", "holistic",
]

EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+",
    flags=re.UNICODE,
)


def extract_visible_text(html: str) -> str:
    """Crude tag stripper for the table-based email HTML this repo generates.
    Not a substitute for a real HTML parser on anything more complex."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def check_copy(text: str) -> list:
    """Returns a list of human-readable violation strings. Empty = clean."""
    violations = []
    lowered = text.lower()

    if "—" in text:
        violations.append("Contains an em dash - not permitted in shipped copy (shared/universal_rules.md).")

    if EMOJI_PATTERN.search(text):
        violations.append("Contains emoji - not permitted in any deliverable.")

    if "lorem ipsum" in lowered:
        violations.append("Contains literal lorem ipsum placeholder text.")

    for word in BANNED_WORDS:
        if word in lowered:
            violations.append(f"Contains banned marketing word: '{word}'")

    return violations


class TestCopyRules(unittest.TestCase):
    """Runs against the checked-in example. Point CLI usage at a different
    file (see module docstring) to QA your own rendered output instead."""

    def test_example_email_passes_universal_rules(self):
        self.assertTrue(DEFAULT_TARGET.exists(), f"No rendered HTML found at {DEFAULT_TARGET}")
        html = DEFAULT_TARGET.read_text(encoding="utf-8")
        violations = check_copy(extract_visible_text(html))
        self.assertEqual(violations, [], "\n" + "\n".join(violations))


def _run_cli(path_str: str) -> int:
    target = Path(path_str)
    if not target.exists():
        print(f"ERROR: file not found: {target}")
        return 1
    violations = check_copy(extract_visible_text(target.read_text(encoding="utf-8")))
    if violations:
        print(f"FAIL — {len(violations)} violation(s) in {target}:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"PASS — {target} is clean.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        sys.exit(_run_cli(sys.argv[1]))
    unittest.main()
