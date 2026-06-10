"""
Generate SEO-optimized services placeholder pages.

Each page is a minimal-but-correct HTML stub with:
  - SEO title + meta description + canonical
  - OpenGraph + Twitter card meta
  - JSON-LD Service + BreadcrumbList schema
  - Visible H1 with target keyword + gradient subhead
  - Brief intro paragraph using target keywords
  - Breadcrumb nav + internal links to existing content (case studies, CV, about)
  - Template markers (TEMPLATE:a11y_widget, TEMPLATE:header, TEMPLATE:footer)
    so apply_templates.py stamps in the shared chrome on next run.

This establishes the URL structure (`/services/{slug}.html` matching the existing
`/contract-vehicles/{slug}.html` pattern) so the dropdown can point at real pages
that crawl, index, and rank — even before deep content is written.
"""

from pathlib import Path

# Resolve project root from this script's location so it works regardless of
# which environment (macOS host or Linux sandbox) is running the script.
ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"

SITE_BASE_URL = "https://pyramidsystems.com"

# 5 services + 1 hub, ordered as they appear in the nav
SERVICES = [
    {
        "slug": "modernization",
        "nav_label": "Modernization",
        "h1_main": "Federal IT Modernization",
        "h1_gradient": "Built to Ship",
        "title": "Federal IT Modernization Services | Pyramid Systems",
        "meta_description": "Federal IT modernization from a 30-year partner to HUD, SEC, CMS, USDA, FDIC, USCIS. Legacy system replacement, low-code, cloud, production-ready delivery.",
        "intro": "Replace legacy systems without breaking the mission. Pyramid Systems has modernized federal IT for civilian agencies for three decades — combining cloud-native architecture, low-code platforms, and agile delivery to ship production software on schedule and under audit.",
        "keywords": ["federal IT modernization", "legacy system modernization", "government IT modernization", "mission-critical software", "federal systems modernization"],
        "schema_keywords": "federal IT modernization, legacy modernization, government IT, mission systems",
    },
    {
        "slug": "cloud",
        "nav_label": "Cloud",
        "h1_main": "Federal Cloud Services",
        "h1_gradient": "FedRAMP-Ready",
        "title": "Federal Cloud Services & Migration | Pyramid Systems",
        "meta_description": "Federal cloud migration and operations. AWS, Azure, GCP for civilian agencies. FedRAMP-aware, FISMA-aligned. AWS Government Competency partner. 30 years federal IT.",
        "intro": "Move federal workloads to AWS, Azure, or Google Cloud with a partner that has earned the AWS Government Competency and delivered cloud modernization at HUD, SEC, CMS, and USDA. FedRAMP-aware, FISMA-aligned, mission-tested.",
        "keywords": ["federal cloud services", "federal cloud migration", "AWS GovCloud", "FedRAMP cloud", "federal cloud modernization"],
        "schema_keywords": "federal cloud, FedRAMP, AWS GovCloud, government cloud migration",
    },
    {
        "slug": "cybersecurity",
        "nav_label": "Cybersecurity",
        "h1_main": "Federal Cybersecurity",
        "h1_gradient": "Built to Withstand",
        "title": "Federal Cybersecurity Services | Pyramid Systems",
        "meta_description": "Federal cybersecurity from a CMMI-DEV / CMMI-SVC Level 3 contractor. Zero trust architecture, ATO acceleration, continuous monitoring, ICAM for civilian agencies.",
        "intro": "Zero-trust architecture, ATO acceleration, continuous monitoring, and identity, credential, and access management for federal civilian agencies. Pyramid Systems is independently appraised at CMMI-DEV and CMMI-SVC Maturity Level 3 — verified by external evaluators, not just claimed in marketing.",
        "keywords": ["federal cybersecurity services", "federal cybersecurity contractor", "zero trust federal", "federal ATO", "federal ICAM"],
        "schema_keywords": "federal cybersecurity, zero trust, ATO, ICAM, continuous monitoring",
    },
    {
        "slug": "devsecops",
        "nav_label": "DevSecOps",
        "h1_main": "Federal DevSecOps",
        "h1_gradient": "Secure by Default",
        "title": "Federal DevSecOps Services | Pyramid Systems",
        "meta_description": "Federal DevSecOps. Secure CI/CD pipelines, automated compliance, accelerated ATO. Production-tested at HUD, SEC, and CMS. 30 years modernizing federal IT delivery.",
        "intro": "CI/CD pipelines with security woven in from commit to production. Pyramid Systems has built federal DevSecOps practices that accelerate delivery without compromising compliance — at HUD, SEC, CMS, and across the AWS Government Competency program.",
        "keywords": ["federal DevSecOps", "government DevSecOps", "secure CI/CD", "automated compliance", "ATO automation"],
        "schema_keywords": "federal DevSecOps, secure CI/CD, government delivery, automated compliance",
    },
    {
        "slug": "analytics-ai",
        "nav_label": "Analytics & AI",
        "h1_main": "Federal Analytics & AI",
        "h1_gradient": "Mission Intelligence",
        "title": "Federal Analytics & AI Services | Pyramid Systems",
        "meta_description": "Federal analytics and AI for civilian agencies. Decision support, predictive analytics, federally-compliant AI aligned to federal AI executive orders and OMB AI memo guidance.",
        "intro": "Decision support systems, predictive analytics, and federally-compliant AI for civilian agencies. Aligned to the latest federal AI executive orders and OMB AI memo guidance — production deployable, audit-ready, mission-focused.",
        "keywords": ["federal analytics services", "federal AI services", "federal data analytics", "government AI", "predictive analytics federal"],
        "schema_keywords": "federal analytics, federal AI, government data, predictive analytics",
    },
]

HUB = {
    "slug": "index",
    "nav_label": "Services",
    "h1_main": "Federal IT Services",
    "h1_gradient": "Delivered for 30 Years",
    "title": "Federal IT Services | Pyramid Systems",
    "meta_description": "Pyramid Systems federal IT services — Modernization, Cloud, Cybersecurity, DevSecOps, Analytics & AI. 30 years of mission-critical delivery for HUD, SEC, CMS, USDA, FDIC, USCIS.",
    "intro": "Modernization, Cloud, Cybersecurity, DevSecOps, and Analytics & AI for federal civilian agencies. Thirty years of production-ready delivery for HUD, SEC, CMS, USDA, FDIC, and USCIS. Independently appraised at CMMI-DEV and CMMI-SVC Maturity Level 3.",
    "keywords": ["federal IT services", "federal IT contractor", "government IT services", "federal civilian IT"],
    "schema_keywords": "federal IT services, government IT, federal modernization",
}


def page_html(service: dict, is_hub: bool = False) -> str:
    """Build the page HTML for one service or the hub."""
    slug = service["slug"]
    file_name = "index.html" if is_hub else f"{slug}.html"
    canonical = f"{SITE_BASE_URL}/services/{file_name}"

    title = service["title"]
    desc = service["meta_description"]
    h1_main = service["h1_main"]
    h1_grad = service["h1_gradient"]
    intro = service["intro"]
    nav_label = service["nav_label"]

    # Breadcrumb structured data
    if is_hub:
        breadcrumb_items = """
        {"@type":"ListItem","position":1,"name":"Home","item":"https://pyramidsystems.com/"},
        {"@type":"ListItem","position":2,"name":"Services","item":"https://pyramidsystems.com/services/index.html"}"""
        breadcrumb_html = """
                <a href="../index.html">Home</a>
                <span aria-hidden="true">/</span>
                <span aria-current="page">Services</span>"""
        schema_type = "CollectionPage"
    else:
        breadcrumb_items = f"""
        {{"@type":"ListItem","position":1,"name":"Home","item":"https://pyramidsystems.com/"}},
        {{"@type":"ListItem","position":2,"name":"Services","item":"https://pyramidsystems.com/services/index.html"}},
        {{"@type":"ListItem","position":3,"name":"{nav_label}","item":"{canonical}"}}"""
        breadcrumb_html = f"""
                <a href="../index.html">Home</a>
                <span aria-hidden="true">/</span>
                <a href="index.html">Services</a>
                <span aria-hidden="true">/</span>
                <span aria-current="page">{nav_label}</span>"""
        schema_type = "Service"

    # Hub-specific: list of all services with cards
    if is_hub:
        cards_html = '\n                <ul class="services-hub-list" style="list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1.5rem;margin-top:3rem;">\n'
        for s in SERVICES:
            cards_html += f"""                    <li>
                        <a href="{s['slug']}.html" style="display:block;padding:1.5rem;border:1px solid rgba(255,255,255,0.1);border-radius:1rem;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s;" onmouseover="this.style.borderColor='#E86222';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.transform='none'">
                            <h2 style="font-size:1.25rem;margin:0 0 .5rem 0;">{s['h1_main']}</h2>
                            <p style="margin:0;color:rgba(255,255,255,0.7);font-size:.9rem;">{s['intro'][:140].rsplit(' ', 1)[0]}…</p>
                        </a>
                    </li>
"""
        cards_html += "                </ul>\n"
        related_html = cards_html
    else:
        # Service-page: list related case studies + contract vehicles
        related_html = """
                <h2 style="margin-top:3rem;">Related at Pyramid</h2>
                <ul style="list-style:none;padding:0;">
                    <li style="margin:.5rem 0;">
                        <a href="../insights/case-studies/index.html">Case Studies</a> — federal delivery examples across agencies
                    </li>
                    <li style="margin:.5rem 0;">
                        <a href="../contract-vehicles/index.html">Contract Vehicles</a> — how to procure Pyramid services
                    </li>
                    <li style="margin:.5rem 0;">
                        <a href="../about-us/index.html">About Pyramid</a> — 30 years of federal IT
                    </li>
                    <li style="margin:.5rem 0;">
                        <a href="index.html">All Services</a> — browse the full portfolio
                    </li>
                </ul>
"""

    # JSON-LD schema (Service + BreadcrumbList)
    schema_block = f"""        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "{schema_type}",
            "name": "{h1_main}",
            "description": "{desc}",
            "url": "{canonical}",
            "provider": {{
                "@type": "Organization",
                "name": "Pyramid Systems",
                "url": "{SITE_BASE_URL}/",
                "logo": "{SITE_BASE_URL}/images/orangeLogo.png"
            }},
            "areaServed": {{
                "@type": "Country",
                "name": "United States"
            }},
            "audience": {{
                "@type": "Audience",
                "audienceType": "Federal civilian agencies"
            }},
            "keywords": "{service['schema_keywords']}"
        }}
        </script>
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [{breadcrumb_items}
            ]
        }}
        </script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <!-- TEMPLATE:a11y_widget:START -->
        <!-- Pyramid Systems accessibility widget — custom replacement for UserWay -->
        <link rel="stylesheet" href="../css/pyramid-a11y.css">
        <script>
          (function () {{
            try {{
              var s = JSON.parse(localStorage.getItem('pyramid-a11y-settings') || '{{}}');
              var c = document.documentElement.classList;
              Object.keys(s).forEach(function (k) {{
                var v = s[k];
                if (!v) return;
                if (k === 'oversized') c.add('pa11y-oversized');
                else if (typeof v === 'string') c.add('pa11y-' + k + '-' + v);
                else c.add('pa11y-' + k);
              }});
            }} catch (e) {{}}
          }})();
        </script>
        <script src="../js/pyramid-a11y.js" defer></script>
        <!-- TEMPLATE:a11y_widget:END -->

        <meta charset="utf-8"/>
        <title>{title}</title>
        <meta content="{desc}" name="description"/>
        <link rel="canonical" href="{canonical}"/>
        <meta content="width=device-width, initial-scale=1" name="viewport"/>

        <!-- OpenGraph -->
        <meta property="og:title" content="{title}"/>
        <meta property="og:description" content="{desc}"/>
        <meta property="og:url" content="{canonical}"/>
        <meta property="og:type" content="website"/>
        <meta property="og:site_name" content="Pyramid Systems"/>
        <!-- Twitter -->
        <meta name="twitter:card" content="summary_large_image"/>
        <meta name="twitter:title" content="{title}"/>
        <meta name="twitter:description" content="{desc}"/>

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@400;700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <link href="../css/styles.css" rel="stylesheet" type="text/css" crossorigin="anonymous"/>

        <style>
            /* Page-scoped styles for services placeholder pages. */
            .services-page-main {{
                padding: 8rem 1.5rem 4rem;
                max-width: 60rem;
                margin: 0 auto;
                color: var(--_tokenization---text-gray, #f4f5f9);
            }}
            .services-breadcrumb {{
                display: flex;
                gap: .5rem;
                font-size: .875rem;
                color: rgba(255,255,255,0.6);
                margin-bottom: 2rem;
            }}
            .services-breadcrumb a {{
                color: inherit;
                text-decoration: none;
            }}
            .services-breadcrumb a:hover {{
                color: #E86222;
            }}
            .services-breadcrumb [aria-current] {{
                color: #fff;
            }}
            .services-page-main h1 {{
                font-size: clamp(2.25rem, 5vw, 3.5rem);
                line-height: 1.1;
                margin: 0 0 1rem;
            }}
            .services-page-main h1 .text-gradient {{
                display: block;
            }}
            .services-page-main .lede {{
                font-size: 1.125rem;
                line-height: 1.6;
                color: rgba(255,255,255,0.8);
                margin: 0 0 2rem;
                max-width: 50rem;
            }}
            .services-page-main h2 {{
                font-size: 1.5rem;
                margin: 3rem 0 1rem;
            }}
            .services-page-main a {{
                color: #E86222;
                text-decoration: underline;
                text-underline-offset: 3px;
                text-decoration-thickness: 1px;
            }}
            .services-page-main a:hover {{
                text-decoration-thickness: 2px;
            }}
            .services-placeholder-note {{
                padding: 1.5rem;
                border: 1px dashed rgba(255,255,255,0.18);
                border-radius: .75rem;
                background: rgba(255,255,255,0.02);
                margin: 2rem 0;
                font-size: .95rem;
                color: rgba(255,255,255,0.7);
            }}
            .services-cta-button {{
                display: inline-flex;
                align-items: center;
                gap: .5rem;
                padding: .875rem 1.5rem;
                background: #E86222;
                color: #fff !important;
                text-decoration: none !important;
                border-radius: .5rem;
                font-weight: 600;
                margin-top: 1rem;
                transition: background .2s ease, transform .15s ease;
            }}
            .services-cta-button:hover {{
                background: #c9531c;
                transform: translateY(-1px);
            }}
        </style>

{schema_block}
    </head>
    <body>
        <!-- TEMPLATE:header:START -->
        <!-- placeholder — apply_templates.py stamps the real header here -->
        <!-- TEMPLATE:header:END -->

        <main class="services-page-main">
            <nav aria-label="Breadcrumb" class="services-breadcrumb">{breadcrumb_html}
            </nav>

            <h1>
                <span>{h1_main}</span>
                <span class="text-gradient">{h1_grad}</span>
            </h1>

            <p class="lede">{intro}</p>

            <div class="services-placeholder-note">
                <strong>This page is in development.</strong> Detailed capabilities, agency past performance, and case studies specific to {h1_main.lower()} are being added. In the meantime, the links below cover what's available today.
            </div>

            <a href="../coming-soon.html" class="services-cta-button">
                Contact the {nav_label} team
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 14 14" fill="none">
                    <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.4" stroke-linecap="square" stroke-linejoin="round"/>
                    <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.4" stroke-linecap="square" stroke-linejoin="bevel"/>
                </svg>
            </a>

{related_html}
        </main>

        <!-- TEMPLATE:footer:START -->
        <!-- placeholder — apply_templates.py stamps the real footer here -->
        <!-- TEMPLATE:footer:END -->
    </body>
</html>
"""


def main():
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)

    # Hub page
    hub_path = SERVICES_DIR / "index.html"
    hub_path.write_text(page_html(HUB, is_hub=True), encoding="utf-8")
    print(f"  ✓ services/index.html  (hub)")

    # Detail pages
    for s in SERVICES:
        path = SERVICES_DIR / f"{s['slug']}.html"
        path.write_text(page_html(s, is_hub=False), encoding="utf-8")
        print(f"  ✓ services/{s['slug']}.html")

    print(f"\nGenerated {1 + len(SERVICES)} services pages. Run scripts/apply_templates.py to stamp shared header/footer.")


if __name__ == "__main__":
    main()
