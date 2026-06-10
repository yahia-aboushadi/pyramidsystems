#!/usr/bin/env python3
"""
generate_contract_vehicles.py — Pyramid Systems Contract Vehicles section generator.

Reads:
    /scripts/contract-vehicles-content/_hub.py            -> hub page data
    /scripts/contract-vehicles-content/<slug>.py          -> sub-page data
        (one per vehicle; the module-level DATA dict is the source of truth)

Writes:
    /contract-vehicles/index.html                         -> hub page
    /contract-vehicles/<slug>.html                        -> sub-pages

Re-runnable (idempotent) — overwrites the same files each run. Pages emit the
TEMPLATE marker comments so the existing apply_templates.py script populates
header/footer/a11y_widget. Use only existing Webflow classes; no CSS additions.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = Path(__file__).resolve().parent / "contract-vehicles-content"
OUT_DIR = ROOT / "contract-vehicles"

VEHICLE_SLUGS = [
    "gsa-it-schedule-70",
    "hhs-cms-sparc",
    "sec-one-it",
    "gsa-8a-stars-iii",
    "fdic-itas-iii",
    "hud-om-bpa",
    "gsa-oasis-plus",
]


# ----------------------------------------------------------------------------
# Loader: import a content module by file path so the filename can contain
# dashes (which Python's normal import system wouldn't allow).
# ----------------------------------------------------------------------------
def load_content(slug: str) -> dict:
    path = CONTENT_DIR / f"{slug}.py"
    if not path.exists():
        raise FileNotFoundError(f"Missing content file: {path}")
    spec = importlib.util.spec_from_file_location(f"content_{slug.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.DATA


# ----------------------------------------------------------------------------
# Shared head / boot scripts. Sub-pages are 1 level deep -> use "../" prefix.
# We keep this static (no PREFIX templating) because there's only one depth.
# apply_templates.py overwrites the header / footer / a11y_widget regions so
# we leave matching marker comments around placeholder text — actual content
# is filled in by apply_templates.
# ----------------------------------------------------------------------------
PREFIX = "../"

HEAD_TOP = """<!DOCTYPE html>
<html lang="en">
    <head>
        <!-- TEMPLATE:a11y_widget:START -->
        <!-- a11y_widget content stamped by scripts/apply_templates.py -->
        <!-- TEMPLATE:a11y_widget:END -->

        <script>document.documentElement.setAttribute("data-wf-page","68b0b16eeab74bec787faa10");document.documentElement.setAttribute("data-wf-site","67ffbeb3c6d67519154ab9f3");</script>
        <meta charset="utf-8"/>
        <title>__TITLE__</title>
        <meta content="__META_DESC__" name="description"/>
        <meta content="width=device-width, initial-scale=1" name="viewport"/>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@400;700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">

        <link href="../css/styles.css" rel="stylesheet" type="text/css" crossorigin="anonymous"/>

        <script type="text/javascript">
            !function(o, c) {
                var n = c.documentElement
                  , t = " w-mod-";
                n.className += t + "js",
                ("ontouchstart"in o || o.DocumentTouch && c instanceof DocumentTouch) && (n.className += t + "touch")
            }(window, document);
        </script>

        <style>
            html.lenis { height: auto; }
            .lenis.lenis-smooth { scroll-behavior: auto; }
            .lenis.lenis-smooth [data-lenis-prevent] { overscroll-behavior: contain; }
            .lenis.lenis-stopped { overflow: hidden; }

            /* Contract-vehicle quick-facts card.
               Mirrors the reference table styling: rounded outer container,
               distinct header strip, generous row padding, thin dividers.
               Inline-scoped to this section of the site only — no global CSS. */
            .cv-qf-card {
                background: #0d0f12;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
                overflow: hidden;
                margin-top: 1rem;
            }
            .cv-qf-head {
                padding: 18px 28px;
                background: rgba(255,255,255,0.035);
                border-bottom: 1px solid rgba(255,255,255,0.08);
                font-family: 'Funnel Display', sans-serif;
                font-weight: 700;
                font-size: 1rem;
                letter-spacing: 0.01em;
                color: #ffffff;
                text-transform: uppercase;
            }
            .cv-qf-row {
                display: grid;
                grid-template-columns: 1fr 1.6fr;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .cv-qf-row:last-child { border-bottom: 0; }
            .cv-qf-label,
            .cv-qf-value {
                padding: 22px 28px;
                font-family: 'Poppins', sans-serif;
                font-size: 0.95rem;
                line-height: 1.55;
                margin: 0;
            }
            .cv-qf-label {
                font-weight: 600;
                color: #ffffff;
                background: rgba(255,255,255,0.015);
                border-right: 1px solid rgba(255,255,255,0.05);
            }
            .cv-qf-value {
                color: rgba(255,255,255,0.6);
            }
            @media (max-width: 640px) {
                .cv-qf-row {
                    grid-template-columns: 1fr;
                }
                .cv-qf-label {
                    border-right: 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                    padding-bottom: 8px;
                }
                .cv-qf-value {
                    padding-top: 8px;
                }
                .cv-qf-label, .cv-qf-value { padding-left: 22px; padding-right: 22px; }
                .cv-qf-head { padding-left: 22px; padding-right: 22px; }
            }

            /* Contract-vehicle "How to order" plain numbered list — no cards.
               Bold lead-in title sits inline with the rest of the prose. */
            .cv-howto-list { padding-left: 1.25rem; margin: 1rem 0 0 0; }
            .cv-howto-list li { margin-bottom: 1.25rem; line-height: 1.65; }
            .cv-howto-list li strong { color: #ffffff; }

            /* Body content typography for CV sub-pages.
               styles.css zeroes out <p> margins globally (line ~2228), and
               .blogs_post-body-content carries no rules of its own. That's
               fine for blog posts where IX animations split paragraphs into
               line-animated blocks, but on CV sub-pages it leaves paragraphs
               glued together and links un-styled. We scope these rules to
               the body wrapper so they only affect the prose inside CV
               pages — no risk to any other page on the site. */
            .blogs_left-content-wrap .blogs_post-body-content p {
                margin-top: 0 !important;
                margin-bottom: 1rem !important;
                line-height: 1.65;
            }
            .blogs_left-content-wrap .blogs_post-body-content p:last-child {
                margin-bottom: 0 !important;
            }
            .blogs_left-content-wrap .blogs_post-body-content ul,
            .blogs_left-content-wrap .blogs_post-body-content ol {
                margin-top: 0;
                margin-bottom: 1.25rem;
            }
            .blogs_left-content-wrap .blogs_post-body-content li {
                margin-bottom: 0.5rem;
                line-height: 1.55;
            }
            /* Inline links inside body prose — orange to match the brand,
               underlined for affordance, smooth color transition on hover. */
            .blogs_left-content-wrap .blogs_post-body-content a {
                color: #ff7a3a;
                text-decoration: underline;
                text-decoration-color: rgba(255, 122, 58, 0.45);
                text-underline-offset: 3px;
                text-decoration-thickness: 1px;
                transition: color 0.2s ease, text-decoration-color 0.2s ease;
            }
            .blogs_left-content-wrap .blogs_post-body-content a:hover {
                color: #ff4d6d;
                text-decoration-color: rgba(255, 77, 109, 0.85);
            }
        </style>
        <!-- Finsweet Attributes -->
        <script async type="module" src="../js/attributes.js" fs-scrolldisable></script>
    </head>
    <body>
        <div class="w-embed">
            <style>
                section {
                    position: relative;
                    max-width: 100vw;
                    overflow: clip;
                    z-index: 2;
                    background-color: var(--_tokenization---bg-main);
                }

                a {
                    color: inherit;
                    text-decoration: none;
                    user-select: none;
                    transition-property: opacity, background-color, border, color, border-radius;
                    transition-timing-function: ease;
                    transition-duration: 0.45s;
                }

                button {
                    background-color: unset;
                    padding: unset;
                    text-align: inherit;
                    transition-property: opacity, background-color, border, color, border-radius;
                    transition-timing-function: ease;
                    transition-duration: 0.45s;
                }

                .arrow-animation:hover .button-arrow {
                    transform: rotate(45deg);
                }

                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .gradient-animation {
                    animation: rotate 10s ease infinite !important;
                }

                html { font-size: calc(0.625rem + 0.41666666666666663vw); }

                @media screen and (max-width: 1920px) { html { font-size: calc(0.625rem + 0.41666666666666674vw); } }
                @media screen and (max-width: 1440px) { html { font-size: calc(-0.5rem + 1.6666666666666665vw); } }
                @media screen and (max-width: 1200px) { html { font-size: calc(0.39114832535885163rem + 0.47846889952153115vw); } }
                @media screen and (max-width: 991px)  { html { font-size: calc(0.758056640625rem + 0.390625vw); } }
                @media screen and (max-width: 479px)  { html { font-size: calc(0.7494769874476988rem + 0.8368200836820083vw); } }
            </style>
        </div>

        <!-- TEMPLATE:header:START -->
        <!-- header content stamped by scripts/apply_templates.py -->
        <!-- TEMPLATE:header:END -->
"""

FOOT_BOTTOM = """        <!-- TEMPLATE:footer:START -->
        <!-- footer content stamped by scripts/apply_templates.py -->
        <!-- TEMPLATE:footer:END -->
        <script src="../js/jquery-3.5.1.min.dc5e7f18c8.js" type="text/javascript" crossorigin="anonymous"></script>
        <script src="../js/webflow.schunk.36b8fb49256177c8.js" type="text/javascript" crossorigin="anonymous"></script>
        <script src="../js/6204f98b.merged.js" type="text/javascript"></script>
        <script src="../js/gsap.min.js" type="text/javascript"></script>
        <script src="../js/ScrollTrigger.min.js" type="text/javascript"></script>
        <script src="../js/SplitText.min.js" type="text/javascript"></script>
        <script type="text/javascript">
            gsap.registerPlugin(ScrollTrigger, SplitText);
        </script>

        <script src="../js/lenis.min.js"></script>
        <script>
            // LENIS SMOOTH SCROLL
            let lenis;
            if (typeof Webflow !== 'undefined' && Webflow.env("editor") === undefined) {
                lenis = new Lenis({
                    lerp: 0.1,
                    wheelMultiplier: 0.7,
                    gestureOrientation: "vertical",
                    normalizeWheel: false,
                    smoothTouch: false
                });
                function raf(time) {
                    lenis.raf(time);
                    requestAnimationFrame(raf);
                }
                requestAnimationFrame(raf);
            }
        </script>
        <script>
            // Lines-animation (replicates the pattern used across the site)
            document.querySelectorAll('[lines-animation]').forEach(el => {
                if (typeof SplitText === 'undefined') return;
                const split = SplitText.create(el, { type: 'lines' });
                gsap.from(split.lines, {
                    scrollTrigger: { trigger: el, start: 'top 80%', toggleActions: 'play none none none' },
                    y: 80,
                    opacity: 0,
                    ease: 'power3.out',
                    duration: 0.8,
                    stagger: { each: 0.1 }
                });
            });
        </script>
        <script>
            /* -------------------------------------------------------------
             * Scroll-spy for the side menu (.blogs_menu).
             *    Ported verbatim from /insights/blog/accelerating-federal-
             *    ato-devsecops.html. As the user scrolls through the page,
             *    the link that points to the heading currently sitting near
             *    the top of the viewport gets the active class. CSS rule
             *    that styles the active state is `.blogs_link._w--current`
             *    (already in css/styles.css) — so that's the class we toggle.
             * ------------------------------------------------------------- */
            (function initBlogScrollSpy() {
                var menu = document.querySelector('.blogs_menu');
                if (!menu) return;

                var links = Array.prototype.slice.call(
                    menu.querySelectorAll('a.blogs_link[href^="#"]')
                );
                var targets = links
                    .map(function (link) {
                        var id = link.getAttribute('href').slice(1);
                        var el = id && document.getElementById(id);
                        return el ? { el: el, link: link } : null;
                    })
                    .filter(Boolean);
                if (!targets.length) return;

                function update() {
                    // Trigger line at 25% from the top of the viewport.
                    // Pick the last heading whose top has crossed that line.
                    var triggerY = window.scrollY + window.innerHeight * 0.25;
                    var active = null;
                    for (var i = 0; i < targets.length; i++) {
                        var top = targets[i].el.getBoundingClientRect().top + window.scrollY;
                        if (top <= triggerY) {
                            active = targets[i];
                        } else {
                            break;
                        }
                    }
                    for (var j = 0; j < links.length; j++) {
                        links[j].classList.remove('_w--current');
                    }
                    if (active) active.link.classList.add('_w--current');
                }

                var ticking = false;
                function onScroll() {
                    if (ticking) return;
                    ticking = true;
                    requestAnimationFrame(function () {
                        update();
                        ticking = false;
                    });
                }
                window.addEventListener('scroll', onScroll, { passive: true });
                window.addEventListener('resize', onScroll, { passive: true });
                update();
            })();
        </script>
    </body>
</html>
"""


# ----------------------------------------------------------------------------
# Hub page builder.
# ----------------------------------------------------------------------------
def build_hub(hub: dict) -> str:
    # Stat strip cells
    stat_cells = "\n".join(
        f"""                        <div class="partner-logo_wrap blog-filter_cell">
                            <div class="upheader" style="margin: 0; gap: 0.5rem;">
                                <div class="upheader_icon"><img src="../images/pyramidIconWhite.png" /></div>
                                <p style="margin: 0;"><strong style="font-size: 1.4rem;">{num}</strong> &middot; {label}</p>
                            </div>
                        </div>"""
        for num, label in hub["stat_strip"]
    )

    # Vehicle cards — using article-card pattern (same as case studies).
    cards = []
    for v in hub["vehicles"]:
        cards.append(f"""                                <div role="listitem" class="w-dyn-item">
                                    <div data-category="contract-vehicle" class="article-card_full">
                                        <div class="article-card">
                                            <div class="article-card_info-wrap">
                                                <div class="article-card_category-info">
                                                    <div class="article-card_category-title">
                                                        <div class="marquee-blog---category-date">
                                                            <p class="t--blog-category blog-category-filter">PRIME</p>
                                                            <div class="t--date">{v['agency']}</div>
                                                        </div>
                                                        <div class="t--artikel-title article-filter--name">{v['name']}</div>
                                                    </div>
                                                    <div class="article-card_desc-wrap"><p class="paragraph">{v['use_for']}</p></div>
                                                </div>
                                                <a href="{v['slug']}.html" class="button-text arrow-animation w-inline-block">
                                                    <div>View details</div>
                                                    <div class="button-arrow is--service"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none"><path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path><path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path></svg></div>
                                                </a>
                                            </div>
                                        </div>
                                        <div class="gradient-animation_wrap"><div class="gradient-animation"></div></div>
                                    </div>
                                </div>""")
    cards_html = "\n".join(cards)

    head = HEAD_TOP.replace("__TITLE__", hub["title"]).replace("__META_DESC__", hub["meta_description"])

    body = f"""        <main>
            <!-- Hero -->
            <section class="section-hero-blogs">
                <div class="w-layout-blockcontainer container w-container">
                    <div class="blogs_hero-content-wrap">
                        <div class="blogs_hero-content">
                            <div class="blogs_hero-texts-wrap">
                                <div class="blogs_hero-titles-wrap">
                                    <div class="upheader">
                                        <div class="upheader_icon">
                                            <img src="../images/pyramidIconWhite.png" />
                                        </div>
                                        <p class="paragraph-3">{hub['upheader']}</p>
                                    </div>
                                    <h1 lines-animation="" class="h1-blogs">{hub['hero_h1']}</h1>
                                    <div class="hero_subheader">
                                        <p lines-animation=""><span class="subheader-white">{hub['hero_subhead']}</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="blogs_hero-figure-wrap-bg">
                            <img src="../images/wf/6878c0c361ff85992a2d05a1_bg.avif" loading="eager" alt="" class="i-100"/>
                        </div>
                        <div class="cta_gradient-wrap">
                            <img src="../images/cta_gradient_transparent.png" loading="lazy" alt="" class="i-100"/>
                        </div>
                        <div class="cta-dots is--2">
                            <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                        </div>
                        <div class="cta-dots">
                            <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Stat strip -->
            <section class="blog-filter-section">
                <div class="w-layout-blockcontainer container w-container">
                    <div class="partner-logos_block-wrap blog-filter_block-wrap">
                        <div class="partner-logos_wrap blog-filter_logos-wrap">
                            <div class="partner-logos_wrapper">
                                <div class="partner-logos_inner-wrap blog-filter_inner-wrap">
{stat_cells}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Vehicle cards grid -->
            <section id="vehicles">
                <div class="w-layout-blockcontainer container w-container">
                    <div class="blog_articles-block">
                        <div class="w-dyn-list">
                            <div role="list" class="articles-wrap w-dyn-items">
{cards_html}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Contracts team contact card -->
            <section>
                <div class="w-layout-blockcontainer container w-container">
                    <div class="blog-cta_content-block">
                        <div class="cta_content-wrap">
                            <div class="cta_content is--blog">
                                <div class="cta_texts-wrap">
                                    <div class="cta_titles-wrap">
                                        <div class="upheader">
                                            <div class="upheader_icon"><img src="../images/pyramidIconWhite.png" /></div>
                                            <p lines-animation="">Pyramid contracts team</p>
                                        </div>
                                        <h2 lines-animation="">Procure us in one email.</h2>
                                    </div>
                                    <p lines-animation="" class="t--cta-text is--blog">
                                        E-mail your statement of work to <span class="subheader-white">{hub['contracts_email']}</span> &mdash; our Contracts team will route to the right ordering officer and respond promptly.
                                    </p>
                                    <div class="cta-form_input-button">
                                        <a href="mailto:{hub['contracts_email']}" class="button arrow-animation is--form">
                                            <div class="button_inner-wrap is--white is--form">
                                                <div>Email {hub['contracts_email']}</div>
                                                <div class="button-arrow is--main">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                        <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                        <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                                    </svg>
                                                </div>
                                            </div>
                                        </a>
                                        <a href="{hub['contracts_phone_href']}" class="button-text arrow-animation w-inline-block" style="margin-left: 1rem;">
                                            <div>or call {hub['contracts_phone']}</div>
                                            <div class="button-arrow is--service"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none"><path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path><path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path></svg></div>
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div class="cta_gradient-wrap">
                                <img src="../images/cta_gradient_transparent.png" loading="lazy" alt="" class="i-100"/>
                            </div>
                            <div class="cta-dots is--2">
                                <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                            </div>
                            <div class="cta-dots">
                                <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Final CTA: teaming -->
            <section>
                <div class="w-layout-blockcontainer container w-container">
                    <div class="sea-seo-content-block">
                        <div class="cases_text-button is--social-inner">
                            <div class="cases_texts-wrap">
                                <div class="upheader">
                                    <div class="upheader_icon"><img src="../images/pyramidIconWhite.png" /></div>
                                    <p lines-animation="">Don&rsquo;t see your vehicle?</p>
                                </div>
                                <h2 lines-animation="">Let&rsquo;s talk about <span class="text-gradient">teaming arrangements</span>.</h2>
                                <p lines-animation="" class="t--result-subheading">Pyramid teams with both small and large primes on the right vehicle for each agency &mdash; bring the work, we&rsquo;ll find the path.</p>
                                <a href="../coming-soon.html" class="button arrow-animation w-inline-block">
                                    <div class="button_inner-wrap">
                                        <div>Get in touch</div>
                                        <div class="button-arrow is--main">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                            </svg>
                                        </div>
                                    </div>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
"""

    return head + body + FOOT_BOTTOM


# ----------------------------------------------------------------------------
# Sub-page builder.
# ----------------------------------------------------------------------------
def build_subpage(v: dict, hub: dict) -> str:
    # Quick-facts card — rounded container, distinct header strip, 2-column rows
    # with thin dividers (matches the table design reference).
    qf_rows = "\n".join(
        f"""                                    <div class="cv-qf-row">
                                        <div class="cv-qf-label">{label}</div>
                                        <div class="cv-qf-value">{value}</div>
                                    </div>"""
        for label, value in v["quick_facts"]
    )

    # What you can buy list items
    buy_items = "\n".join(f"                                    <li>{item}</li>" for item in v["what_you_can_buy"])

    # How-to-order — plain numbered list with bold lead-in titles (no cards).
    steps = []
    for step in v["how_to_order"]:
        steps.append(
            f"                                    <li><strong>{step['title']}.</strong> {step['body']}</li>"
        )
    steps_html = "\n".join(steps)

    # About paragraphs
    about_html = "\n".join(f"                                <p>{para}</p>" for para in v["about_paragraphs"])

    # Extra source-content sections (optional, for vehicles like CMS SPARC).
    extra_html_parts = []
    nav_extra_links = []
    for sec in v.get("extra_sections", []) or []:
        sec_id = sec["id"]
        heading = sec["heading"]
        nav_extra_links.append(
            f'                                        <a href="#{sec_id}" class="blogs_link w-inline-block"><div>{heading}</div></a>'
        )
        body_paras = "\n".join(f"                                <p>{p}</p>" for p in sec.get("paragraphs", []))
        bullets = sec.get("bullets") or []
        bullets_html = ""
        if bullets:
            items = "\n".join(f"                                    <li>{b}</li>" for b in bullets)
            bullets_html = f"\n                                <ul>\n{items}\n                                </ul>"
        trailing = "\n".join(f"                                <p>{p}</p>" for p in sec.get("trailing_paragraphs", []))
        section_block = (
            f'\n                            <h2 id="{sec_id}" class="h2-blogs">{heading}</h2>\n'
            f'                            <div class="blogs_post-body-content">\n'
            f'{body_paras}'
            f'{bullets_html}\n'
            f'{trailing}\n'
            f'                            </div>'
        )
        extra_html_parts.append(section_block)
    extra_sections_html = "".join(extra_html_parts)
    extra_nav_html = "\n".join(nav_extra_links)

    # Capability statement sidebar card (only for vehicles that have one).
    cap_pdf_url = hub.get("capability_pdf_url", "#")
    if v.get("has_capability_statement"):
        capability_card_html = f"""                            <div class="blogs_baner-content-wrap">
                                <div class="blogs_baner-content">
                                    <div class="blogs_hero-texts-wrap">
                                        <div class="upheader text--white">
                                            <div class="upheader_icon">
                                                <img src="../images/pyramidIconWhite.png" />
                                            </div>
                                            <p lines-animation="">Capability statement</p>
                                        </div>
                                        <h5 lines-animation="" class="h5-white">Download the Pyramid Systems federal capability statement (PDF).</h5>
                                        <a href="{cap_pdf_url}" class="button arrow-animation w-inline-block">
                                            <div class="button_inner-wrap is--white">
                                                <div>Download PDF</div>
                                                <div class="button-arrow is--main">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                        <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                        <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                                    </svg>
                                                </div>
                                            </div>
                                        </a>
                                    </div>
                                </div>
                                <div class="cta_gradient-wrap">
                                    <img src="../images/cta_gradient_transparent.png" loading="lazy" alt="" class="i-100"/>
                                </div>
                                <div class="cta-dots is--2">
                                    <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                                </div>
                                <div class="cta-dots">
                                    <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                                </div>
                            </div>"""
    else:
        capability_card_html = ""

    head = HEAD_TOP.replace("__TITLE__", v["title"]).replace("__META_DESC__", v["meta_description"])

    body = f"""        <main>
            <!-- Hero -->
            <section class="section-hero-blogs">
                <div class="w-layout-blockcontainer container w-container">
                    <div class="blogs_hero-content-wrap">
                        <div class="blogs_hero-content">
                            <div class="blogs_hero-texts-wrap">
                                <div class="blogs_hero-titles-wrap">
                                    <div class="upheader">
                                        <div class="upheader_icon">
                                            <img src="../images/pyramidIconWhite.png" />
                                        </div>
                                        <p class="paragraph-3">{v['upheader']}</p>
                                    </div>
                                    <h1 lines-animation="" class="h1-blogs">{v['vehicle_short']} <span class="text-gradient">PRIME</span></h1>
                                    <div class="hero_subheader">
                                        <p lines-animation=""><span class="subheader-white">{v['hero_positioning']}</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="blogs_hero-figure-wrap-bg">
                            <img src="../images/wf/6878c0c361ff85992a2d05a1_bg.avif" loading="eager" alt="" class="i-100"/>
                        </div>
                        <div class="cta_gradient-wrap">
                            <img src="../images/cta_gradient_transparent.png" loading="lazy" alt="" class="i-100"/>
                        </div>
                        <div class="cta-dots is--2">
                            <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                        </div>
                        <div class="cta-dots">
                            <img src="../images/wf/680359143d96b2fa3c7c23a1_dots 3.avif" loading="lazy" alt="" class="i-100"/>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Body: 2-column layout (left content, right sticky sidebar) -->
            <section>
                <div class="w-layout-blockcontainer container w-container">
                    <div class="blogs_wrap">
                        <div class="blogs_left-content-wrap">

                            <!-- Quick facts table -->
                            <h2 id="quick-facts" class="h2-blogs">Quick facts</h2>
                            <div class="blogs_post-body-content">
                                <div class="cv-qf-card">
                                    <div class="cv-qf-head">Contract details</div>
{qf_rows}
                                </div>
                            </div>

                            <!-- What You Can Buy -->
                            <h2 id="what-you-can-buy" class="h2-blogs">What you can buy</h2>
                            <div class="blogs_post-body-content">
                                <ul>
{buy_items}
                                </ul>
                            </div>

                            <!-- How to Order -->
                            <h2 id="how-to-order" class="h2-blogs">How to order</h2>
                            <div class="blogs_post-body-content">
                                <ol class="cv-howto-list">
{steps_html}
                                </ol>
                            </div>

                            <!-- About -->
                            <h2 id="about" class="h2-blogs">About this vehicle</h2>
                            <div class="blogs_post-body-content">
{about_html}
                            </div>
{extra_sections_html}

                            <!-- Back to hub -->
                            <div class="blogs_post-body-content" style="margin-top: 2rem;">
                                <a href="index.html" class="button-text arrow-animation w-inline-block">
                                    <div>&larr; Back to all vehicles</div>
                                </a>
                            </div>
                        </div>

                        <!-- Sticky sidebar: contents + capability-statement card -->
                        <div class="blogs_right-content-wrap">
                            <div class="social-card_wrapp-gradient">
                                <div class="blogs_menu-wrap">
                                    <h5 class="h5-white">On this page</h5>
                                    <div class="blogs_menu">
                                        <a href="#quick-facts" class="blogs_link w-inline-block"><div>Quick facts</div></a>
                                        <a href="#what-you-can-buy" class="blogs_link w-inline-block"><div>What you can buy</div></a>
                                        <a href="#how-to-order" class="blogs_link w-inline-block"><div>How to order</div></a>
                                        <a href="#about" class="blogs_link w-inline-block"><div>About this vehicle</div></a>
{extra_nav_html}
                                    </div>
                                </div>
                                <div class="gradient-animation_wrap">
                                    <div class="gradient-animation"></div>
                                </div>
                            </div>
{capability_card_html}
                            <div class="hero-dots is--4 blogs">
                                <img src="../images/wf/680359144aaf391f45e21aec_dots 4.avif" loading="eager" width="286" height="163" alt="" class="i-100"/>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
"""

    return head + body + FOOT_BOTTOM


# ----------------------------------------------------------------------------
# Main.
# ----------------------------------------------------------------------------
def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Hub
    hub_data = load_content("_hub")
    hub_html = build_hub(hub_data)
    hub_path = OUT_DIR / "index.html"
    hub_path.write_text(hub_html, encoding="utf-8")
    print(f"  wrote {hub_path.relative_to(ROOT)}")

    # Sub-pages
    for slug in VEHICLE_SLUGS:
        v_data = load_content(slug)
        sub_html = build_subpage(v_data, hub_data)
        sub_path = OUT_DIR / f"{slug}.html"
        sub_path.write_text(sub_html, encoding="utf-8")
        print(f"  wrote {sub_path.relative_to(ROOT)}")

    print(f"\nGenerated {1 + len(VEHICLE_SLUGS)} pages under {OUT_DIR.relative_to(ROOT)}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
