#!/usr/bin/env python3
"""
apply_templates.py — Pyramid Systems static-site template applicator.

Workflow:
    1. Edit a file in /templates/  (header.html, footer.html, a11y_widget.html)
    2. Run:  python3 scripts/apply_templates.py
    3. FTP up the changed HTML files

Each page is regenerated in place: the script finds marker comments and
replaces the content between them with the template (with {{PREFIX}}
substituted to match the page's depth). Pages without markers are skipped.

Markers in pages look like:
    <!-- TEMPLATE:header:START -->
    ...existing content (will be replaced)...
    <!-- TEMPLATE:header:END -->

The script is IDEMPOTENT — running it twice produces the same result as
once. Safe to run on every commit, before every FTP upload, etc.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

# Regions handled by this script. Maps region name -> template filename.
REGIONS = {
    "a11y_widget": "a11y_widget.html",
    "header":      "header.html",
    "footer":      "footer.html",
}

# Folders whose .html files should NOT be templated
EXCLUDE_DIRS = {
    "templates",
    "scripts",
    "emails",     # transactional email HTML, different structure
    "node_modules",
    ".git",
}
# Specific files to skip (e.g. iframe pages, redirects)
EXCLUDE_FILES = {
    "preview-mocks.html",
}


def page_prefix(html_path: Path) -> str:
    """
    Compute the relative path prefix from a page's location back to site root.

    Examples (with ROOT = /pyramidConcept1):
        index.html                            -> ""
        about-us/index.html                   -> "../"
        insights/blog/foo.html                -> "../../"
        solutions/air-quire.html              -> "../"
    """
    rel = html_path.relative_to(ROOT)
    depth = len(rel.parts) - 1   # number of directories above the file
    return "../" * depth


def load_templates() -> dict[str, str]:
    """Read each template file from /templates/. Returns name -> raw text."""
    out = {}
    for name, fname in REGIONS.items():
        path = TEMPLATES_DIR / fname
        if not path.exists():
            raise FileNotFoundError(f"Missing template: {path}")
        out[name] = path.read_text(encoding="utf-8")
    return out


def find_pages(root: Path) -> list[Path]:
    """Yield every .html file under root that isn't in an excluded location."""
    pages = []
    for p in root.rglob("*.html"):
        if p.name in EXCLUDE_FILES:
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        pages.append(p)
    return sorted(pages)


# Match  <!-- TEMPLATE:name:START -->  ...anything (incl. newlines)... <!-- TEMPLATE:name:END -->
def region_pattern(name: str) -> re.Pattern:
    return re.compile(
        r"(<!--\s*TEMPLATE:"
        + re.escape(name)
        + r":START\s*-->)"
        + r"(.*?)"
        + r"(<!--\s*TEMPLATE:"
        + re.escape(name)
        + r":END\s*-->)",
        re.DOTALL,
    )


def apply_to_page(page: Path, templates: dict[str, str]) -> tuple[bool, list[str]]:
    """
    Replace every marker region on the page with the corresponding template
    (with {{PREFIX}} substituted to the page's depth). Returns (changed,
    region_names_updated).
    """
    text = page.read_text(encoding="utf-8")
    original = text
    prefix = page_prefix(page)
    updated = []

    for name, raw in templates.items():
        rendered = raw.replace("{{PREFIX}}", prefix)
        pat = region_pattern(name)
        # Ensure the rendered body sits on its own lines between the markers,
        # with no double blank lines. Strip a trailing newline if present so
        # the END marker line ends up immediately after the content.
        body = rendered.rstrip("\n")
        new_text, n = pat.subn(
            lambda m: f"{m.group(1)}\n{body}\n        {m.group(3)}",
            text,
        )
        if n > 0:
            text = new_text
            updated.append(f"{name}×{n}")

    if text != original:
        page.write_text(text, encoding="utf-8")
        return True, updated
    return False, updated


def main() -> int:
    if not TEMPLATES_DIR.is_dir():
        print(f"!! No templates directory at {TEMPLATES_DIR}", file=sys.stderr)
        return 2

    templates = load_templates()
    pages = find_pages(ROOT)
    print(f"Templates loaded: {list(templates.keys())}")
    print(f"Pages to scan:    {len(pages)}\n")

    changed_count = 0
    skipped_no_markers = 0

    for page in pages:
        rel = page.relative_to(ROOT)
        changed, updated = apply_to_page(page, templates)
        if changed:
            changed_count += 1
            print(f"  ✓ {rel}  [{', '.join(updated)}]")
        elif not updated:
            skipped_no_markers += 1

    print()
    print(f"Updated: {changed_count}")
    print(f"Unchanged (no markers, or already current): {len(pages) - changed_count}")
    print(f"No markers found at all: {skipped_no_markers}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
