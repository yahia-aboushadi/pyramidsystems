# Shared Templates

This folder holds the **single sources of truth** for site-wide content that
used to be duplicated across every HTML page. Edit a file here, run the
build script, and every page on the site updates in one shot.

## Files

| File | What it controls |
|---|---|
| `a11y_widget.html` | The accessibility widget block at the top of every `<head>` — the early-load script, the widget CSS link, and the widget JS include. |
| `header.html` | The entire `<header class="header">…</header>` block (logo, nav, dropdowns, Contact CTA, mobile menu, floating award badge). |
| `footer.html` | The entire `<footer class="footer">…</footer>` block (nav columns, contact info, social links, copyright, background watermark). |

## How it works

Each templated page on the site has comment markers around each region:

```html
<!-- TEMPLATE:header:START -->
   …rendered template…
<!-- TEMPLATE:header:END -->
```

The build script `scripts/apply_templates.py` reads each template, replaces
the `{{PREFIX}}` placeholder with the right `../` chain for the page's depth,
and writes the rendered content between the markers. Anything outside the
markers stays untouched — per-page `<title>`, meta description, OG tags,
inline animation styles, and main content all keep their individual values.

## Day-to-day workflow

1. Edit a template here (e.g. tweak nav copy in `header.html`).
2. From the project root, run:

   ```bash
   python3 scripts/apply_templates.py
   ```

3. FTP up the changed `.html` files.

That's it. Output is plain static HTML — no JS fetch, no build artifacts on
the server, no flash of unstyled content. Page load performance is identical
to hand-edited HTML.

## The `{{PREFIX}}` placeholder

Inside templates, every path that points back into the site uses
`{{PREFIX}}` instead of a relative path. The build script substitutes it
based on where each page lives:

| Page location | `{{PREFIX}}` becomes |
|---|---|
| `index.html` (root) | `` (empty) |
| `about-us/index.html` (1 deep) | `../` |
| `insights/blog/foo.html` (2 deep) | `../../` |

So `<img src="{{PREFIX}}images/logo.png">` renders as `images/logo.png` at
the root and `../../images/logo.png` inside a blog post.

## Adding markers to a new page

If you create a brand-new HTML page, paste these markers around the regions
you want templated:

```html
<!-- TEMPLATE:a11y_widget:START -->
<!-- TEMPLATE:a11y_widget:END -->
```

```html
<!-- TEMPLATE:header:START -->
<!-- TEMPLATE:header:END -->
```

```html
<!-- TEMPLATE:footer:START -->
<!-- TEMPLATE:footer:END -->
```

The content between them can be empty or stale — the build script will
overwrite it with the current template content on the next run.

## What stays per-page (not templated)

- `<title>` and the surrounding per-page `<meta>` block
- Open Graph and Twitter card tags
- `data-wf-page` and `data-wf-site` Webflow IDs
- Page-specific inline `<style>` blocks for Webflow IX animations
- The full body content between `<header>` and `<footer>`
- Any JSON-LD schema blocks

All of that lives outside the marker regions and is never touched by the
build script.
