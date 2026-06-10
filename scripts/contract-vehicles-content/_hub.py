# Contract Vehicles hub page content.
# Used by scripts/generate_contract_vehicles.py to stamp /contract-vehicles/index.html.

DATA = {
    "slug": "_hub",
    "title": "Contract Vehicles | Pyramid Systems",
    "meta_description": (
        "Pyramid Systems holds seven prime federal contract vehicles — "
        "GSA IT Schedule 70, GSA OASIS+ Unrestricted, HHS CMS SPARC, "
        "SEC ONE IT, GSA 8(a) STARS III, FDIC ITAS III Next Gen BOA, and the HUD O&M BPA. "
        "30 years of mission-critical federal delivery."
    ),
    "upheader": "How to procure us",
    "hero_h1": "Contract Vehicles",
    "hero_subhead": (
        "Seven prime vehicles. One trusted partner. "
        "30 years of mission-critical federal delivery."
    ),
    "stat_strip": [
        ("7", "PRIME VEHICLES"),
        ("30", "YEARS DELIVERING"),
    ],
    "vehicles": [
        {
            "slug": "gsa-it-schedule-70",
            "name": "GSA IT Schedule 70",
            "agency": "General Services Administration (GSA)",
            "use_for": "Federal IT products, cloud services, and IT professional services across civilian and defense agencies.",
        },
        {
            "slug": "gsa-oasis-plus",
            "name": "GSA OASIS+ Unrestricted",
            "agency": "General Services Administration (GSA)",
            "use_for": "Governmentwide multi-award services contract — management/advisory and technical/engineering services.",
        },
        {
            "slug": "hhs-cms-sparc",
            "name": "HHS CMS SPARC",
            "agency": "HHS / Centers for Medicare & Medicaid Services",
            "use_for": "Healthcare IT services at CMS — the full software lifecycle from concept through maintenance.",
        },
        {
            "slug": "sec-one-it",
            "name": "SEC ONE IT",
            "agency": "U.S. Securities and Exchange Commission",
            "use_for": "Streamlined SEC IT procurement across seven service channels — application development through TBM.",
        },
        {
            "slug": "gsa-8a-stars-iii",
            "name": "GSA 8(a) STARS III",
            "agency": "General Services Administration (GSA)",
            "use_for": "Small-business set-aside GWAC for customized IT solutions — federal, state, and local government.",
        },
        {
            "slug": "fdic-itas-iii",
            "name": "FDIC ITAS III Next Gen BOA",
            "agency": "Federal Deposit Insurance Corporation (FDIC)",
            "use_for": "Full IT application lifecycle support at the FDIC — modernization, cloud migration, ML/AI, and sustainment.",
        },
        {
            "slug": "hud-om-bpa",
            "name": "HUD O&M BPA",
            "agency": "U.S. Department of Housing and Urban Development",
            "use_for": "HUD OCIO operations and maintenance — program management, modernization, and transition support.",
        },
    ],
    "contracts_email": "contracts@pyramidsystems.com",
    "contracts_phone": "703.553.0800",
    "contracts_phone_href": "tel:+17035530800",
    # Placeholder until the actual PDF is uploaded; swap to the real URL here.
    # Originally tracked as {{CAPABILITY_PDF_URL}}.
    "capability_pdf_url": "#",
}
