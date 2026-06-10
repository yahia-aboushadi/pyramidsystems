#!/usr/bin/env python3
"""
install_markers.py — ONE-SHOT setup script.

Wraps the existing a11y-widget, header, and footer regions on every page
with TEMPLATE:name:START / TEMPLATE:name:END comments so that
apply_templates.py can keep them in sync going forward.

Run this ONCE during the template-system rollout. Afterwards, use
apply_templates.py for ongoing updates.

The script is idempotent — re-running it on a page that already has
markers is a no-op. Pages without the expected region are silently
skipped (they'll show up in the final "no markers" count from
apply_templates.py).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {"templates", "scripts", "emails", "node_modules", ".git"}
EXCLUDE_FILES = {"preview-mocks.html"}


def find_pages(root: Path) -> list[Path]:
    pages = []
    for p in root.rglob("*.html"):
        if p.name in EXCLUDE_FILES:
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        pages.append(p)
    return sorted(pages)


# --- a11y widget ---------------------------------------------------------
# Existing block opens with `<!-- Pyramid Systems accessibility widget` and
# ends with `<script src=".../pyramid-a11y.js" defer></script>`.
A11Y_RX = re.compile(
    r"(?P<body>"
    r"\s*<!--\s*Pyramid Systems accessibility widget[^-]*-->.*?"
    r'<script src="[^"]*pyramid-a11y\.js"\s+defer></script>'
    r")",
    re.DOTALL,
)

# --- header --------------------------------------------------------------
# Match the FIRST <header class="header">...</header> block.
# Use non-greedy + DOTALL to capture the contents.
HEADER_RX = re.compile(
    r'(?P<body><header class="header">.*?</header>)',
    re.DOTALL,
)

# --- footer --------------------------------------------------------------
# Match the LAST <footer class="footer">...</footer> on the page.
FOOTER_RX = re.compile(
    r'(?P<body><footer class="footer">.*?</footer>)',
    re.DOTALL,
)


def already_marked(text: str, name: str) -> bool:
    return f"TEMPLATE:{name}:START" in text


def wrap(text: str, name: str, pattern: re.Pattern) -> tuple[str, bool]:
    """Wrap the first match with TEMPLATE markers. No-op if already marked."""
    if already_marked(text, name):
        return text, False
    m = pattern.search(text)
    if not m:
        return text, False
    start = m.start("body")
    end = m.end("body")
    body = text[start:end]
    # Preserve leading whitespace of the original block — sniff from line
    # the body starts on.
    line_start = text.rfind("\n", 0, start) + 1
    indent = text[line_start:start]
    if not indent.strip() == "" and indent:  # safety
        indent = ""
    # Insert markers on their own lines, matched-indent
    replacement = (
        f"{indent}<!-- TEMPLATE:{name}:START -->\n"
        f"{indent}{body}\n"
        f"{indent}<!-- TEMPLATE:{name}:END -->"
    )
    new = text[:line_start] + replacement + text[end:]
    return new, True


def process(page: Path) -> list[str]:
    text = page.read_text(encoding="utf-8")
    original = text
    added = []
    for name, pattern in [
        ("a11y_widget", A11Y_RX),
        ("header",      HEADER_RX),
        ("footer",      FOOTER_RX),
    ]:
        text, did = wrap(text, name, pattern)
        if did:
            added.append(name)
    if text != original:
        page.write_text(text, encoding="utf-8")
    return added


def main() -> int:
    pages = find_pages(ROOT)
    print(f"Scanning {len(pages)} HTML pages for marker installation\n")

    by_region = {"a11y_widget": 0, "header": 0, "footer": 0}
    touched = 0
    for page in pages:
        added = process(page)
        if added:
            touched += 1
            for r in added:
                by_region[r] += 1
            print(f"  ✓ {page.relative_to(ROOT)}  [+{', +'.join(added)}]")

    print()
    print(f"Pages touched: {touched}")
    for r, n in by_region.items():
        print(f"  {r:14} markers installed on {n} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
