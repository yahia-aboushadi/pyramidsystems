#!/usr/bin/env python3
"""
build_service_pages.py - Build the 5 Pyramid federal IT service pages.

Generates:
    services/modernization.html
    services/cloud.html
    services/cybersecurity.html
    services/analytics-ai.html
    services/devsecops.html

Each page:
  - Full Pyramid head (Poppins fonts, JSON-LD Service + FAQPage, canonical, OG, Twitter)
  - Templated regions (a11y_widget, consent, attribution, ac_tracking, header, footer)
  - Glossar-style 2-col layout: breadcrumbs, tag, H1, lead, body, FAQ + sticky orange CTA
  - "Other services" grid (links to the OTHER 4 services)
  - Embedded contact form (copied verbatim from services/index.html lines 2881-3311)
  - Site-wide popup-leave (exit-intent) + popup-magnet (sticky bottom-left) wired to AC
  - Site standard scripts (jQuery, Webflow, GSAP, Lenis, Swiper, Finsweet, proof-stats)

Run: python3 scripts/build_service_pages.py
Then: python3 scripts/apply_templates.py
"""
from __future__ import annotations
from pathlib import Path
import html as html_lib

ROOT = Path(__file__).resolve().parent.parent
# The contact form was previously slurped from services/index.html lines 2881-3311
# and stamped into every service page. That dragged in the "Continuous improvement"
# placeholder, the broken contact-form section, and orphan markup (aq-form-fed-item,
# process-card_texts-wrap). Service pages now use the bottom CTA module exclusively;
# users click "Talk to our team" to reach /contact/ for the dedicated form.
CONTACT_FORM_SECTION = ""


# Service catalog. For each service, the slug is its filename, the rest
# is the per-page content the user dictated verbatim.
SERVICES = [
    {
        "slug": "modernization",
        "name": "Modernization",
        "h1_main": "Modernization",
        "tag": "Modernization Services",
        "title": "Modernization Services | Pyramid Systems",
        "meta_desc": "Replace legacy mainframe, Oracle, and SharePoint systems without breaking the mission. Pyramid modernizes systems federal agencies depend on, and regulated enterprises that demand the same rigor. 30 years of production delivery.",
        "service_type": "IT modernization, legacy system replacement, mainframe and Oracle migration",
        "cta_h2": "Ready to replace a legacy system without breaking the mission?",
        "lead": "Replace legacy systems without breaking the mission. Pyramid retires mainframe, Oracle Fusion, and SharePoint workloads on a published increment schedule, keeps the existing ATO boundary or audit constraints intact during cutover, and ships the same engineers from year one through year five. Built originally for federal mission systems, equally rigorous for regulated commercial platforms.",
        "body_sections": [
            {
                "h2": "What we do",
                "items": [
                    "Enterprise Modernization Strategy and Planning",
                    "Architecture, Engineering, and Prototyping",
                    "Agile Development and Implementation",
                    "Cloud Migration and Transition",
                    "Mainframe, SharePoint, Oracle Fusion Middleware, and Legacy System Modernization",
                ],
            },
            {
                "h2": "How we deliver",
                "items": [
                    "Scrum, Kanban, SAFe, and DevSecOps",
                    "Agile engineering with TDD and test automation",
                    "UX design and usability engineering",
                    "CI/CD pipelines for federal environments",
                ],
            },
            {
                "h2": "Outcomes we ship",
                "items": [
                    "Intuitive applications federal staff actually use",
                    "Secure, scalable, optimized processes",
                    "Decreased total cost of ownership",
                    "Elevated mission capabilities",
                ],
            },
        ],
        "anchor_p": 'Production proof. The <a href="../solutions/air-quire.html">HUD AMSS</a> acquisition platform is live in production at HUD. For another federal agency, we cut mortgage claims processing from <a href="../insights/case-studies/index.html">17 months to 17 minutes</a>, documented and verifiable. Production-tested across <a href="../insights/case-studies/index.html">HUD, SEC, CMS, USDA, FDIC, and USCIS</a>.',
        "faqs": [
            {
                "q": "How long does a federal modernization engagement typically take?",
                "a": "Most modernization engagements run 12 to 36 months, depending on system complexity and ATO scope. We deliver in production increments every 2 to 4 weeks so value lands before the full program closes out, not just at the end.",
            },
            {
                "q": "Can you modernize systems that need to maintain their ATO?",
                "a": "Yes. Every modernization track we run is ATO-aware from day one. We work alongside your ISSM and authorizing official, generate continuous compliance evidence in the pipeline, and stage changes so existing ATO boundaries are respected throughout the rollout.",
            },
            {
                "q": "What is your approach to migrating legacy mainframe or Oracle systems?",
                "a": "We start with a current-state inventory and a target-state architecture, then peel off services or modules in priority order. Mainframe and Oracle Fusion workloads move to modern stacks (cloud-native, low-code, or open-source) in increments, with parallel run periods so federal staff are never left without a working system.",
            },
            {
                "q": "How do you handle modernization while we are still serving the public?",
                "a": "Strangler-fig patterns, blue/green deploys, and feature flags. Public-facing systems stay live while the new architecture takes over function by function. We design rollback paths before we ship, so any issue is recoverable in minutes rather than an outage that hits the front page.",
            },
            {
                "q": "Does Pyramid Systems hold contract vehicles for federal modernization work?",
                "a": "Yes. Pyramid is on GSA IT Schedule 70, GSA OASIS+ Unrestricted, GSA 8(a) STARS III, HHS CMS SPARC, SEC ONE IT, FDIC ITAS III Next Gen BOA, and the HUD O&M BPA. AIR-Quire, our AI-powered federal acquisition platform, is Awardable on the DoW Tradewinds Solutions Marketplace.",
            },
            {
                "q": "What does a typical modernization roadmap look like for a federal program of record?",
                "a": "Weeks 1 to 6: current-state inventory, target-state architecture, and a written rollout plan tied to the existing ATO boundary. Months 2 to 6: first vertical slice in production behind a feature flag. Months 6 to 18: increment-by-increment migration with parallel run on every cutover. Months 18 to 36: legacy decommission and SRE handoff. We tie every increment to a 2 to 4 week production cadence.",
            },
            {
                "q": "How do you handle a mid-program modernization where the prime contractor is changing?",
                "a": "The pipeline, the IaC, the documentation, and the SBOMs are written so a new prime can pick up the program without a rebuild. Open-source tooling, federal-standard languages, no proprietary lock-in. What survives a contract change is the discipline embedded in the artifacts.",
            },
            {
                "q": "Do you only work with federal agencies?",
                "a": "Federal agencies are the majority of our delivery experience, and that's the rigor our commercial clients hire us for too. Pyramid serves federal agencies and regulated enterprises (financial services, healthcare networks, utilities, regulated technology platforms) that demand the same audit posture, uptime, and compliance discipline we built for federal mission systems. If your environment is regulated, audited, or relied on by people who notice when it breaks, you are our audience.",
            },
        ],
    },
    {
        "slug": "cloud",
        "name": "Cloud",
        "h1_main": "Cloud",
        "tag": "Cloud Services",
        "title": "Cloud Services | Pyramid Systems",
        "meta_desc": "Move workloads to AWS, Azure, Google Cloud, or Cloud.gov on a Cloud Smart roadmap. FedRAMP-aware architecture for federal agencies and regulated enterprises that need the same security posture. 30 years of production delivery.",
        "service_type": "Cloud migration, FedRAMP cloud architecture, managed cloud operations",
        "cta_h2": "Ready to land a Cloud Smart migration with FedRAMP in scope?",
        "lead": "Move workloads to AWS, Azure, Google Cloud, or Cloud.gov on a Cloud Smart roadmap. Pyramid lands FedRAMP Moderate and High architectures, runs hybrid through the on-prem boundary, and operates the platform after launch so your team does not inherit a half-built migration. Built originally for federal mission systems, equally rigorous for regulated commercial platforms.",
        "body_sections": [
            {
                "h2": "What we do",
                "items": [
                    "Cloud Migration Planning aligned to the Federal Cloud Smart strategy",
                    "Cloud Architecture and Implementation",
                    "Managed Cloud Operations and Services",
                ],
            },
            {
                "h2": "How we deliver",
                "items": [
                    "IaaS across AWS, Azure, and Google Cloud",
                    "PaaS on Red Hat OpenShift, Cloud Foundry, Cloud.gov, and Login.gov",
                    "SaaS rollouts on Microsoft 365",
                    "Low-code on Salesforce, Appian, and ServiceNow",
                ],
            },
            {
                "h2": "Outcomes we ship",
                "items": [
                    "Increased capability and performance at lower TCO",
                    "Elastic, on-demand architecture that scales with the mission",
                    "Secure, highly available systems audited to federal standards",
                ],
            },
        ],
        "anchor_p": 'Production proof. A <a href="../insights/case-studies/index.html">biometrics platform</a> we deployed runs across 138 application support centers and processes 15,000+ daily immigration applicants. A <a href="../insights/case-studies/index.html">Cloud.gov publishing automation</a> we built powers a public-facing .gov today.',
        "faqs": [
            {
                "q": "Do you support FedRAMP High deployments?",
                "a": "Yes. We architect, deploy, and operate workloads at FedRAMP Moderate and High boundaries. We have shipped to AWS GovCloud, Azure Government, and Cloud.gov, and we can step into existing ATO boundaries or help establish new ones.",
            },
            {
                "q": "Can you migrate without downtime to public-facing systems?",
                "a": "Yes, on most workloads. We use blue/green deployments, traffic shifting, and database replication so the public site, portal, or API stays available during cutover. For systems that cannot be split, we plan a maintenance window with stakeholders weeks in advance.",
            },
            {
                "q": "How do you handle the boundary between cloud and our existing on-prem systems?",
                "a": "Hybrid is the rule, not the exception. We design private connectivity (Direct Connect, ExpressRoute, Cloud Interconnect), identity federation via ICAM, and data-flow patterns that respect the existing on-prem authority boundary while letting cloud workloads consume what they need.",
            },
            {
                "q": "What is the cost trajectory in years 1, 2, and 3 of a typical migration?",
                "a": "Year 1 is usually flat to slightly higher than on-prem because you are running both. Year 2 drops as on-prem decommissions complete and reserved instances or savings plans kick in. Year 3 is where the elastic, right-sized footprint shows up as a 25 to 40 percent reduction versus the original baseline, alongside capacity gains the legacy stack could not deliver.",
            },
            {
                "q": "Does Pyramid Systems hold a contract vehicle for federal cloud migration?",
                "a": "Yes. GSA IT Schedule 70 (SIN 518210C Cloud Services), GSA OASIS+ Unrestricted, HHS CMS SPARC, SEC ONE IT, GSA 8(a) STARS III, and the HUD O&M BPA all cover cloud migration and managed cloud operations. Cloud Smart, FedRAMP, and OMB M-19-26 alignment is in scope under each vehicle.",
            },
            {
                "q": "Can Pyramid support IL5 or IL6 environments?",
                "a": "For DoD IL2 and IL4 we deploy under FedRAMP Moderate and High on AWS GovCloud and Azure Government. IL5 and IL6 require sponsor-specific authorizations; we scope these per program, in partnership with the cognizant Authorizing Official, and staff to the clearance level the mission requires.",
            },
            {
                "q": "How long does a federal cloud migration typically take?",
                "a": "A single application moves in 8 to 16 weeks once the target boundary is defined. A program of record with 20 to 40 applications runs 12 to 24 months end to end. We deliver the first production cutover inside 90 days so the agency sees real elastic capacity before the long-tail decommission completes.",
            },
            {
                "q": "Do you only work with federal agencies?",
                "a": "Federal agencies are the majority of our delivery experience, and that's the rigor our commercial clients hire us for too. Pyramid serves federal agencies and regulated enterprises (financial services, healthcare networks, utilities, regulated technology platforms) that demand the same audit posture, uptime, and compliance discipline we built for federal mission systems. If your environment is regulated, audited, or relied on by people who notice when it breaks, you are our audience.",
            },
        ],
    },
    {
        "slug": "cybersecurity",
        "name": "Cybersecurity and Compliance",
        "h1_main": "Cybersecurity and Compliance",
        "tag": "Cybersecurity Services",
        "title": "Cybersecurity and Compliance | Pyramid Systems",
        "meta_desc": "FISMA, FedRAMP, and ATO-ready security from day one. Zero-trust architecture and DevSecOps from a CMMI Level 3 partner. Built for federal agencies and regulated enterprises across financial, healthcare, and critical infrastructure.",
        "service_type": "Cybersecurity, FISMA and FedRAMP compliance, ATO support, zero-trust architecture",
        "cta_h2": "Ready to ship FISMA-aligned systems that pass the first ATO review?",
        "lead": "Pyramid runs FISMA-aligned, FedRAMP-aware, and ATO-ready security from day one of the program. We work alongside your ISSM, generate continuous-monitoring evidence in the pipeline, and brief the authorizing official in language they recognize. Built originally for federal mission systems, equally at home in regulated commercial environments under HIPAA, PCI, or SOC 2.",
        "body_sections": [
            {
                "h2": "What we do",
                "items": [
                    "Security architecture and zero-trust design",
                    "ATO authorization support",
                    "FedRAMP and FISMA compliance",
                    "Continuous monitoring",
                    "SOC integration",
                ],
            },
            {
                "h2": "How we deliver",
                "items": [
                    "Security-by-design from day one, not bolted on at the end",
                    "DevSecOps pipelines with embedded SAST, DAST, and SCA scanning",
                    "SBOM generation and vulnerability management",
                    "NIST 800-53 and 800-171 controls implemented and evidenced, EO 14028 logging and SBOM requirements wired into the pipeline.",
                    "ICAM integration for federal identity",
                ],
            },
            {
                "h2": "Outcomes we ship",
                "items": [
                    "Faster path to ATO",
                    "Reduced audit findings",
                    "Continuous compliance evidence, generated automatically",
                    "Mission systems hardened against active threats",
                ],
            },
        ],
        "anchor_p": 'Production proof. Independently appraised at CMMI-DEV Maturity Level 3 and CMMI-SVC Maturity Level 3. <a href="../contract-vehicles/index.html">FedRAMP</a>-aware delivery, production-tested across <a href="../insights/case-studies/index.html">HUD, SEC, CMS, USDA, FDIC, and USCIS</a>.',
        "faqs": [
            {
                "q": "Do you handle the full ATO process end-to-end?",
                "a": "Yes. We have walked agencies through ATO from initial categorization through SSP, SAR, POA&M, and authorizing-official decision. We work the way your ISSM and authorizing official work, not the way a textbook says it should go.",
            },
            {
                "q": "What is your approach to zero-trust for federal systems?",
                "a": "We align to OMB M-22-09 and the CISA Zero Trust Maturity Model. Identity is the new perimeter: every workload, every user, every device, every request authenticated and authorized. We implement in stages so you reach optimal maturity in pillars where the mission depends on it first.",
            },
            {
                "q": "How do you keep continuous compliance after go-live?",
                "a": "We bake evidence generation into the pipeline itself: control attestations from IaC, SBOMs from every build, scan results from every deploy. Your continuous-monitoring posture is a query, not a quarterly scramble.",
            },
            {
                "q": "Can you brief our agency CIO and ISSM on the security posture?",
                "a": "Yes. We deliver formal posture briefings, risk dashboards, and walk-through sessions tuned to the audience. CIO gets the strategic view; ISSM gets the control-level detail; both leave knowing what is green, what is amber, and what is being done about it.",
            },
            {
                "q": "What is a realistic timeline to ATO with Pyramid?",
                "a": "A new moderate-impact system typically reaches ATO in 6 to 12 months from kickoff when we start with the security categorization. A re-authorization on a known boundary runs 3 to 6 months. We can compress these timelines using a continuous ATO model where evidence is generated by the pipeline rather than written at the end. The Authorizing Official still owns the decision.",
            },
            {
                "q": "Does Pyramid hold a contract vehicle for federal cybersecurity work?",
                "a": "Yes. Cybersecurity scope is covered under GSA IT Schedule 70 (HACS SIN), GSA OASIS+ Unrestricted, HHS CMS SPARC, SEC ONE IT, GSA 8(a) STARS III, FDIC ITAS III, and the HUD O&M BPA. CMMI-DEV Maturity Level 3 and CMMI-SVC Maturity Level 3 appraisals are current.",
            },
            {
                "q": "How do you align to EO 14028 and OMB M-22-09?",
                "a": "EO 14028 logging (M-21-31) and SBOM requirements (NTIA minimum elements) are wired into our pipelines so every build emits the artifacts. M-22-09 zero-trust pillars are implemented in priority order tied to the mission, with identity-first as the default starting line. We track maturity against the CISA Zero Trust Maturity Model and report progress quarterly.",
            },
            {
                "q": "Do you only work with federal agencies?",
                "a": "Federal agencies are the majority of our delivery experience, and that's the rigor our commercial clients hire us for too. Pyramid serves federal agencies and regulated enterprises (financial services, healthcare networks, utilities, regulated technology platforms) that demand the same audit posture, uptime, and compliance discipline we built for federal mission systems. If your environment is regulated, audited, or relied on by people who notice when it breaks, you are our audience.",
            },
        ],
    },
    {
        "slug": "analytics-ai",
        "name": "Analytics and AI",
        "h1_main": "Analytics and AI",
        "tag": "Analytics and AI Services",
        "title": "Analytics and AI | Pyramid Systems",
        "meta_desc": "Data platforms, dashboards, and explainable AI built for audit and Inspector General review. Aligned to OMB M-24-10 and EO 14110. Built for federal agencies and regulated enterprises that need defensible AI decisions.",
        "service_type": "Data analytics, dashboards, machine learning and explainable AI",
        "cta_h2": "Ready to ship AI workflows that survive Inspector General review?",
        "lead": "Convert structured and unstructured data into evidence for decision-making. Pyramid builds data platforms, dashboards, and AI workflows that hold up under audit and Inspector General review. Built originally for federal mission systems, equally rigorous for regulated enterprises where every model decision has to defend itself.",
        "body_sections": [
            {
                "h2": "What we do",
                "items": [
                    "Data platform architecture",
                    "Dashboards and reporting",
                    "ML and AI workflow design",
                    "Natural language and document understanding",
                    "Data quality and governance",
                ],
            },
            {
                "h2": "How we deliver",
                "items": [
                    "Cloud-native data stacks",
                    "Open-source ML tooling, with commercial AI services where they fit",
                    "Explainable AI tuned for federal use, with audit trails per decision",
                    "PII handling and minimum-necessary access",
                    "Aligned with OMB M-24-10 and the federal executive order on AI",
                ],
            },
            {
                "h2": "Outcomes we ship",
                "items": [
                    "Auditor-ready evidence",
                    "Faster analyst workflows",
                    "Defensible AI decisions",
                    "Lower data infrastructure cost",
                ],
            },
        ],
        "anchor_p": 'Production proof. <a href="../solutions/air-quire.html">AIR-Quire</a>, our AI-powered federal acquisition platform, is live, <a href="../contract-vehicles/index.html">Awardable on Tradewinds</a>, and deployed at HUD AMSS. Production-tested across <a href="../insights/case-studies/index.html">HUD, SEC, CMS, USDA, FDIC, and USCIS</a>.',
        "faqs": [
            {
                "q": "How do you handle PII in analytics and AI workflows?",
                "a": "Minimum necessary access, encryption at rest and in transit, tokenization for joins across datasets, and audit logs on every read. We design data flows so PII never reaches an unauthorized analyst, model, or report.",
            },
            {
                "q": "What is your stance on generative AI for federal use cases?",
                "a": "Useful when scoped, risky when ungoverned. We help agencies pick the right model class for the job, isolate it in the right boundary, log every prompt and response, and provide a human-review path for any decision the model touches.",
            },
            {
                "q": "Do you build models in-house or use commercial AI services?",
                "a": "Both. Where a frontier model adds real capability and the boundary allows it, we use it. Where the data must stay inside the agency boundary or the use case demands transparency, we build and tune in-house, often on open-source foundations.",
            },
            {
                "q": "How do you make AI decisions explainable to OIG or Congressional review?",
                "a": "Every AI-assisted decision lands with a decision record: inputs, model version, prompt or feature set, output, human reviewer, and final action. The record is queryable, exportable, and retained per the system's records schedule.",
            },
            {
                "q": "Is Pyramid Systems on a contract vehicle for federal AI and analytics?",
                "a": "Yes. AIR-Quire, our AI-powered federal acquisition platform, is Awardable on the DoW Tradewinds Solutions Marketplace. Analytics and AI services are also covered under GSA IT Schedule 70 (including SINs 54151S and 518210C), GSA OASIS+ Unrestricted, HHS CMS SPARC, SEC ONE IT, GSA 8(a) STARS III, and the HUD O&M BPA.",
            },
            {
                "q": "How do you align AI workflows to OMB M-24-10 and Executive Order 14110?",
                "a": "M-24-10 requires agencies to inventory AI use cases, manage risk, and designate a Chief AI Officer. We help agencies build the inventory, classify each use case, write the impact assessment, and put the governance loop on a calendar. EO 14110 alignment shows up as model documentation, red-team testing on high-risk use cases, and reproducible evaluation artifacts.",
            },
            {
                "q": "Can you build AI inside an agency boundary without sending data to a commercial API?",
                "a": "Yes. For high-sensitivity data we deploy open-source foundation models (Llama family, Mistral, others) inside the agency FedRAMP boundary on AWS GovCloud or Azure Government. Inference, fine-tuning, and evaluation all stay inside the boundary. No prompt, no embedding, no training example crosses the trust boundary unless an Authorizing Official has approved that egress in writing.",
            },
            {
                "q": "Do you only work with federal agencies?",
                "a": "Federal agencies are the majority of our delivery experience, and that's the rigor our commercial clients hire us for too. Pyramid serves federal agencies and regulated enterprises (financial services, healthcare networks, utilities, regulated technology platforms) that demand the same audit posture, uptime, and compliance discipline we built for federal mission systems. If your environment is regulated, audited, or relied on by people who notice when it breaks, you are our audience.",
            },
        ],
    },
    {
        "slug": "devsecops",
        "name": "DevSecOps",
        "h1_main": "DevSecOps",
        "tag": "DevSecOps Services",
        "title": "DevSecOps | Pyramid Systems",
        "meta_desc": "DevSecOps pipelines, security tooling, and engineering culture. CMMI Level 3, ATO-aware from day one. Built for federal agencies and regulated enterprises that ship audited software under uptime pressure.",
        "service_type": "DevSecOps pipelines, CI/CD, security tooling, SRE",
        "cta_h2": "Ready to compress lead time without compromising the ATO?",
        "lead": "Move DME and O&M programs onto an integrated DevSecOps pipeline. Pyramid wires SAST, DAST, SCA, and SBOM generation into every pull request, ships GitOps from dev through production, and emits the audit evidence the ISSM (or your auditor) needs in the format the authorizing official accepts. Built originally for federal mission systems, equally rigorous for regulated commercial platforms shipping under uptime pressure.",
        "body_sections": [
            {
                "h2": "What we do",
                "items": [
                    "CI/CD pipeline design and rollout",
                    "Security tooling integration",
                    "Container and Kubernetes deployment",
                    "Automated testing and quality gates",
                    "SRE and observability",
                ],
            },
            {
                "h2": "How we deliver",
                "items": [
                    "Open-source pipeline tooling that survives the contract change",
                    "SAST, DAST, and SCA integrated into every pull request",
                    "SBOM generation on every build",
                    "EO 14028 SBOM and logging requirements (NTIA minimum elements, M-21-31) generated in pipeline.",
                    "IaC with Terraform and Ansible",
                    "GitOps for federal environments, from dev to production",
                ],
            },
            {
                "h2": "Outcomes we ship",
                "items": [
                    "Lead time from commit to production drops from weeks to hours",
                    "Security findings caught in pipeline rather than production",
                    "Audit evidence generated automatically",
                    "Team velocity compounds over the life of the program",
                ],
            },
        ],
        "anchor_p": 'Production proof. Our internal R&D function ships experiments into pilots and pilots into production programs. Independently appraised at CMMI-DEV Maturity Level 3. Production-tested across <a href="../insights/case-studies/index.html">HUD, SEC, CMS, USDA, FDIC, and USCIS</a>.',
        "faqs": [
            {
                "q": "Can you stand up a DevSecOps pipeline that is ATO-aware from day one?",
                "a": "Yes. The pipeline itself emits compliance evidence: control attestations, scan results, SBOMs, deployment records. By the time you reach the SSP and SAR, the pipeline has been generating the artifacts you need for months.",
            },
            {
                "q": "How do you integrate with our existing security tooling and SOC?",
                "a": "We meet the SOC where it lives. SIEM forwarding, Splunk integration, Tenable feeds, ServiceNow ticketing, agency-standard vulnerability databases. We do not bring a tool the SOC has not approved unless the SOC asks for it.",
            },
            {
                "q": "What is a realistic timeline for a DevSecOps rollout in a federal program?",
                "a": "First production pipeline in 90 days for a single service, 6 to 12 months to roll the model across a program of record. We deliver in increments so an agency sees value before the full rollout completes.",
            },
            {
                "q": "Do you support classified or sensitive environments?",
                "a": "Yes. We have engineers cleared and active in environments with the security postures federal mission systems require. We can scope work to the clearance level and environment the program needs. We have engineers cleared up to TS/SCI and active in Impact Level 4 and Impact Level 5 environments where the program requires it. Scope is set per contract, with cleared resources cited by name in the technical volume.",
            },
            {
                "q": "Is Pyramid on a contract vehicle for federal DevSecOps work?",
                "a": "Yes. GSA IT Schedule 70 (including SIN 54151S), GSA OASIS+ Unrestricted, HHS CMS SPARC, SEC ONE IT, GSA 8(a) STARS III, FDIC ITAS III, and the HUD O&M BPA all cover DevSecOps and platform-engineering work.",
            },
            {
                "q": "What tooling does Pyramid bring versus what stays agency-standard?",
                "a": "We default to the agency existing toolchain wherever it works. If the agency has standardized on GitLab, we run GitLab CI. If the SOC uses Splunk and Tenable, we forward to Splunk and Tenable. We only introduce a new tool when there is a gap the existing stack cannot cover, and we always run that introduction through the agency CCB and SOC.",
            },
            {
                "q": "How do you measure DevSecOps maturity for a federal program?",
                "a": "We track the four DORA metrics (deployment frequency, lead time for changes, change failure rate, time to restore service) alongside federal-specific metrics: time-to-evidence, percentage of controls auto-attested, and percentage of releases that ship without a manual security gate. We report quarterly against a published baseline.",
            },
            {
                "q": "Do you only work with federal agencies?",
                "a": "Federal agencies are the majority of our delivery experience, and that's the rigor our commercial clients hire us for too. Pyramid serves federal agencies and regulated enterprises (financial services, healthcare networks, utilities, regulated technology platforms) that demand the same audit posture, uptime, and compliance discipline we built for federal mission systems. If your environment is regulated, audited, or relied on by people who notice when it breaks, you are our audience.",
            },
        ],
    },
]


# Map every service to a short description and SVG icon for the "other services" grid
OTHER_SERVICE_BLURB = {
    "modernization": {
        "blurb": "Replace legacy systems without breaking the mission. Mainframe, SharePoint, Oracle, low-code.",
        "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#E86222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="i-100"><path d="M3 12a9 9 0 1 0 9-9"/><path d="M3 4v5h5"/><path d="M12 7v5l3 3"/></svg>',
    },
    "cloud": {
        "blurb": "Cloud Smart federal migrations across AWS, Azure, GCP, and Cloud.gov.",
        "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#E86222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="i-100"><path d="M17.5 19a4.5 4.5 0 1 0-1.5-8.75A6 6 0 0 0 4 12a5 5 0 0 0 5 7h8.5"/></svg>',
    },
    "cybersecurity": {
        "blurb": "Zero-trust, FISMA, FedRAMP, and ATO support from a CMMI Level 3 partner.",
        "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#E86222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="i-100"><path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z"/><path d="M9 12l2 2 4-4"/></svg>',
    },
    "analytics-ai": {
        "blurb": "Federal data platforms, dashboards, and explainable AI built for audit.",
        "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#E86222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="i-100"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/></svg>',
    },
    "devsecops": {
        "blurb": "CI/CD pipelines, security tooling, and SRE for federal mission systems.",
        "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#E86222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="i-100"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M6 8v3a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V8"/><path d="M12 14v2"/></svg>',
    },
}


def build_head(svc: dict) -> str:
    """Build the page <head>. Marker comments are stamped by apply_templates.py."""
    canon = f"https://pyramidsystems.com/services/{svc['slug']}.html"

    faqs_json = ",\n        ".join(
        '{{"@type":"Question","name":{q},"acceptedAnswer":{{"@type":"Answer","text":{a}}}}}'.format(
            q=_json_str(f["q"]), a=_json_str(f["a"])
        )
        for f in svc["faqs"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel="icon" type="image/png" href="../images/newPyramidLogoIcon.png"/>
        <link rel="apple-touch-icon" href="../images/newPyramidLogoIcon.png"/>

        <!-- TEMPLATE:a11y_widget:START -->
        <!-- TEMPLATE:a11y_widget:END -->

                <!-- TEMPLATE:consent:START -->
        <link rel="stylesheet" href="../css/pyramid-consent.css">
        <script src="../js/pyramid-consent.js" defer></script>
        <!-- TEMPLATE:consent:END -->

                <!-- TEMPLATE:attribution:START -->
        <script src="../js/pyramid-attribution.js"></script>
        <!-- TEMPLATE:attribution:END -->

                <!-- TEMPLATE:ac_tracking:START -->
        <script src="../js/pyramid-ac-tracking.js"></script>
        <!-- TEMPLATE:ac_tracking:END -->

        <!-- Webflow w-mod-js bootstrap. Marks <html> with .w-mod-js so the
             interaction CSS that gates animations on .w-mod-js applies. Also
             tags .w-mod-touch on touch devices. Must run before paint. -->
        <script type="text/javascript">
            !function(o, c) {{
                var n = c.documentElement
                  , t = " w-mod-";
                n.className += t + "js",
                ("ontouchstart"in o || o.DocumentTouch && c instanceof DocumentTouch) && (n.className += t + "touch")
            }}(window, document);
        </script>
        <script>document.documentElement.setAttribute("data-wf-page","68b0b16eeab74bec787faa10");document.documentElement.setAttribute("data-wf-site","67ffbeb3c6d67519154ab9f3");</script>
        <meta charset="utf-8"/>
        <title>{svc['title']}</title>
        <meta content="{svc['meta_desc']}" name="description"/>
        <link rel="canonical" href="{canon}"/>
        <meta content="width=device-width, initial-scale=1" name="viewport"/>

        <!-- OpenGraph -->
        <meta property="og:title" content="{svc['title']}"/>
        <meta property="og:description" content="{svc['meta_desc']}"/>
        <meta property="og:url" content="{canon}"/>
        <meta property="og:type" content="website"/>
        <meta property="og:site_name" content="Pyramid Systems"/>
        <meta property="og:image" content="https://pyramidsystems.com/images/orangeLogo.png"/>
        <!-- Twitter -->
        <meta name="twitter:card" content="summary_large_image"/>
        <meta name="twitter:title" content="{svc['title']}"/>
        <meta name="twitter:description" content="{svc['meta_desc']}"/>
        <meta name="twitter:image" content="https://pyramidsystems.com/images/orangeLogo.png"/>

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@400;700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">

        <!-- Shared Webflow / neurakey base CSS that powers the glossar 2-col layout, the popups,
             and the contact form section. Hashed integrity copy lives on the CDN. -->
        <link href="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/css/neurakey.webflow.shared.6005fb4e8.css" rel="stylesheet" type="text/css" integrity="sha384-YAX7ToYn4yzo7mWTlBz2bG3fT2O7Shcg4NiD0JruypcCk6qRUvmmdGI5PdUajEJl" crossorigin="anonymous"/>
        <link href="../css/styles.css" rel="stylesheet" type="text/css" crossorigin="anonymous"/>
        <!-- air-quire-mocks.css powers the contact form's right-side preview panel
             (the agency-readiness mockup). The embedded contact form section relies
             on .aq-form-mock, .aq-form-chart, .eng-progress, .aq-form-donut. -->
        <link href="../css/air-quire-mocks.css" rel="stylesheet" type="text/css"/>

        <!-- Pyramid orange overrides for the neurakey-blue CTA card and minor glossar polish.
             These targeted rules win on specificity without editing shared CSS. -->
        <style>
            /* Pyramid brand: re-color the glossar sticky CTA from neurakey-blue to Pyramid orange. */
            .glossar_blue-cta-wrap {{
                background: linear-gradient(160deg, #E86222 0%, #C9531C 60%, #A8431A 100%) !important;
            }}
            .glossar_blue-cta-wrap .button_inner-wrap.is--white {{
                color: #E86222 !important;
            }}
            /* The sticky CTA's gradient halo asset is brand-blue. Hide it under the orange surface. */
            .glossar_blue-cta-wrap .cta_gradient-wrap.is--glossar {{ display: none; }}
            /* Tag pill: replace neurakey gradient with Pyramid orange tint. */
            .glossar-inner_tag-wrap {{
                background: rgba(232, 98, 34, 0.14) !important;
                border: 1px solid rgba(232, 98, 34, 0.35) !important;
            }}
            .glossar-inner_tag-wrap p {{
                color: #E86222 !important;
            }}
            /* Full portfolio grid: fixed 3 columns desktop, 2 mid, 1 mobile.
               With 5 cards, desktop renders as 3 on top + 2 on bottom row.
               The bottom two anchor to the left (default grid auto-placement),
               matching the reference layout. */
            .other-services-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1.25rem;
                margin-top: 2.5rem;
            }}
            @media (max-width: 991px) {{
                .other-services-grid {{ grid-template-columns: repeat(2, 1fr); }}
            }}
            @media (max-width: 599px) {{
                .other-services-grid {{ grid-template-columns: 1fr; }}
            }}
            .other-services-card {{
                position: relative;
                display: flex;
                flex-direction: column;
                gap: .75rem;
                padding: 1.5rem;
                border-radius: 1rem;
                background: rgba(255, 255, 255, 0.025);
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: #f4f5f9;
                text-decoration: none;
                transition: transform .18s ease, border-color .18s ease, background .18s ease;
            }}
            .other-services-card:hover {{
                transform: translateY(-3px);
                border-color: rgba(232, 98, 34, 0.45);
                background: rgba(232, 98, 34, 0.05);
            }}
            .other-services-card_icon {{ width: 2.5rem; height: 2.5rem; }}
            .other-services-card_title {{ font-size: 1.25rem; font-weight: 600; margin: 0; }}
            .other-services-card_blurb {{
                font-size: .95rem;
                line-height: 1.5;
                color: rgba(244, 245, 249, 0.75);
                margin: 0;
            }}
            .other-services-card_arrow {{
                position: absolute;
                top: 1.25rem;
                right: 1.25rem;
                width: 1.25rem;
                height: 1.25rem;
                color: rgba(244, 245, 249, 0.55);
                transition: color .18s ease, transform .18s ease;
            }}
            .other-services-card:hover .other-services-card_arrow {{
                color: #E86222;
                transform: rotate(45deg);
            }}
            /* Current-page card: subdued surface, no hover lift, "You are here" pill. */
            .other-services-card.is--current {{
                background: rgba(232, 98, 34, 0.06);
                border-color: rgba(232, 98, 34, 0.35);
                cursor: default;
            }}
            .other-services-card.is--current:hover {{
                transform: none;
                background: rgba(232, 98, 34, 0.06);
                border-color: rgba(232, 98, 34, 0.35);
            }}
            .other-services-card_here {{
                position: absolute;
                top: 1.1rem;
                right: 1.1rem;
                padding: 0.25rem 0.625rem;
                border-radius: 999px;
                background: rgba(232, 98, 34, 0.18);
                border: 1px solid rgba(232, 98, 34, 0.45);
                color: #E86222;
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.02em;
                line-height: 1;
                white-space: nowrap;
            }}
            /* Popups: start hidden until the JS controller decides to show them */
            .popup-leave, .popup-magnet {{ opacity: 0; display: none; }}

            /* Keep the site-wide sticky-reveal footer behavior. The footer is
               position: sticky; bottom: 0 — as you scroll, main slides up over it
               and the footer is "revealed" from below. To prevent the footer's
               transparent rendering from bleeding through gaps in the page body,
               give <main> a solid bg color and lift it above the footer in the
               stacking context. */
            main {{
                position: relative;
                z-index: 1;
                background-color: var(--_tokenization---bg-main, #0E0E12);
            }}

            /* +/- accordion icon toggle. When an accordion opens, fade out the
               vertical bar so only the horizontal remains, forming a minus icon. */
            .accordion_icon .vertical_faq-line,
            .accordion_icon .horizontal_faq-line {{
                transition: opacity .25s ease, transform .25s ease;
            }}
            .accordion.is--opened .vertical_faq-line {{
                opacity: 0;
                transform: rotate(90deg);
            }}

            /* Sticky right-rail CTA position: stretch the column and pin the CTA. */
            .glossar-content_additional-info {{ align-self: stretch; }}
            .glossar_blue-cta-wrap {{ position: sticky; top: 7rem; }}

            /* Contact form side preview: hide on mobile, collapse to full-width form.
               Matches the rule in services/index.html so the form section behaves the
               same way here as on the services hub. */
            @media (max-width: 991px) {{
                .form-image_wrap,
                .aq-form-mock {{ display: none !important; }}
                .form-block__form-image {{
                    grid-template-columns: 1fr !important;
                    display: flex !important;
                    flex-direction: column !important;
                }}
            }}
        </style>

        <!-- Finsweet Attributes (local copy on the Pyramid site for offline-safe loads) -->
        <script async type="module" src="../js/attributes.js" fs-scrolldisable></script>

        <!-- Structured data: Service schema -->
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Federal IT {svc['name']}",
            "serviceType": {_json_str(svc['service_type'])},
            "description": {_json_str(svc['meta_desc'])},
            "url": "{canon}",
            "provider": {{
                "@type": "Organization",
                "name": "Pyramid Systems",
                "url": "https://pyramidsystems.com/",
                "logo": "https://pyramidsystems.com/images/orangeLogo.png",
                "telephone": "+1-703-553-0800",
                "sameAs": ["https://www.linkedin.com/company/pyramid-systems-inc-"]
            }},
            "areaServed": [
                {{"@type":"Country","name":"United States"}},
                {{"@type":"GovernmentOrganization","name":"U.S. Department of Housing and Urban Development"}},
                {{"@type":"GovernmentOrganization","name":"U.S. Securities and Exchange Commission"}},
                {{"@type":"GovernmentOrganization","name":"Centers for Medicare and Medicaid Services"}},
                {{"@type":"GovernmentOrganization","name":"U.S. Department of Agriculture"}},
                {{"@type":"GovernmentOrganization","name":"Federal Deposit Insurance Corporation"}},
                {{"@type":"GovernmentOrganization","name":"U.S. Citizenship and Immigration Services"}}
            ],
            "audience": {{
                "@type": "Audience",
                "audienceType": "Federal civilian agencies"
            }}
        }}
        </script>
        <!-- Structured data: FAQPage schema -->
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
        {faqs_json}
            ]
        }}
        </script>
        <!-- Structured data: Breadcrumbs -->
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
        {{"@type":"ListItem","position":1,"name":"Home","item":"https://pyramidsystems.com/"}},
        {{"@type":"ListItem","position":2,"name":"Services","item":"https://pyramidsystems.com/services/"}},
        {{"@type":"ListItem","position":3,"name":{_json_str(svc['name'])},"item":"{canon}"}}
            ]
        }}
        </script>
        <!-- Structured data: WebPage with Speakable specification for voice assistants. -->
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "WebPage",
            "url": "{canon}",
            "name": {_json_str(svc['h1_main'])},
            "speakable": {{
                "@type": "SpeakableSpecification",
                "cssSelector": [".glossar-inner_rt p", ".blogs_faq-text p"]
            }},
            "isPartOf": {{"@type":"WebSite","url":"https://pyramidsystems.com/","name":"Pyramid Systems"}}
        }}
        </script>
    </head>"""


def _json_str(s: str) -> str:
    """Return s as a JSON string literal (quote + escape). Used inside ld+json blocks."""
    import json
    return json.dumps(s, ensure_ascii=False)


def build_other_services_section(current_slug: str) -> str:
    """Build the full Pyramid services grid. Renders ALL 5 services so the
    visitor sees the complete portfolio in peripheral vision; the card for
    the current page gets an `is--current` modifier so it can be styled as
    a "You're here" pill rather than a navigation target."""
    cards = []
    for svc in SERVICES:
        meta = OTHER_SERVICE_BLURB[svc["slug"]]
        is_current = svc["slug"] == current_slug
        modifier = " is--current" if is_current else ""
        aria_current = ' aria-current="page"' if is_current else ""
        # "You're here" pill replaces the diagonal arrow on the current card
        # so it reads as orientation, not a click target.
        if is_current:
            corner_html = '<span class="other-services-card_here">You are here</span>'
        else:
            corner_html = (
                '<svg class="other-services-card_arrow" xmlns="http://www.w3.org/2000/svg" '
                'viewBox="0 0 14 14" fill="none">'
                '<path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.4" stroke-linecap="square" stroke-linejoin="round"/>'
                '<path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.4" stroke-linecap="square" stroke-linejoin="bevel"/>'
                '</svg>'
            )
        cards.append(f"""                            <a href="{svc['slug']}.html" class="other-services-card{modifier}"{aria_current}>
                                <div class="other-services-card_icon">{meta['icon']}</div>
                                <h3 class="other-services-card_title">{svc['name']}</h3>
                                <p class="other-services-card_blurb">{meta['blurb']}</p>
                                {corner_html}
                            </a>""")
    cards_html = "\n".join(cards)

    return f"""            <section>
                <div class="section-form_wrap">
                    <div class="w-layout-blockcontainer container w-container">
                        <div class="blog_articles-block is--inner">
                            <div class="content-wrap">
                                <div class="blog-heading_wrap">
                                    <div class="upheader">
                                        <div class="upheader_icon">
                                            <img src="../images/newPyramidLogoIcon.png" alt="" />
                                        </div>
                                        <p lines-animation="">The full Pyramid portfolio</p>
                                    </div>
                                    <h2 lines-animation="" class="heading-7">
                                        Explore the <span class="text-gradient">Pyramid portfolio</span>
                                    </h2>
                                </div>
                                <div class="other-services-grid">
{cards_html}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>"""


def build_bottom_cta_section(svc: dict) -> str:
    """Bottom dark CTA card with decorative imagery (gradient + bg + 2x dots)."""
    return f"""            <section>
                <div class="cta_content-block">
                    <div class="w-layout-blockcontainer container w-container">
                        <div class="cta_content-wrap is--dark">
                            <div class="cta_texts-wrap">
                                <div class="cta_titles-wrap">
                                    <h2 lines-animation="" class="heading-8">{svc['cta_h2']}</h2>
                                </div>
                                <p lines-animation="" class="t--cta-text">
                                    30 minutes with an engineer who has shipped at HUD, SEC, CMS, USDA, FDIC, and USCIS. Bring your problem, leave with a fit assessment.
                                </p>
                            </div>
                            <div class="tripple-buttons-wrap">
                                <a href="../services/index.html" class="button arrow-animation is--glossar-cta w-inline-block">
                                    <div class="button_inner-wrap">
                                        <div>View All Services</div>
                                        <div class="button-arrow is--main">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                            </svg>
                                        </div>
                                    </div>
                                </a>
                                <a href="../contact/index.html" class="button arrow-animation is--glossar-cta w-inline-block">
                                    <div class="button_inner-wrap is--white-dark">
                                        <div>Talk to our team</div>
                                        <div class="button-arrow is--main">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                            </svg>
                                        </div>
                                    </div>
                                </a>
                            </div>
                            <div class="cta_gradient-wrap">
                                <img src="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/680dce4e9bf5c7568927c86f_cta%20gradient.svg" loading="lazy" alt="" class="i-100"/>
                            </div>
                            <div class="cta_figure-wrap-bg is--dark">
                                <img src="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/6878c0c361ff85992a2d05a1_bg.avif" loading="eager" alt="" class="i-100"/>
                            </div>
                            <div class="cta-dots is--2">
                                <img src="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/680359143d96b2fa3c7c23a1_dots%203.avif" loading="lazy" alt="" class="i-100"/>
                            </div>
                            <div class="cta-dots">
                                <img src="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/680359143d96b2fa3c7c23a1_dots%203.avif" loading="lazy" alt="" class="i-100"/>
                            </div>
                        </div>
                    </div>
                </div>
            </section>"""


def build_glossar_section(svc: dict) -> str:
    """Build the glossar 2-column layout: breadcrumbs, tag, H1, lead, body, FAQ + sticky CTA."""

    # Body rich-text: heading + bullets per section
    body_blocks = []
    for sec in svc["body_sections"]:
        items_html = "".join(f"<li>{item}</li>" for item in sec["items"])
        body_blocks.append(f"""                                            <h2>{sec['h2']}</h2>
                                            <ul>{items_html}</ul>""")
    body_blocks.append(f'                                            <p>{svc["anchor_p"]}</p>')
    body_html = "\n".join(body_blocks)

    # FAQ block — accordion.is--blogs pattern with +/- icon and per-item expand/collapse.
    faq_items = []
    for f in svc["faqs"]:
        faq_items.append(f"""                                            <div class="accordion is--blogs">
                                                <div class="accordion_heading blogs">
                                                    <h3 class="h3-faq-blogs">{f['q']}</h3>
                                                    <div class="accordion_icon">
                                                        <div class="horizontal_faq-line"></div>
                                                        <div class="vertical_faq-line"></div>
                                                    </div>
                                                </div>
                                                <div class="accordion_text-wrap">
                                                    <div class="accordion-text">
                                                        <div class="blogs_faq-text w-richtext"><p>{f['a']}</p></div>
                                                    </div>
                                                </div>
                                            </div>""")
    faq_html = "\n".join(faq_items)

    return f"""            <section>
                <div class="w-layout-blockcontainer container w-container">
                    <div class="glossar-inner_content-wrap">
                        <div class="glossar-inner_breadcrumbs-wrap">
                            <a href="../index.html" class="bc_link w-inline-block">
                                <div>Home</div>
                            </a>
                            <div class="bc-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 12 12" fill="none">
                                    <path d="M4.5 9L7.5 6L4.5 3" stroke="#F4F5F9" stroke-opacity="0.55"></path>
                                </svg>
                            </div>
                            <a href="index.html" class="bc_link w-inline-block">
                                <div>Services</div>
                            </a>
                            <div class="bc-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 12 12" fill="none">
                                    <path d="M4.5 9L7.5 6L4.5 3" stroke="#F4F5F9" stroke-opacity="0.55"></path>
                                </svg>
                            </div>
                            <p class="bc-current">{svc['name']}</p>
                        </div>
                        <div class="glossar_content-block">
                            <div class="glossar-content_body">
                                <div class="glossar-inner_tag-wrap">
                                    <p>{svc['tag']}</p>
                                </div>
                                <div class="glossar-inner_h1--overview">
                                    <h1 class="h1--h2-style">{svc['h1_main']}</h1>
                                    <div class="glossar-inner_rt w-richtext">
                                        <p>{svc['lead']}</p>
                                    </div>
                                </div>
                                <div class="glossar_second-rt">
                                    <div class="glossar-inner_rt w-richtext">
{body_html}
                                    </div>
                                </div>
                                <div class="glossar-inner_faq-block">
                                    <h2 class="h2-32">Frequently asked questions</h2>
                                    <div class="glossar-faqs_wrap">
{faq_html}
                                    </div>
                                </div>
                            </div>
                            <div class="glossar-content_additional-info">
                                <div class="glossar_blue-cta-wrap">
                                    <div class="glossar-blue_main-info">
                                        <div class="upheader text--white">
                                            <div class="upheader_icon-na">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M7.65625 0.109375C6.93138 0.109375 6.34375 0.697001 6.34375 1.42187V5.2002C6.34375 5.8957 6.03525 6.55536 5.50147 7.00122C5.07943 7.35375 4.54699 7.54688 3.99708 7.54688H1.3125C0.587626 7.54688 0 8.1345 0 8.85938V12.5781C0 13.303 0.587626 13.8906 1.3125 13.8906H5.03125C5.75612 13.8906 6.34375 13.303 6.34375 12.5781V10.0986C6.34375 9.40719 6.65046 8.75136 7.18113 8.3081C7.60071 7.95762 8.13005 7.76562 8.67676 7.76562H12.6875C13.4124 7.76562 14 7.178 14 6.45312V1.42188C14 0.697001 13.4124 0.109375 12.6875 0.109375H7.65625Z" fill="currentColor"></path>
                                                </svg>
                                            </div>
                                            <p>Free. No obligation.</p>
                                        </div>
                                        <h3 class="h3-24">30-min modernization consultation</h3>
                                        <div class="glossar-blue_subheader">
                                            <p>30 minutes with an engineer who has shipped at HUD, SEC, CMS, USDA, FDIC, and USCIS. Bring your problem, leave with a fit assessment.</p>
                                        </div>
                                    </div>
                                    <div class="glossar-blue_button-wrap">
                                        <a href="../services/index.html" class="button arrow-animation w-inline-block">
                                            <div class="button_inner-wrap is--white">
                                                <div>View All Services</div>
                                                <div class="button-arrow is--main">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none">
                                                        <path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>
                                                        <path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>
                                                    </svg>
                                                </div>
                                            </div>
                                        </a>
                                    </div>
                                    <div class="glossar-blue_common-info-wrap">
                                        <div class="glossar-common_text-block">
                                            <div class="glossar-common_icon">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 16 16" fill="none">
                                                    <g opacity="0.85"><path d="M8.00002 14.6667C8.00002 14.6667 13.3334 12 13.3334 8.00004V3.33337L8.00002 1.33337L2.66669 3.33337V8.00004C2.66669 12 8.00002 14.6667 8.00002 14.6667Z" stroke="white" stroke-opacity="0.8" stroke-width="1.16667"></path></g>
                                                </svg>
                                            </div>
                                            <p>HUD, SEC, CMS, USDA, FDIC, USCIS deployments</p>
                                        </div>
                                        <div class="glossar-common_text-block">
                                            <div class="glossar-common_icon">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 16 16" fill="none">
                                                    <g opacity="0.85"><path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="white" stroke-opacity="0.8" stroke-width="1.16667"></path></g>
                                                </svg>
                                            </div>
                                            <p>CMMI Maturity Level 3 appraised</p>
                                        </div>
                                        <div class="glossar-common_text-block">
                                            <div class="glossar-common_icon">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 16 16" fill="none">
                                                    <g opacity="0.85"><rect x="2.5" y="3.33" width="11" height="10" rx="1.2" stroke="white" stroke-opacity="0.8" stroke-width="1.16667"></rect><path d="M2.5 6.67H13.5M5.5 2v2.67M10.5 2v2.67" stroke="white" stroke-opacity="0.8" stroke-width="1.16667" stroke-linecap="round"></path></g>
                                                </svg>
                                            </div>
                                            <p>30 years modernizing mission-critical systems</p>
                                        </div>
                                    </div>
                                    <div class="cta_gradient-wrap is--glossar">
                                        <img src="https://cdn.prod.website-files.com/67ffbeb3c6d67519154ab9f3/680dce4e9bf5c7568927c86f_cta%20gradient.svg" loading="lazy" alt="" class="i-100"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>"""


# ----------------------------------------------------------------------------
# Site-wide popups (English) + AC submission JS
# ----------------------------------------------------------------------------

POPUP_LEAVE_HTML = """            <style>
                /* Popup-leave dark-glass input styling. Webflow's .w-input base styling
                   gives these inputs a white background and ~32px height; these rules
                   override that to match the neurakey dark-glass aesthetic the rest of
                   the popup uses and the contact form on services/index.html. */
                /* User-specified spec: dark glass field with inset highlight. */
                .popup-leave .leave-popup_input,
                .popup-leave .leave-popup_input.w-input {
                    height: 2.75rem !important;
                    color: var(--_tokenization---text-white, #f4f5f9) !important;
                    background-color: #f4f5f90a !important;
                    border: 0.0625rem solid #fbfbfb14 !important;
                    border-radius: 0.75rem !important;
                    margin-bottom: 0 !important;
                    padding: 0.75rem 0.875rem !important;
                    font-size: 0.875rem !important;
                    box-shadow: inset 0 5px 12px #f4f5f90f !important;
                    transition: border-color .2s ease, background-color .2s ease;
                }
                .popup-leave .leave-popup_input::placeholder { color: rgba(244, 245, 249, 0.4); }
                .popup-leave .leave-popup_input:focus,
                .popup-leave .leave-popup_input.w-input:focus {
                    outline: none;
                    border-color: rgba(232, 98, 34, 0.65) !important;
                    background-color: rgba(255, 255, 255, 0.06) !important;
                }
                .popup-leave .leave-popup_input:invalid:focus { border-color: rgba(232, 98, 34, 0.65) !important; }
                /* Magnet popup email input: same dark glass with PDF-prefix room. */
                .popup-magnet .pm-form_input-wrap { position: relative; }
                .popup-magnet .magnet-popup_input,
                .popup-magnet .magnet-popup_input.w-input {
                    height: 2.75rem !important;
                    color: var(--_tokenization---text-white, #f4f5f9) !important;
                    background-color: #f4f5f90a !important;
                    border: 0.0625rem solid #fbfbfb14 !important;
                    border-radius: 0.75rem !important;
                    margin-bottom: 0 !important;
                    padding: 0.75rem 0.875rem 0.75rem 4rem !important;
                    font-size: 0.875rem !important;
                    box-shadow: inset 0 5px 12px #f4f5f90f !important;
                    width: 100%;
                    transition: border-color .2s ease;
                }
                .popup-magnet .magnet-popup_input::placeholder { color: rgba(244, 245, 249, 0.4); }
                .popup-magnet .magnet-popup_input:focus { outline: none; border-color: rgba(232, 98, 34, 0.65) !important; }
                .popup-magnet .magnet-input_prefix {
                    position: absolute;
                    left: 0.5rem;
                    top: 50%;
                    transform: translateY(-50%);
                    display: inline-flex;
                    align-items: center;
                    gap: 0.25rem;
                    padding: 0.25rem 0.5rem;
                    background: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0.5rem;
                    font-size: 0.6875rem;
                    font-weight: 600;
                    letter-spacing: 0.04em;
                    color: rgba(244, 245, 249, 0.85);
                    pointer-events: none;
                    line-height: 1;
                }
                .popup-magnet .magnet-input_prefix svg { opacity: 0.85; }
                /* Agency chips: pill-style rows mirroring the services hero partner
                   treatment (small inverted icon + agency abbreviation in glassy pill).
                   Selector chain matches neurakey specificity so width:auto on the
                   chip actually sticks (previously chips inherited full column width). */
                body .popup-leave .pll_partners .pll-partners_logos-wrap {
                    display: flex !important;
                    flex-direction: row !important;
                    flex-wrap: wrap !important;
                    align-items: center !important;
                    gap: 0.5rem 0.5rem !important;
                    width: 100% !important;
                }
                body .popup-leave .pll_partners .pll-partners_logos-wrap .pll-partner_logo {
                    display: inline-flex !important;
                    flex: 0 0 auto !important;
                    width: auto !important;
                    max-width: max-content !important;
                    align-items: center !important;
                    padding: 0.4rem 0.8rem !important;
                    border-radius: 999px !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                    border: 1px solid rgba(255, 255, 255, 0.1) !important;
                    height: auto !important;
                    min-height: 0 !important;
                    font-size: 0.8125rem !important;
                    line-height: 1 !important;
                    color: #f4f5f9 !important;
                    white-space: nowrap !important;
                    font-weight: 500;
                    letter-spacing: 0.02em;
                }
                .popup-leave .pll-partner_logo span {
                    font-weight: 500;
                    letter-spacing: 0.02em;
                }
                /* Tighten label → input spacing per launch feedback */
                .popup-leave .popul-leave_input {
                    margin-bottom: 0.25rem !important;
                    line-height: 1.2 !important;
                    font-size: 0.8125rem;
                    color: rgba(244, 245, 249, 0.7);
                }
                .popup-leave .leave-popup_labell-input { gap: 0.25rem !important; }
                .popup-leave .leave-popup_inputs-wrap { gap: 0.75rem !important; }
                /* Name row: side-by-side First + Last on desktop, stacked under 540px. */
                .popup-leave .leave-popup_name-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 0.625rem;
                }
                @media (max-width: 539px) {
                    .popup-leave .leave-popup_name-row { grid-template-columns: 1fr; }
                }
                /* Required-field asterisk: muted accent so it reads as helper info, not alarm. */
                .popup-leave .popup-required-mark {
                    color: rgba(232, 98, 34, 0.85);
                    margin-left: 0.15rem;
                    font-weight: 500;
                }
                .popup-magnet .popup-required-mark {
                    color: rgba(232, 98, 34, 0.85);
                    margin-left: 0.15rem;
                    font-weight: 500;
                }
                /* Override Webflow's heavy pink alert box for any server-side error
                   we couldn't catch client-side (network failure, surprise AC
                   validation, etc). Renders as a small inline note matching the
                   client-side .popup-inline-error style. */
                .popup-leave .w-form-fail,
                .popup-magnet .w-form-fail {
                    margin-top: 0.5rem !important;
                    padding: 0 !important;
                    background: transparent !important;
                    border: 0 !important;
                    border-radius: 0 !important;
                    box-shadow: none !important;
                }
                .popup-leave .w-form-fail > div,
                .popup-magnet .w-form-fail > div {
                    color: #ff7777 !important;
                    font-size: 12px !important;
                    line-height: 1.4 !important;
                    text-align: left !important;
                    padding: 0 !important;
                    background: transparent !important;
                }
            </style>
            <div class="popup-leave">
                <div class="popup-bg leave-popup_close"></div>
                <div class="popup-leave_content">
                    <div class="popup-leave_side">
                        <div class="pll_tag">
                            <div class="pll-tag_dot"></div>
                            <p>Free consultation</p>
                        </div>
                        <div class="pll_title">
                            <p class="h2-32">
                                <span>30 minutes with a </span><span class="text-gradient">senior engineer</span><span>. No slide deck.</span>
                            </p>
                        </div>
                        <div class="pll_description">
                            <p class="pll_description--desk">Bring a system, a procurement question, or an ATO problem. Leave with a fit assessment and a written next step.</p>
                            <p class="pll_description--mob">Bring a system or an ATO problem. Leave with a fit assessment.</p>
                        </div>
                        <div class="pll_list">
                            <ul role="list" class="pl-list">
                                <li class="pl-li">
                                    <div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div>
                                    <p>30 minutes, no obligation, no upsell</p>
                                </li>
                                <li class="pl-li">
                                    <div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div>
                                    <p>Tailored to your agency mission and contract vehicle</p>
                                </li>
                                <li class="pl-li">
                                    <div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div>
                                    <p>Production engineers on the call, not sales</p>
                                </li>
                                <li class="pl-li">
                                    <div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div>
                                    <p>Fit assessment and scoping notes after</p>
                                </li>
                            </ul>
                        </div>
                        <div class="pll_partners">
                            <p class="t--partners-title">Trusted by federal agencies</p>
                            <div class="pll-partners_logos-wrap">
                                <div class="pll-partner_logo"><span>HUD</span></div>
                                <div class="pll-partner_logo"><span>SEC</span></div>
                                <div class="pll-partner_logo"><span>CMS</span></div>
                                <div class="pll-partner_logo"><span>USDA</span></div>
                                <div class="pll-partner_logo"><span>FDIC</span></div>
                                <div class="pll-partner_logo"><span>USCIS</span></div>
                            </div>
                        </div>
                    </div>
                    <div class="popup-leave_side">
                        <div class="plr_tag">Get the consultation</div>
                        <div class="plr_title">
                            <p>Tell us where you sit. We will reply by tomorrow.</p>
                        </div>
                        <div class="plr_description">
                            <p>One business day reply. Reach a federal engineer on the first call.</p>
                        </div>
                        <div class="plr_form--button">
                            <div class="u---form-block w-form">
                                <!-- Dedicated AC form: "Service Page Consultation Request" (u=7, f=7).
                                     Created in AC with firstname + lastname + agency + email + phone +
                                     attribution fields + marketing consent. The `or` UUID matches AC's
                                     embed so AC's native form analytics see this submission as form 7. -->
                                <form id="popup-leave-form" name="popup-leave-form" data-name="Popup Leave Form" method="POST" class="leave-popup_form" action="https://pyramidsystems.activehosted.com/proc.php">
                                    <input type="hidden" name="u" value="7"/>
                                    <input type="hidden" name="f" value="7"/>
                                    <input type="hidden" name="s"/>
                                    <input type="hidden" name="c" value="0"/>
                                    <input type="hidden" name="m" value="0"/>
                                    <input type="hidden" name="act" value="sub"/>
                                    <input type="hidden" name="v" value="2"/>
                                    <input type="hidden" name="or" value="f3e1a45a-e7ac-419a-9653-170725fb2bed"/>
                                    <!-- Marketing consent (field[14]): implied opt-in on consultation
                                         request. The user is asking for sales/engineering contact, which
                                         constitutes consent for related communications. -->
                                    <input type="hidden" name="field[14]" value="Yes"/>
                                    <!-- UTM + attribution hidden fields. Pre-filled at page load from
                                         window.PyramidAttribution.getStored(), then re-written at submit
                                         time from getStoredAndIncrementSubmission() so submission_count
                                         reflects THIS submission. Same field IDs as contact form. -->
                                    <input type="hidden" name="field[18]" value="" id="popup-leave-first_utm_source"/>
                                    <input type="hidden" name="field[19]" value="" id="popup-leave-first_utm_medium"/>
                                    <input type="hidden" name="field[20]" value="" id="popup-leave-first_utm_campaign"/>
                                    <input type="hidden" name="field[21]" value="" id="popup-leave-first_utm_content"/>
                                    <input type="hidden" name="field[22]" value="" id="popup-leave-first_landing_page"/>
                                    <input type="hidden" name="field[23]" value="" id="popup-leave-first_referrer_url"/>
                                    <input type="hidden" name="field[25]" value="" id="popup-leave-last_utm_source"/>
                                    <input type="hidden" name="field[26]" value="" id="popup-leave-last_utm_medium"/>
                                    <input type="hidden" name="field[27]" value="" id="popup-leave-last_utm_campaign"/>
                                    <input type="hidden" name="field[28]" value="" id="popup-leave-last_utm_content"/>
                                    <input type="hidden" name="field[29]" value="" id="popup-leave-last_landing_page"/>
                                    <input type="hidden" name="field[30]" value="" id="popup-leave-last_referrer_url"/>
                                    <input type="hidden" name="field[33]" value="" id="popup-leave-session_count"/>
                                    <input type="hidden" name="field[34]" value="" id="popup-leave-days_since_first_visit"/>
                                    <input type="hidden" name="field[35]" value="" id="popup-leave-submission_count"/>
                                    <!-- Submission page URL: the EXACT URL where the form was filled.
                                         Distinct from last_landing_page (entry point for the session).
                                         Set fresh at populate-time from window.location.href. -->
                                    <input type="hidden" name="field[36]" value="" id="popup-leave-submission_page_url"/>
                                    <input type="text" name="ac_hp_zz9" tabindex="-1" autocomplete="new-password" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0;width:0;height:0;"/>
                                    <div class="leave-popup_inputs-wrap">
                                        <div class="leave-popup_name-row">
                                            <div class="leave-popup_labell-input">
                                                <label for="popup-leave-firstname" class="popul-leave_input">First name <span class="popup-required-mark" aria-hidden="true">*</span></label>
                                                <input class="leave-popup_input w-input" maxlength="120" name="firstname" placeholder="Jane" type="text" id="popup-leave-firstname" required aria-required="true"/>
                                            </div>
                                            <div class="leave-popup_labell-input">
                                                <label for="popup-leave-lastname" class="popul-leave_input">Last name <span class="popup-required-mark" aria-hidden="true">*</span></label>
                                                <input class="leave-popup_input w-input" maxlength="120" name="lastname" placeholder="Smith" type="text" id="popup-leave-lastname" required aria-required="true"/>
                                            </div>
                                        </div>
                                        <div class="leave-popup_labell-input">
                                            <label for="popup-leave-agency" class="popul-leave_input">Agency or organization <span class="popup-required-mark" aria-hidden="true">*</span></label>
                                            <input class="leave-popup_input w-input" maxlength="256" name="field[10]" placeholder="HUD, SEC, CMS, USDA..." type="text" id="popup-leave-agency" required aria-required="true"/>
                                        </div>
                                        <div class="leave-popup_labell-input">
                                            <label for="popup-leave-email" class="popul-leave_input">Email <span class="popup-required-mark" aria-hidden="true">*</span></label>
                                            <input class="leave-popup_input w-input" maxlength="256" name="email" placeholder="jane.smith@agency.gov" type="email" id="popup-leave-email" required aria-required="true"/>
                                        </div>
                                        <div class="leave-popup_labell-input">
                                            <label for="popup-leave-phone" class="popul-leave_input">Phone</label>
                                            <input class="leave-popup_input w-input" maxlength="256" name="phone" placeholder="+1 (202) 555 0123" type="tel" id="popup-leave-phone" autocomplete="tel"/>
                                        </div>
                                    </div>
                                    <button type="submit" class="button arrow-animation is--mob-smaller">
                                        <div class="button_inner-wrap is--mob-smaller">
                                            <div>Get my 30-min consultation</div>
                                            <div class="button-arrow is--main is--mob-smaller">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none"><path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path><path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path></svg>
                                            </div>
                                        </div>
                                    </button>
                                </form>
                                <div class="success-message w-form-done" style="display:none;">
                                    <div>Got it. We will email you within one business day to schedule.</div>
                                </div>
                                <div class="w-form-fail" style="display:none;">
                                    <div>Something went wrong. Please email <a href="mailto:info@pyramidsystems.com">info@pyramidsystems.com</a> or try again.</div>
                                </div>
                            </div>
                        </div>
                        <div class="plr_checks is--desk">
                            <div class="plr-check">
                                <div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16683 2.75L4.12516 7.79167L1.8335 5.5" stroke="#10B981" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div>
                                <p>30 years modernizing mission-critical systems</p>
                            </div>
                            <div class="plr-check">
                                <div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16683 2.75L4.12516 7.79167L1.8335 5.5" stroke="#10B981" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div>
                                <p>CMMI Maturity Level 3 appraised</p>
                            </div>
                            <button type="button" class="plr-check is--underline leave-popup_close">
                                <p>I will figure it out on my own</p>
                            </button>
                        </div>
                    </div>
                    <button type="button" class="popup_close-btn leave-popup_close">
                        <div class="close-btn_icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 16 16" fill="none"><path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.66667" stroke-linecap="round"></path></svg>
                        </div>
                    </button>
                </div>
            </div>"""

POPUP_MAGNET_HTML = """            <div class="popup-magnet">
                <div class="popup-magnet_top-side">
                    <div class="popup-magnet_icon-wrap">
                        <div class="u---svg w-embed">
                            <svg width="100%" height="100%" viewBox="0 0 72 96" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="72" height="96" rx="6" fill="#E86222"/>
                                <rect opacity="0.18" width="72" height="96" rx="6" fill="white"/>
                                <rect x="8" y="8" width="40" height="4" rx="2" fill="#fff" fill-opacity="0.9"/>
                                <rect x="8" y="15" width="50" height="4" rx="2" fill="#fff" fill-opacity="0.6"/>
                                <rect x="8" y="22" width="28" height="4" rx="2" fill="#fff" fill-opacity="0.6"/>
                                <rect x="8" y="60" width="56" height="3" rx="1.5" fill="#fff" fill-opacity="0.55"/>
                                <rect x="8" y="68" width="48" height="3" rx="1.5" fill="#fff" fill-opacity="0.45"/>
                                <rect x="8" y="76" width="40" height="3" rx="1.5" fill="#fff" fill-opacity="0.45"/>
                                <rect x="8" y="84" width="32" height="3" rx="1.5" fill="#fff" fill-opacity="0.45"/>
                            </svg>
                        </div>
                    </div>
                    <div class="popup-magnet_top--texts">
                        <div class="pm_tag">
                            <p>Free PDF, 1 page</p>
                        </div>
                        <div class="pm-title">
                            <p>Get the Pyramid Capability Statement.</p>
                        </div>
                        <div class="pm_subheading">
                            <p>1-page federal contractor snapshot: agencies served, contract vehicles, NAICS codes, past performance.</p>
                        </div>
                    </div>
                    <button type="button" class="pm-popup_icon-close">
                        <div class="cross-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 12 12" fill="none">
                                <path d="M9 3L3 9" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"></path>
                                <path d="M3 3L9 9" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"></path>
                            </svg>
                        </div>
                    </button>
                </div>
                <div class="pm_ul-wrap">
                    <ul role="list" class="pm-ul">
                        <li class="pm-li"><div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div><p>Agencies served and contract vehicles</p></li>
                        <li class="pm-li"><div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div><p>NAICS codes and core competencies</p></li>
                        <li class="pm-li"><div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div><p>Past performance highlights</p></li>
                        <li class="pm-li"><div class="pl-li_icon"><div class="pl-check"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 11 11" fill="none"><path d="M9.16659 2.75L4.12492 7.79167L1.83325 5.5" stroke="currentColor" stroke-width="1.60417" stroke-linecap="round" stroke-linejoin="round"></path></svg></div></div><p>Ready to drop into a capture file</p></li>
                    </ul>
                </div>
                <div class="pm_form--text">
                    <div class="u---form-block w-form">
                        <!-- PDF asset placeholder. The user will swap the real PDF in post-launch.
                             Path: images/pyramid-capability-statement.pdf -->
                        <!-- Dedicated AC form: "Service Page PDF Download" (u=5, f=5).
                             Created in AC with email-only + attribution fields + marketing consent.
                             The `or` UUID matches AC's embed so AC's native form analytics see
                             this submission as belonging to form 5. -->
                        <form id="popup-magnet-form" name="popup-magnet-form" data-name="Popup Magnet Form" method="POST" action="https://pyramidsystems.activehosted.com/proc.php" novalidate>
                            <input type="hidden" name="u" value="5"/>
                            <input type="hidden" name="f" value="5"/>
                            <input type="hidden" name="s"/>
                            <input type="hidden" name="c" value="0"/>
                            <input type="hidden" name="m" value="0"/>
                            <input type="hidden" name="act" value="sub"/>
                            <input type="hidden" name="v" value="2"/>
                            <input type="hidden" name="or" value="60a44107-a165-4d05-8fec-22ab75aa485d"/>
                            <!-- Marketing consent (field[14]): implied opt-in on PDF download.
                                 Standard B2B lead-magnet pattern. The user is initiating the
                                 download action, which constitutes consent for related comms.
                                 If you want explicit consent later, swap this for a visible
                                 checkbox that posts the same value. -->
                            <input type="hidden" name="field[14]" value="Yes"/>
                            <!-- UTM + attribution hidden fields. Pre-filled on load + re-written
                                 at submit time from PyramidAttribution. Same field IDs as the
                                 contact form so AC's custom fields are reused. -->
                            <input type="hidden" name="field[18]" value="" id="popup-magnet-first_utm_source"/>
                            <input type="hidden" name="field[19]" value="" id="popup-magnet-first_utm_medium"/>
                            <input type="hidden" name="field[20]" value="" id="popup-magnet-first_utm_campaign"/>
                            <input type="hidden" name="field[21]" value="" id="popup-magnet-first_utm_content"/>
                            <input type="hidden" name="field[22]" value="" id="popup-magnet-first_landing_page"/>
                            <input type="hidden" name="field[23]" value="" id="popup-magnet-first_referrer_url"/>
                            <input type="hidden" name="field[25]" value="" id="popup-magnet-last_utm_source"/>
                            <input type="hidden" name="field[26]" value="" id="popup-magnet-last_utm_medium"/>
                            <input type="hidden" name="field[27]" value="" id="popup-magnet-last_utm_campaign"/>
                            <input type="hidden" name="field[28]" value="" id="popup-magnet-last_utm_content"/>
                            <input type="hidden" name="field[29]" value="" id="popup-magnet-last_landing_page"/>
                            <input type="hidden" name="field[30]" value="" id="popup-magnet-last_referrer_url"/>
                            <input type="hidden" name="field[33]" value="" id="popup-magnet-session_count"/>
                            <input type="hidden" name="field[34]" value="" id="popup-magnet-days_since_first_visit"/>
                            <input type="hidden" name="field[35]" value="" id="popup-magnet-submission_count"/>
                            <!-- Submission page URL: the EXACT URL where the form was filled.
                                 Distinct from last_landing_page (entry point for the session).
                                 Set fresh at populate-time from window.location.href. -->
                            <input type="hidden" name="field[36]" value="" id="popup-magnet-submission_page_url"/>
                            <input type="text" name="ac_hp_zz9" tabindex="-1" autocomplete="new-password" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0;width:0;height:0;"/>
                            <div class="pm-form_input--btn">
                                <div class="pm-form_input-wrap">
                                    <div class="magnet-input_prefix" aria-hidden="true">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
                                        <span>PDF</span>
                                    </div>
                                    <input class="magnet-popup_input w-input" maxlength="256" name="email" placeholder="you@agency.gov" type="email" id="popup-magnet-email" required aria-required="true"/>
                                </div>
                                <button type="submit" class="magnet-popup_button">
                                    <p>PDF</p>
                                    <div class="magnet-popu_icon">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 14 14" fill="none"><path d="M12.8334 1.16669L6.41675 7.58335" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12.8334 1.16669L8.75008 12.8334L6.41675 7.58335L1.16675 5.25002L12.8334 1.16669Z" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"></path></svg>
                                    </div>
                                </button>
                            </div>
                        </form>
                        <div class="success-message smaller w-form-done" style="display:none;">
                            <div>Sent. Check your inbox in the next minute.</div>
                        </div>
                        <div class="w-form-fail" style="display:none;">
                            <div>Something went wrong. Try again or email info@pyramidsystems.com.</div>
                        </div>
                    </div>
                    <p class="t--form-wa">
                        Federal contractor snapshot. PDF, 1 page.
                    </p>
                </div>
            </div>"""


POPUP_JS = """        <!-- Site-wide popup controller: exit-intent leave popup + 8s sticky capability magnet.
             Both forms submit to AC via the same JSONP pattern as the contact form. -->
        <script>
            (function () {
                /* === Attribution helpers — populate the hidden field[18-35]
                       inputs that match AC's custom fields. Called twice:
                       once on page load with the stored state, again at
                       submit time after bumping submission_count so the
                       value sent to AC reflects THIS submission. */
                function setACField(prefix, id, v) {
                    var el = document.getElementById(prefix + '-' + id);
                    if (el) el.value = (v == null ? '' : String(v));
                }
                function populateAttribution(prefix, state) {
                    state = state || {};
                    setACField(prefix, 'first_utm_source',   state.first_utm_source);
                    setACField(prefix, 'first_utm_medium',   state.first_utm_medium);
                    setACField(prefix, 'first_utm_campaign', state.first_utm_campaign);
                    setACField(prefix, 'first_utm_content',  state.first_utm_content);
                    setACField(prefix, 'first_landing_page', state.first_landing_page);
                    setACField(prefix, 'first_referrer_url', state.first_referrer_url);
                    setACField(prefix, 'last_utm_source',    state.last_utm_source);
                    setACField(prefix, 'last_utm_medium',    state.last_utm_medium);
                    setACField(prefix, 'last_utm_campaign',  state.last_utm_campaign);
                    setACField(prefix, 'last_utm_content',   state.last_utm_content);
                    setACField(prefix, 'last_landing_page',  state.last_landing_page);
                    setACField(prefix, 'last_referrer_url',  state.last_referrer_url);
                    setACField(prefix, 'session_count',      state.session_count);
                    setACField(prefix, 'submission_count',   state.submission_count);
                    var days = (window.PyramidAttribution && window.PyramidAttribution.getDaysSinceFirstVisit)
                        ? window.PyramidAttribution.getDaysSinceFirstVisit()
                        : 0;
                    setACField(prefix, 'days_since_first_visit', days);
                    /* submission_page_url is captured fresh from window.location.href
                       (not from PyramidAttribution state) so it always reflects the
                       EXACT page the popup is rendering on. Set at both prefill and
                       submit time, but in practice both happen on the same page so
                       both calls produce the same value. */
                    setACField(prefix, 'submission_page_url', window.location.href);
                }
                function prefillAttribution(prefix) {
                    var stored = (window.PyramidAttribution && window.PyramidAttribution.getStored && window.PyramidAttribution.getStored()) || {};
                    populateAttribution(prefix, stored);
                }

                /* === Phone helpers (mirrors air-quire form pattern) ===
                       AC's server requires E.164 format (+XXXXXXXXXXX). We normalize
                       client-side so users can type "(202) 555-0123" and get +12025550123
                       sent. If we can't normalize, show an inline error under the field
                       and block submit so AC never rejects the form. */
                function normalizePhoneToE164(raw) {
                    if (!raw) return '';
                    var trimmed = String(raw).trim();
                    if (!trimmed) return '';
                    var hasPlus = trimmed.charAt(0) === '+';
                    var digits = trimmed.replace(/[^\\d]/g, '');
                    if (!digits) return null;
                    if (hasPlus) {
                        if (digits.length < 7 || digits.length > 15) return null;
                        return '+' + digits;
                    }
                    /* No + → assume US/Canada */
                    if (digits.length === 10) return '+1' + digits;
                    if (digits.length === 11 && digits.charAt(0) === '1') return '+' + digits;
                    return null;
                }
                function showPhoneError(form, msg) {
                    var phoneEl = form.querySelector('input[name="phone"], input[name="phone-iti"]');
                    if (!phoneEl) return;
                    var wrap = phoneEl.closest('.leave-popup_labell-input') || phoneEl.parentElement;
                    showInlineError(wrap, msg, phoneEl);
                }
                /* Generic inline error helper: removes any prior error in the wrap,
                   inserts a small dark-red note, focuses the offending field. Used
                   for any client-side validation that needs to block submit without
                   rendering Webflow's heavy pink alert box. */
                function showInlineError(wrap, msg, focusEl) {
                    var existing = wrap.querySelector('.popup-inline-error');
                    if (existing) existing.remove();
                    if (!msg) return;
                    var err = document.createElement('div');
                    err.className = 'popup-inline-error';
                    err.style.cssText = 'color:#ff7777;font-size:12px;margin-top:4px;line-height:1.4;';
                    err.textContent = msg;
                    wrap.appendChild(err);
                    if (focusEl && typeof focusEl.focus === 'function') focusEl.focus();
                }
                /* Email validation: empty or invalid format → inline error, block submit.
                   Prevents AC's server-side "email-or-phone-required" translation error
                   from ever firing on an empty form. */
                var EMAIL_RE = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/;
                function validateEmail(form) {
                    var emailEl = form.querySelector('input[type="email"], input[name="email"]');
                    if (!emailEl) return true;
                    /* Pick a wrap so the error renders below the field, not beside it.
                       popup-leave: email's column container — error stacks below input.
                       popup-magnet: the form itself — error appended at end of form
                         renders visually below the horizontal email+button row, since
                         that row is the form's only visible child. */
                    var wrap = emailEl.closest('.leave-popup_labell-input') || form;
                    var val = (emailEl.value || '').trim();
                    if (!val) {
                        showInlineError(wrap, 'Enter your email to receive the PDF.', emailEl);
                        return false;
                    }
                    if (!EMAIL_RE.test(val)) {
                        showInlineError(wrap, 'That email address looks off. Double-check the format.', emailEl);
                        return false;
                    }
                    showInlineError(wrap, null); /* clear */
                    return true;
                }

                /* === AC form submission helper === */
                function wireAcForm(form, prefix) {
                    if (!form) return;
                    var wrap = form.closest('.w-form') || form.parentNode;
                    var doneEl = wrap.querySelector('.w-form-done');
                    var failEl = wrap.querySelector('.w-form-fail');

                    function showDone() {
                        form.style.display = 'none';
                        if (doneEl) doneEl.style.display = 'block';
                        if (failEl) failEl.style.display = 'none';
                    }
                    function showFail(msg) {
                        if (failEl) {
                            failEl.style.display = 'block';
                            var d = failEl.querySelector('div');
                            if (d && msg) d.textContent = msg;
                        }
                    }

                    /* Pre-fill attribution fields at page load so they're present
                       even if the form serializes earlier than our submit handler. */
                    prefillAttribution(prefix);

                    form.addEventListener('submit', function (e) {
                        e.preventDefault();
                        e.stopImmediatePropagation();

                        /* Honeypot */
                        var hp = form.querySelector('input[name="ac_hp_zz9"]');
                        if (hp && hp.value.trim() !== '') { showDone(); return false; }

                        /* Email validation. Block submit on empty/invalid so AC's
                           server-side validator never returns its translation-error
                           message through the pink fail box. */
                        if (!validateEmail(form)) return false;

                        /* Phone normalization (E.164). If user typed a US 10-digit
                           number, prepend +1; if they used +country format already,
                           strip formatting and validate length. Block submit on
                           invalid input so AC never returns its red-box error. */
                        var phoneEl = form.querySelector('input[name="phone"]');
                        if (phoneEl) {
                            showPhoneError(form, null); /* clear any prior */
                            var raw = phoneEl.value;
                            if (raw && raw.trim()) {
                                var normalized = normalizePhoneToE164(raw);
                                if (normalized === null) {
                                    showPhoneError(form, 'Enter a valid phone number, e.g. (202) 555-0123 or +44 20 7946 0958.');
                                    return false;
                                }
                                phoneEl.value = normalized; /* overwrite for serialization */
                            }
                        }

                        /* Refresh attribution + bump submission_count THIS submit */
                        try {
                            if (window.PyramidAttribution && window.PyramidAttribution.getStoredAndIncrementSubmission) {
                                populateAttribution(prefix, window.PyramidAttribution.getStoredAndIncrementSubmission());
                            }
                        } catch (err) {}

                        /* AC identify */
                        try {
                            var emailEl = form.querySelector('input[type="email"]');
                            if (window.PyramidACTracking && emailEl && emailEl.value) {
                                window.PyramidACTracking.identify(emailEl.value);
                            }
                        } catch (err) {}

                        /* Serialize and JSONP-submit */
                        var pairs = [];
                        var elements = form.elements;
                        for (var i = 0; i < elements.length; i++) {
                            var el = elements[i];
                            if (!el.name || el.disabled) continue;
                            if (el.name === 'ac_hp_zz9') continue;
                            if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) continue;
                            if (el.type === 'submit' || el.type === 'button') continue;
                            pairs.push(encodeURIComponent(el.name) + '=' + encodeURIComponent(el.value));
                        }
                        var serialized = pairs.join('&').replace(/%0A/g, '\\\\n');

                        window._show_thank_you = showDone;
                        window._show_error = function (id, msg) { showFail(msg); };

                        var s = document.createElement('script');
                        s.src = 'https://pyramidsystems.activehosted.com/proc.php?' + serialized + '&jsonp=true';
                        s.onerror = function () { showFail('Network error. Please try again or email info@pyramidsystems.com.'); };
                        document.body.appendChild(s);
                        return false;
                    }, true);
                }

                wireAcForm(document.getElementById('popup-leave-form'), 'popup-leave');
                wireAcForm(document.getElementById('popup-magnet-form'), 'popup-magnet');

                /* === Popup show/hide controller === */
                var leavePopup = document.querySelector('.popup-leave');
                var magnetPopup = document.querySelector('.popup-magnet');
                var leaveCloseBtns = document.querySelectorAll('.leave-popup_close');
                var magnetCloseBtn = document.querySelector('.pm-popup_icon-close');

                /* Session storage so a closed popup stays closed for the rest of the session. */
                var STORAGE_KEY_LEAVE = 'pyramid-popup-leave-dismissed';
                var STORAGE_KEY_MAGNET = 'pyramid-popup-magnet-dismissed';

                var leaveShown = sessionStorage.getItem(STORAGE_KEY_LEAVE) === '1';
                var magnetShown = sessionStorage.getItem(STORAGE_KEY_MAGNET) === '1';
                var leaveOpen = false;
                var magnetTimer = null;

                var isDesktop = window.matchMedia('(min-width: 992px)').matches;

                function showPopup(p) {
                    p.style.display = 'flex';
                    setTimeout(function () { p.style.opacity = '1'; }, 0);
                }
                function hidePopup(p, cb) {
                    p.style.opacity = '0';
                    p.addEventListener('transitionend', function once() {
                        p.style.display = 'none';
                        p.removeEventListener('transitionend', once);
                        if (cb) cb();
                    });
                    /* Fallback in case transitionend never fires */
                    setTimeout(function () { p.style.display = 'none'; if (cb) cb(); }, 500);
                }

                function scheduleMagnet() {
                    if (!magnetPopup || magnetShown) return;
                    clearTimeout(magnetTimer);
                    magnetTimer = setTimeout(function () {
                        if (leaveOpen || magnetShown) return;
                        magnetShown = true;
                        showPopup(magnetPopup);
                    }, 12000);
                }
                function showLeave() {
                    if (!leavePopup || leaveShown) return;
                    leaveShown = true;
                    leaveOpen = true;
                    clearTimeout(magnetTimer);
                    if (magnetPopup && magnetPopup.style.display === 'flex') {
                        hidePopup(magnetPopup, function () { showPopup(leavePopup); });
                    } else {
                        showPopup(leavePopup);
                    }
                }

                scheduleMagnet();

                if (isDesktop) {
                    document.documentElement.addEventListener('mouseleave', function (e) {
                        if (e.clientY < 5) showLeave();
                    });
                }

                leaveCloseBtns.forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        leaveOpen = false;
                        sessionStorage.setItem(STORAGE_KEY_LEAVE, '1');
                        if (leavePopup) hidePopup(leavePopup, scheduleMagnet);
                    });
                });
                if (magnetCloseBtn) {
                    magnetCloseBtn.addEventListener('click', function () {
                        sessionStorage.setItem(STORAGE_KEY_MAGNET, '1');
                        if (magnetPopup) hidePopup(magnetPopup);
                    });
                }
            })();
        </script>"""


def build_scripts_block() -> str:
    """Standard Pyramid scripts block (jQuery, Webflow, GSAP, Lenis, Swiper, Finsweet, proof-stats)."""
    return """        <script src="../js/jquery-3.5.1.min.dc5e7f18c8.js" type="text/javascript" crossorigin="anonymous"></script>
        <script src="../js/webflow.schunk.36b8fb49256177c8.js" type="text/javascript" crossorigin="anonymous"></script>
        <script src="../js/6204f98b.merged.js" type="text/javascript"></script>
        <script src="../js/gsap.min.js" type="text/javascript"></script>
        <script src="../js/ScrollTrigger.min.js" type="text/javascript"></script>
        <script src="../js/SplitText.min.js" type="text/javascript"></script>
        <script type="text/javascript">gsap.registerPlugin(ScrollTrigger, SplitText);</script>
        <script src="../js/lenis.min.js"></script>
        <script async src="../js/cmsfilter.js"></script>
        <script>
            let lenis;
            if (typeof Webflow !== 'undefined' && Webflow.env("editor") === undefined) {
                lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 0.7, gestureOrientation: "vertical", normalizeWheel: false, smoothTouch: false });
                function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
                requestAnimationFrame(raf);
            }
        </script>
        <script>
            gsap.registerPlugin(ScrollTrigger, SplitText);
            (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () {
                document.querySelectorAll('[lines-animation]').forEach(function (el) {
                    var split = SplitText.create(el, { type: 'lines' });
                    gsap.from(split.lines, { scrollTrigger: { trigger: el, start: 'top 80%', toggleActions: 'play none none none' }, y: 80, opacity: 0, ease: 'power3.out', duration: 0.8, stagger: { each: 0.1 } });
                });
            });
        </script>
        <!-- FAQ accordion: .accordion.is--blogs pattern. Click-to-toggle with smooth
             height transition, one open at a time inside each .glossar-faqs_wrap. -->
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                var wrappers = document.querySelectorAll('.glossar-faqs_wrap');
                wrappers.forEach(function (wrap) {
                    var accs = wrap.querySelectorAll('.accordion.is--blogs');
                    if (!accs.length) return;
                    accs.forEach(function (acc) {
                        var tw = acc.querySelector('.accordion_text-wrap');
                        if (!tw) return;
                        acc.classList.remove('is--opened');
                        tw.style.overflow = 'hidden';
                        tw.style.height = '0px';
                        tw.style.transition = 'height 0.35s cubic-bezier(0.2, 0.8, 0.2, 1)';
                        var heading = acc.querySelector('.accordion_heading');
                        if (heading) heading.style.cursor = 'pointer';
                    });
                    wrap.addEventListener('click', function (e) {
                        var heading = e.target.closest('.accordion_heading');
                        if (!heading || !wrap.contains(heading)) return;
                        var cur = heading.closest('.accordion');
                        var curTw = cur && cur.querySelector('.accordion_text-wrap');
                        if (!curTw) return;
                        var isOpen = cur.classList.contains('is--opened');
                        if (isOpen) {
                            curTw.style.height = curTw.scrollHeight + 'px';
                            requestAnimationFrame(function () { curTw.style.height = '0px'; });
                            cur.classList.remove('is--opened');
                        } else {
                            accs.forEach(function (a) {
                                if (a !== cur && a.classList.contains('is--opened')) {
                                    var oTw = a.querySelector('.accordion_text-wrap');
                                    if (oTw) {
                                        oTw.style.height = oTw.scrollHeight + 'px';
                                        requestAnimationFrame(function () { oTw.style.height = '0px'; });
                                    }
                                    a.classList.remove('is--opened');
                                }
                            });
                            curTw.style.height = curTw.scrollHeight + 'px';
                            cur.classList.add('is--opened');
                            setTimeout(function () {
                                if (cur.classList.contains('is--opened')) curTw.style.height = 'auto';
                            }, 380);
                        }
                    });
                });
            });
        </script>
        <link rel="stylesheet" href="../css/swiper-bundle.min.css"/>
        <script src="../js/swiper-bundle.min.js"></script>
        <script src="../js/proof-stats.js" defer></script>
        <!-- Contact form side-preview animation engine. Drives the agency-readiness
             mockup (rotating focus card, progress bars, donut percentages). -->
        <script src="../js/air-quire-mocks.js" defer></script>"""


EMBED_RESET_BLOCK = """        <!-- w-embed inline reset. Restores link/button defaults and the +/- /
             arrow accordion-icon rotations the rest of the site relies on. -->
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
                .accordion.is--opened .accordion_icon {
                    color: var(--_tokenization---text-black);
                }
                .accordion.is--opened .vertical_faq-icon {
                    transform: rotate(90deg);
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
                html {
                    font-size: calc(0.625rem + 0.41666666666666663vw);
                }
                @media screen and (max-width: 1920px) {
                    html { font-size: calc(0.625rem + 0.41666666666666674vw); }
                }
                @media screen and (max-width: 1440px) {
                    html { font-size: calc(-0.5rem + 1.6666666666666665vw); }
                }
                @media screen and (max-width: 1200px) {
                    html { font-size: calc(0.39114832535885163rem + 0.47846889952153115vw); }
                }
                @media screen and (max-width: 991px) {
                    html { font-size: calc(0.758056640625rem + 0.390625vw); }
                }
                @media screen and (max-width: 479px) {
                    html { font-size: calc(0.7494769874476988rem + 0.8368200836820083vw); }
                }
            </style>
        </div>"""


def _strip_em_dashes(text: str) -> str:
    """Replace user-visible em dashes (U+2014) with periods/commas/and per project rule."""
    # Targeted replacements for known phrases in the included contact form section.
    repls = [
        ("we evolve with you — adding capabilities", "we evolve with you, adding capabilities"),
        ("A no-pitch fit assessment — straight to the point", "A no-pitch fit assessment. Straight to the point"),
        ("with a fit assessment — not a sales pitch", "with a fit assessment, not a sales pitch"),
        ("Thanks — we received your inquiry", "Thanks. We received your inquiry"),
        ("HUD — AMSS Acquisition", "HUD. AMSS Acquisition"),
        ("SEC — Exam Modernization", "SEC. Exam Modernization"),
        ("CMS — Cloud migration", "CMS. Cloud migration"),
        ("USDA — WIC food delivery", "USDA. WIC food delivery"),
    ]
    for old, new in repls:
        text = text.replace(old, new)
    # Project policy: no em dashes anywhere in the page output, even in HTML
    # comments. Sweep any remaining occurrences.
    text = text.replace('—', '.')
    return text


def build_page(svc: dict) -> str:
    """Compose the full page HTML for one service."""
    head = build_head(svc)
    glossar = build_glossar_section(svc)
    other_services = build_other_services_section(svc["slug"])
    bottom_cta = build_bottom_cta_section(svc)

    # Service pages live at /services/*.html so they're one folder deep; image
    # paths in the popup template need a "../" prefix to reach /images/.
    popup_leave_html = POPUP_LEAVE_HTML.replace("{{PREFIX}}", "../")

    # Contact form section intentionally not stamped here. See CONTACT_FORM_SECTION
    # comment above for history. Service pages flow: glossar -> other-services -> bottom CTA.
    page = f"""{head}
    <body>
{EMBED_RESET_BLOCK}
        <!-- TEMPLATE:header:START -->
        <!-- TEMPLATE:header:END -->
        <main>
{glossar}
{other_services}
{bottom_cta}
        </main>
        <!-- TEMPLATE:footer:START -->
        <!-- TEMPLATE:footer:END -->

{popup_leave_html}

{POPUP_MAGNET_HTML}

{build_scripts_block()}

{POPUP_JS}
    </body>
</html>
"""
    # Final sweep: strip every em dash from the entire page (project policy).
    page = page.replace('—', '.')
    return page


def main() -> int:
    services_dir = ROOT / "services"
    for svc in SERVICES:
        out_path = services_dir / f"{svc['slug']}.html"
        page = build_page(svc)
        out_path.write_text(page, encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)}  ({len(page.splitlines())} lines)")
    print(f"\nDone. Now run: python3 scripts/apply_templates.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
