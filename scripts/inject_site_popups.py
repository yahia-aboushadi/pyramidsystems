#!/usr/bin/env python3
"""
inject_site_popups.py - Strip the capability-magnet + consultation popups from
site-wide pages (homepage, services hub, contact, about-us, contract-vehicles
hub + 7 CV detail pages).

Why this script no longer INJECTS:
  Popups were originally propagated site-wide so every page got both the
  capability-statement PDF magnet and the consultation request popup. Two
  problems with that:
    1) The popup CSS lives inline in scripts/build_service_pages.py (it ships
       into the 5 service pages directly). The non-service pages received the
       popup HTML but not the matching CSS, so popup-magnet rendered as a
       giant unstyled block on the homepage (visible bug, see screenshot
       from 2026-06-04 review).
    2) Strategically these are deep-funnel asks. A visitor on the homepage
       isn't ready to download a federal capability statement or request a
       consultation; they're still figuring out what Pyramid does. The
       popups belong on service pages where context already exists.

  Decision: scope popups to the 5 service pages only. They're built directly
  by build_service_pages.py with their CSS attached. This script now wipes
  any PYRAMID:popups marker blocks that were previously injected into the
  12 non-service pages so a re-run cleans up old state.

If the decision ever reverses, this script's git history shows the prior
inject logic. Easier to restore from history than to keep dead code around.

All targeted blocks live inside <!-- PYRAMID:popups:START --> ... <!-- PYRAMID:popups:END -->
markers, so the strip is precise and idempotent.

Run: python3 scripts/inject_site_popups.py
"""
from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

# Pages where popups may have been previously injected and should now be removed.
# The 5 service pages are NOT in this list — they get popups directly from
# build_service_pages.py and keep them.
TARGET_PAGES = [
    "index.html",
    "services/index.html",
    "contact/index.html",
    "about-us/index.html",
    "contract-vehicles/index.html",
    "contract-vehicles/fdic-itas-iii.html",
    "contract-vehicles/gsa-8a-stars-iii.html",
    "contract-vehicles/gsa-it-schedule-70.html",
    "contract-vehicles/gsa-oasis-plus.html",
    "contract-vehicles/hhs-cms-sparc.html",
    "contract-vehicles/hud-om-bpa.html",
    "contract-vehicles/sec-one-it.html",
]

MARKER_START = "<!-- PYRAMID:popups:START -->"
MARKER_END = "<!-- PYRAMID:popups:END -->"

# Matches a marker block plus any surrounding whitespace/newlines on its line
# so the strip leaves a clean file rather than a stack of blank lines.
MARKER_BLOCK_RE = re.compile(
    r"[ \t]*" + re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"[ \t]*\n?",
    re.DOTALL,
)


def strip(html: str) -> tuple[str, bool]:
    """Remove any popup marker blocks. Returns (new_html, changed)."""
    new_html, count = MARKER_BLOCK_RE.subn("", html)
    return new_html, count > 0


def main() -> int:
    cleaned = 0
    already_clean = 0
    missing = 0
    for rel in TARGET_PAGES:
        path = ROOT / rel
        if not path.exists():
            print(f"  - {rel} (skip: not found)")
            missing += 1
            continue
        before = path.read_text(encoding="utf-8")
        after, changed = strip(before)
        if changed:
            path.write_text(after, encoding="utf-8")
            print(f"  - {rel} (stripped popup markers)")
            cleaned += 1
        else:
            print(f"  = {rel} (already clean)")
            already_clean += 1

    print(f"\nStripped popups from {cleaned} pages; {already_clean} already clean; {missing} missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
