#!/usr/bin/env python3
"""
NPS (Nila Pro Services), static site generator.

Plain Python, no dependencies. Run `python3 build.py` to regenerate every
.html file in the repo root from the content defined below.

Why a generator instead of 22 hand-edited HTML files?
  - The header, nav, footer and CTA band stay identical everywhere.
  - Adding a service = one dict entry, not one new file + 21 nav edits.
The *output* is still 100% plain static HTML/CSS/JS, no build step is
required to deploy, and you can hand-edit the generated files if you prefer.
"""

import html
import json
import re
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# SITE CONFIG ,  edit this block first
# ============================================================================

SITE = {
    "name": "NPS",
    "legal_name": "NPS",
    # The registered entity name is deliberately not used in marketing copy.
    # Privacy and Terms name it once each, which counsel will normally want.
    "legal_entity": "Nila Pro Services",
    "domain": "https://nilaproservices.com",
    "tagline": "Security advisory for companies that can't afford to guess.",
    "email": "info@nilaproservices.com",
    "address_1": "924 US Highway 9, Suite 311",
    "address_2": "South Amboy, New Jersey 08879",
    "linkedin": "https://www.linkedin.com/company/nilapro/",
    "booking_url": ("https://outlook.office.com/bookwithme/user/0b69000b72af40f3869df745aac995f6@nilaproservices.com/meetingtype/fz1tXex6vUOMyihW7K7jKA2?anonymous&amp;ismsaljsauthenabled&amp;ep=mCardFromTile"),
    # The contact form posts to FormSubmit, which relays the message to the
    # address below. No account, no server. The FIRST submission triggers a
    # confirmation email to info@ that must be clicked once to activate the
    # endpoint; after that it just works.
    "form_action": "https://formsubmit.co/info@nilaproservices.com",

    # PREVIEW MODE. True adds <meta name="robots" content="noindex,nofollow"> to
    # every page and a blanket Disallow in robots.txt, which is useful while
    # drafting. False is the live setting.
    "preview_mode": False,

    # Case studies are written but hidden. The content stays in CASE_STUDIES
    # below; flip this to True to bring back the nav link, the footer link,
    # the home page section and the individual pages.
    "show_case_studies": False,

    # ---- Analytics -------------------------------------------------------
    # Paste your GA4 Measurement ID here (Admin -> Data Streams -> Web -> it
    # looks like "G-XXXXXXXXXX"). Leave it empty and no analytics code is
    # emitted at all: no script tag, no cookie banner, no third-party request.
    "ga_measurement_id": "G-0TWWXMD13Z",

    # Hostnames where analytics must NOT run. Local previews are excluded
    # already. Once the site is live on nilaproservices.com, add
    # "sahasraja.github.io" here so staging traffic stops mixing into the
    # real numbers. Matching is on the end of the hostname.
    "analytics_exclude_hosts": ["localhost", "127.0.0.1", "", "sahasraja.github.io"],
}

# -- CONTENT ------------------------------------------------------------------
# Everything below is real and confirmed.

METRICS = [  # Confirmed accurate by RK, 4 Sep 2026.
    ("20<em>+</em>", "Years leading security programs across regulated industries"),
    ("60<em>+</em>", "Audits, assessments and certifications guided to completion"),
    ("9", "Compliance frameworks operated end to end, not just advised on"),
    ("100<em>%</em>", "Engagements led by a senior practitioner, never handed to juniors"),
]

CLIENT_LOGOS = ["Revalgo.AI", "Engaiz", "Morphis Inc", "Excelencia",
                "Katpro", "99yards", "Cloudcreek", "1Trooper"]  # TODO: confirm permission to name each

# None yet. Real quotes only, in writing, with approved attribution. Anonymized
# attribution such as "Director of IT, regional manufacturer" is fine.
TESTIMONIALS = []

# ============================================================================
# ICONS  (inline SVG, stroke-based, 24x24 viewbox)
# ============================================================================

def _svg(paths, extra=""):
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + extra + ">"
        + paths + "</svg>"
    )

ICONS = {
    "shield": _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>'),
    "compass": _svg('<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5.5-5.5 2 2-5.5 5.5-2Z"/>'),
    "clipboard": _svg('<path d="M9 3h6v3H9z"/><path d="M15 4.5h2.5A1.5 1.5 0 0 1 19 6v13.5A1.5 1.5 0 0 1 17.5 21h-11A1.5 1.5 0 0 1 5 19.5V6a1.5 1.5 0 0 1 1.5-1.5H9"/><path d="m8.5 13 2 2 4.5-4.5"/>'),
    "layers": _svg('<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>'),
    "code": _svg('<path d="m9 8-5 4 5 4"/><path d="m15 8 5 4-5 4"/>'),
    "cpu": _svg('<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M10 10h4v4h-4z"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/>'),
    "radar": _svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12 18 6"/>'),
    "handshake": _svg('<circle cx="6" cy="6.5" r="2.6"/><circle cx="18" cy="6.5" r="2.6"/>'
                      '<circle cx="12" cy="18" r="2.6"/><path d="M7.6 8.6 10.6 16"/>'
                      '<path d="m16.4 8.6-3 7.4"/><path d="M8.6 6.5h6.8"/>'),
    "check": _svg('<path d="m4.5 12.5 5 5 10-11"/>'),
    "arrow": _svg('<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>'),
    "plus": _svg('<path d="M12 5v14M5 12h14"/>'),
    "chev": _svg('<path d="m6 9 6 6 6-6"/>'),
    "menu": _svg('<path d="M4 7h16M4 12h16M4 17h16"/>', ' class="ico-open"'),
    "close": _svg('<path d="m6 6 12 12M18 6 6 18"/>', ' class="ico-close"'),
    "mail": _svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>'),
    "phone": _svg('<path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 5.2 2 2 0 0 1 6 3Z"/>'),
    "pin": _svg('<path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>'),
    "clock": _svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.2 2"/>'),
    "calendar": _svg('<rect x="3.5" y="5" width="17" height="15" rx="2.5"/>'
                     '<path d="M3.5 10h17M8 3.5v3M16 3.5v3"/><path d="m9.5 14.5 1.6 1.6 3.4-3.4"/>'),
    "linkedin": _svg('<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7.5 10.5V17M7.5 7.4v.1M11.5 17v-3.6a2.4 2.4 0 0 1 4.8 0V17"/>'),
    "github": _svg('<path d="M9 19c-4 1.5-4-2.5-6-3m12 5v-3.9a3.4 3.4 0 0 0-.9-2.6c3-.3 6.1-1.5 6.1-6.6a5.1 5.1 0 0 0-1.4-3.5 4.8 4.8 0 0 0-.1-3.6s-1.1-.3-3.7 1.4a12.6 12.6 0 0 0-6.6 0C5.8 1 4.7 1.3 4.7 1.3a4.8 4.8 0 0 0-.1 3.6A5.1 5.1 0 0 0 3.2 8.4c0 5.1 3.1 6.3 6.1 6.6a3.4 3.4 0 0 0-.9 2.6V21"/>'),
    "lock": _svg('<rect x="4.5" y="10" width="15" height="10.5" rx="2"/><path d="M8 10V7.5a4 4 0 0 1 8 0V10"/>'),
    "users": _svg('<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19.5a5.5 5.5 0 0 1 11 0"/><path d="M16 5.6a3.2 3.2 0 0 1 0 6.2"/><path d="M17.5 14.6a5.5 5.5 0 0 1 3 4.9"/>'),
    "chart": _svg('<path d="M4 20V4"/><path d="M4 20h16"/><path d="m8 16 3.5-4.5 3 2.5L20 7"/>'),
    "doc": _svg('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>'),
}


def icon(name, cls=""):
    svg = ICONS[name]
    if cls:
        svg = svg.replace("<svg ", '<svg class="%s" ' % cls, 1)
    return svg


# ============================================================================
# SERVICES
# ============================================================================

SERVICES = [
    {
        "slug": "virtual-ciso",
        "icon": "shield",
        "title": "Virtual &amp; Fractional CISO",
        "short": "Embedded security leadership",
        "menu_desc": "Senior security ownership without a full-time hire.",
        "summary": "A named senior security leader who owns your program: strategy, roadmap, "
                   "budget, board reporting and vendor management, all at the fraction of a "
                   "full-time hire that your stage actually needs.",
        "problem_head": "You need a CISO's judgment, not a CISO's salary",
        "problem": [
            "Security decisions are landing on an engineering leader who already has a full job, "
            "or on nobody at all.",
            "Customers and insurers are asking who owns security, and the honest answer is "
            "“everyone a little.”",
            "The board wants a straight answer on risk and the room can only produce a tool list.",
        ],
        "does": [
            "Own the security program end to end with a named, accountable senior leader",
            "Build and maintain a 12–18 month roadmap tied to business milestones, not tool releases",
            "Run the security governance cadence: risk register, exceptions, metrics, steering reviews",
            "Present risk to the board, investors, insurers and enterprise customers in their language",
            "Set security budget and defend it with a defensible cost-of-risk argument",
            "Manage security vendors, MSSPs and pen test partners so they earn their invoice",
            "Stand up policy, standards and the operating rhythm that makes them stick",
            "Coach and level up your internal engineers into real security owners",
        ],
        "deliverables": [
            ("Security program charter", "Scope, authority, RACI and decision rights, agreed with your executive team"),
            ("Risk register + treatment plan", "Ranked, owned, dated, with the accepted risks written down on purpose"),
            ("12–18 month roadmap", "Sequenced by risk reduction per dollar, mapped to your funding cycle"),
            ("Board / customer reporting pack", "A repeatable deck and metric set you can run without us"),
            ("Policy and standards set", "Written to be followed, mapped to the frameworks you are held to"),
            ("Quarterly program review", "What moved, what didn't, what changes next quarter and why"),
        ],
        "engagements": [
            ("Fractional CISO", "Ongoing", "A recurring commitment, typically 2 to 6 days a month, with standing exec presence."),
            ("Interim CISO", "3–12 months", "Full-time coverage through a departure, a crisis or a funding event."),
            ("CISO advisory", "Retainer", "Your internal leader keeps the title; we're the bench they call."),
        ],
    },
    {
        "slug": "risk-strategy",
        "icon": "compass",
        "title": "Cyber Risk &amp; Security Strategy",
        "short": "Know what actually matters",
        "menu_desc": "Assess, prioritize and sequence, in business terms.",
        "summary": "An honest read of where you stand, what could actually hurt you, and the "
                   "shortest sequence of work that reduces the most risk. Written for executives, "
                   "detailed enough for engineers.",
        "problem_head": "A tool inventory is not a risk picture",
        "problem": [
            "You have findings from three assessments and no agreement on what to do first.",
            "Spend is going up and nobody can say what risk went down.",
            "“Critical” has stopped meaning anything because everything is critical.",
        ],
        "does": [
            "Run a control and capability assessment against NIST CSF 2.0, CIS Controls or ISO 27001",
            "Model the handful of scenarios that would genuinely damage the business",
            "Quantify exposure in dollars and downtime, not red-amber-green",
            "Build a single ranked risk register that survives contact with your executive team",
            "Sequence remediation by risk reduced per dollar and per engineering week",
            "Produce a costed multi-year roadmap tied to your budget and hiring plan",
            "Define the metrics that prove the program is working",
            "Rationalize an overlapping security tool stack and cut what isn't earning its keep",
        ],
        "deliverables": [
            ("Current-state assessment", "Capability maturity by domain, with the evidence behind every score"),
            ("Scenario risk analysis", "The 5–8 events that matter, with likelihood, impact and current coverage"),
            ("Ranked risk register", "One list, one owner per item, one date, no parallel spreadsheets"),
            ("Costed roadmap", "Phased 12–36 months with dependencies, effort and expected risk reduction"),
            ("Executive briefing", "A 20-minute version your CEO and board can act on"),
            ("Metrics baseline", "The starting numbers you will be measured against next quarter"),
        ],
        "engagements": [
            ("Rapid diagnostic", "2–3 weeks", "Fast, focused read on posture with a top-ten action list."),
            ("Full assessment", "4–8 weeks", "Framework-based assessment, scenario modeling and costed roadmap."),
            ("Strategy retainer", "Ongoing", "Quarterly reassessment and roadmap stewardship as the business changes."),
        ],
    },
    {
        "slug": "compliance",
        "icon": "clipboard",
        "title": "Compliance &amp; Audit Readiness",
        "short": "SOC 2, ISO 27001, HIPAA, CMMC",
        "menu_desc": "Certification and audit programs run end to end.",
        "summary": "We run the certification, not just advise on it: scoping, control design, "
                   "evidence, auditor management and the operating rhythm that keeps you compliant "
                   "in year two without another fire drill.",
        "problem_head": "Compliance is blocking revenue, and the deadline is real",
        "problem": [
            "A customer contract or an investor is gating on SOC 2, ISO 27001 or HIPAA attestation.",
            "You bought a compliance automation platform and discovered it doesn't do the work for you.",
            "Last year's audit was survived, not run, and nobody wants to repeat it.",
        ],
        "does": [
            "Scope the audit honestly: the right systems, the right boundary, the right trust criteria",
            "Perform gap analysis against the target framework with a remediation plan you can staff",
            "Design controls that fit how your team actually works, so they survive year two",
            "Write the policy set, procedures and system description",
            "Build the evidence pipeline and automate collection where it is worth automating",
            "Configure and actually operate Vanta, Drata, Secureframe or your GRC platform of choice",
            "Select and manage the auditor, and run the fieldwork so your engineers stay shipping",
            "Handle customer security questionnaires, CAIQ, HECVAT and enterprise vendor reviews",
        ],
        "deliverables": [
            ("Readiness assessment", "Gap-by-control view with effort estimates and a critical path to audit date"),
            ("Control set and policy library", "Mapped across every framework you carry, written once"),
            ("Evidence system", "Owners, cadence, automation and a repository the auditor can walk"),
            ("Auditor management", "Selection, scoping, fieldwork coordination and finding response"),
            ("Trust package", "Public trust page content, security whitepaper and standard questionnaire answers"),
            ("Sustainment plan", "The annual calendar that keeps the certificate without the fire drill"),
        ],
        "engagements": [
            ("Readiness sprint", "3–6 weeks", "Gap analysis, scoping and a costed plan to your audit date."),
            ("Certification program", "3–9 months", "We run the whole thing from kickoff to clean report."),
            ("Sustainment retainer", "Annual", "Continuous monitoring, evidence upkeep and surveillance audits."),
        ],
        "frameworks": ["SOC 2 Type I &amp; II", "ISO/IEC 27001:2022", "ISO/IEC 27701", "ISO/IEC 42001",
                       "HIPAA / HITECH", "HITRUST", "CMMC Level 1 &amp; 2", "NIST SP 800-171",
                       "NIST CSF 2.0", "PCI DSS 4.0", "GDPR", "CCPA / CPRA", "FedRAMP readiness",
                       "TX-RAMP / StateRAMP"],
    },
    {
        "slug": "security-architecture",
        "icon": "layers",
        "title": "Security Architecture &amp; Engineering",
        "short": "Identity, cloud and Zero Trust",
        "menu_desc": "Design and build the controls, not just the diagram.",
        "summary": "Architecture reviews and hands-on engineering across identity, cloud and network "
                   ",  with reference designs your team can actually implement and a Zero Trust "
                   "path that doesn't require replacing everything at once.",
        "problem_head": "The diagram and the deployment stopped matching a long time ago",
        "problem": [
            "Cloud footprint grew faster than the guardrails around it.",
            "Identity sprawl means nobody can answer “who can reach production?” in under a day.",
            "Every Zero Trust proposal so far has been a procurement plan wearing a strategy costume.",
        ],
        "does": [
            "Review cloud architecture across Azure, AWS and GCP against a hardened reference design",
            "Design identity and access architecture: Entra ID, Okta, conditional access, PAM, joiner-mover-leaver",
            "Build a staged Zero Trust roadmap sequenced by blast-radius reduction",
            "Segment networks and workloads without stalling delivery",
            "Design data protection: classification, encryption, key management, DLP that people don't route around",
            "Codify guardrails as policy-as-code and landing zone patterns your platform team owns",
            "Harden Microsoft 365, Google Workspace and the SaaS estate nobody is watching",
            "Review and secure OT / IoT boundaries where they touch the corporate network",
        ],
        "deliverables": [
            ("Architecture review", "Findings ranked by blast radius, each with a concrete design fix"),
            ("Target-state reference architecture", "Diagrams plus the decisions and trade-offs behind them"),
            ("Identity blueprint", "Access model, privileged path, lifecycle automation and break-glass design"),
            ("Zero Trust roadmap", "Phased, tool-agnostic, with what to do before buying anything"),
            ("Guardrail code", "Policy-as-code, landing zone and baseline configuration your team maintains"),
            ("Implementation support", "We stay through build and validation, not just design"),
        ],
        "engagements": [
            ("Architecture review", "2–4 weeks", "Deep review of one domain: cloud, identity or network."),
            ("Design and build", "6–16 weeks", "Target-state design plus hands-on implementation with your team."),
            ("Embedded architect", "Ongoing", "A senior architect in your design reviews and change process."),
        ],
    },
    {
        "slug": "product-security",
        "icon": "code",
        "title": "Product &amp; Application Security",
        "short": "Secure the thing you sell",
        "menu_desc": "Threat modeling, secure SDLC and pen test programs.",
        "summary": "Security built into the product your customers buy: threat modeling, a secure "
                   "SDLC engineers don't resent, dependency and supply chain control, and a pen test "
                   "program that produces fixes instead of PDFs.",
        "problem_head": "Enterprise buyers are auditing your product, not your policies",
        "problem": [
            "Security review is the longest step in your enterprise sales cycle.",
            "The last pen test produced a 60-page report and four actual fixes.",
            "Multi-tenant isolation is “fine” but nobody has written down why.",
        ],
        "does": [
            "Threat model the architecture and the features that carry the most risk (STRIDE / PASTA)",
            "Review multi-tenant isolation and authorization logic, the failure mode that ends companies",
            "Design a secure SDLC with gates that fit your release cadence, not against it",
            "Stand up SAST, DAST, SCA and secrets scanning tuned to a signal-to-noise ratio engineers accept",
            "Build supply chain controls: dependency policy, SBOM, artifact signing, build integrity",
            "Run the pen test program: scoping, vendor selection, triage, retest and closure",
            "Review against OWASP ASVS / SAMM and produce a maturity path",
            "Prepare the security artefacts that unblock enterprise procurement"
        ],
        "deliverables": [
            ("Threat model", "Trust boundaries, abuse cases and ranked mitigations for your real architecture"),
            ("Application security assessment", "Code, configuration and design review with reproducible findings"),
            ("Secure SDLC design", "Gates, tooling, ownership and the exception path that keeps it honest"),
            ("Pipeline implementation", "Scanning wired into CI with triage rules and burn-down"),
            ("Pen test program", "Vendor, scope, cadence, remediation SLAs and retest discipline"),
            ("Buyer trust package", "Architecture overview, data flow, control narrative and questionnaire answers"),
        ],
        "engagements": [
            ("Threat model sprint", "1–3 weeks", "One product or one critical feature, modeled and ranked."),
            ("AppSec program build", "8–16 weeks", "SDLC, tooling, training and pen test program stood up."),
            ("Embedded AppSec", "Ongoing", "Design reviews, triage and engineer coaching on a standing basis."),
        ],
    },
    {
        "slug": "ai-governance",
        "icon": "cpu",
        "title": "AI Governance &amp; Secure AI Adoption",
        "short": "Move fast on AI, defensibly",
        "menu_desc": "Governance, threat modeling and controls for AI systems.",
        "summary": "A governance model that lets your teams ship AI instead of waiting for permission "
                   ",  built on NIST AI RMF and ISO 42001, with real controls for model, data and "
                   "agent risk rather than a policy nobody reads.",
        "problem_head": "AI is already in production; the governance is not",
        "problem": [
            "Teams are shipping LLM features and legal found out from the changelog.",
            "Customers are sending AI-specific security questionnaires you can't yet answer.",
            "Nobody can say what data leaves the building through which model, on what terms.",
        ],
        "does": [
            "Inventory AI use across the business: including the shadow usage that already exists",
            "Stand up an AI governance framework on NIST AI RMF and ISO/IEC 42001",
            "Define an intake and risk-tiering process that approves low-risk use in days, not quarters",
            "Threat model AI systems: prompt injection, data leakage, model and agent abuse (OWASP LLM Top 10)",
            "Set data handling rules for training, fine-tuning, RAG corpora and vendor retention terms",
            "Review AI vendor and model contracts for the terms that actually matter",
            "Design controls for agentic systems: tool permissions, human-in-the-loop, blast radius, audit trail",
            "Prepare for the AI clauses now appearing in SOC 2, ISO and enterprise customer reviews",
        ],
        "deliverables": [
            ("AI use inventory", "What's running, who owns it, what data it touches, what the exposure is"),
            ("AI governance framework", "Policy, standards, risk tiers and the approval path, mapped to ISO 42001"),
            ("AI threat models", "Per high-risk system, with mitigations and residual risk written down"),
            ("Control set for AI", "Data, model, prompt, output and agent controls that engineering can implement"),
            ("Vendor review standard", "The questions and contract terms to require of every AI vendor"),
            ("Customer-facing AI trust content", "Answers to the AI questionnaire before it arrives"),
        ],
        "engagements": [
            ("AI risk baseline", "2–4 weeks", "Inventory, risk tiering and the top exposures with fixes."),
            ("Governance build", "6–12 weeks", "Full framework, intake process and control set operationalised."),
            ("ISO 42001 program", "4–9 months", "Certification-track AI management system, run end to end."),
        ],
    },
    {
        "slug": "security-operations",
        "icon": "radar",
        "title": "Security Operations &amp; Incident Response",
        "short": "Detect, respond, recover",
        "menu_desc": "Detection engineering, IR readiness and MSSP oversight.",
        "summary": "Detection that fires on what matters, an incident response plan that has been "
                   "tested under pressure, and enough oversight of your MSSP that you know what "
                   "you're paying for.",
        "problem_head": "You'll find out how good your response is at the worst possible time",
        "problem": [
            "The IR plan exists as a PDF and has never been run.",
            "Your MSSP sends a monthly report and you have no way to judge it.",
            "Alert volume is high, alert value is unknown, and the team has learned to ignore it.",
        ],
        "does": [
            "Assess detection coverage against MITRE ATT&amp;CK and close the gaps that matter",
            "Engineer detections and tune the noise out of SIEM, EDR and cloud logs",
            "Design log strategy and retention that satisfies both investigators and the finance team",
            "Write an incident response plan with real playbooks, roles and decision authority",
            "Run tabletop exercises for executives, and technical exercises for responders",
            "Build the ransomware playbook: including the decisions you want made before the day",
            "Evaluate, onboard and hold your MSSP or MDR provider to a measurable standard",
            "Align business continuity and disaster recovery with tested, timed recovery objectives",
        ],
        "deliverables": [
            ("Detection coverage map", "ATT&amp;CK-mapped view of what you'd catch and what you'd miss"),
            ("Tuned detection content", "Rules, thresholds and enrichment that cut false positives measurably"),
            ("Incident response plan", "Roles, severity model, comms tree, legal and regulatory triggers"),
            ("Playbook library", "Ransomware, BEC, cloud compromise, insider, third-party breach"),
            ("Tabletop exercise + report", "Facilitated, scored, with a corrective action list"),
            ("MSSP scorecard", "The metrics and SLAs to hold your provider to, reviewed quarterly"),
        ],
        "engagements": [
            ("IR readiness review", "2–4 weeks", "Plan, playbooks and one facilitated tabletop."),
            ("SOC uplift", "8–16 weeks", "Detection engineering, tuning and process build with your team."),
            ("Response retainer", "Ongoing", "Standing senior support for incidents and post-incident review."),
        ],
    },
    {
        "slug": "third-party-risk",
        "icon": "handshake",
        "title": "Third-Party &amp; M&amp;A Security Due Diligence",
        "short": "Security risk you inherit",
        "menu_desc": "Vendor security programs and cyber diligence on deals.",
        "summary": "This is the security half of diligence, not the financial, tax or "
                   "commercial half. A vendor security program that scales past a spreadsheet, "
                   "and cyber due diligence on acquisitions, so you find out what you are "
                   "buying before the wire clears rather than after integration.",
        "problem_head": "Most of your risk now sits on someone else's infrastructure",
        "problem": [
            "Vendor reviews are a questionnaire nobody reads, filed by nobody in particular.",
            "You're acquiring a company and have two weeks to judge its security debt.",
            "A fourth-party outage took you down and you had no idea the dependency existed.",
        ],
        "does": [
            "Build a tiered vendor risk program proportionate to actual data and access exposure",
            "Run assessments on critical vendors, including the ones already embedded",
            "Set security requirements and contract language: DPAs, right to audit, breach notice, SLAs",
            "Map concentration and fourth-party dependency risk",
            "Perform pre-close security due diligence on acquisition targets",
            "Quantify remediation cost and integration risk as a deal input",
            "Plan post-close integration: identity merge, network join, control harmonization",
            "Support divestiture and carve-out separation without leaving doors open",
            "Work alongside your financial, tax and legal diligence teams, covering the security scope only",
        ],
        "deliverables": [
            ("Vendor risk program", "Tiering model, assessment workflow, SLAs and the reassessment calendar"),
            ("Critical vendor assessments", "Findings and required remediation per vendor, with contract hooks"),
            ("Contract security schedule", "Reusable language your legal team can drop into every agreement"),
            ("Diligence report", "Target's posture, material findings and quantified remediation cost"),
            ("Integration plan", "Day-1, day-30 and day-90 security actions with owners"),
            ("Concentration risk map", "Where a single third or fourth party would take you down"),
        ],
        "engagements": [
            ("TPRM program build", "4–8 weeks", "Program design, tooling and first wave of assessments."),
            ("Deal diligence", "1–3 weeks", "A focused cyber review delivered inside the timetable the deal sets."),
            ("Integration support", "3–6 months", "Post-close security integration run alongside your team."),
        ],
    },
]

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}

# ============================================================================
# DOMAIN MAP  (the coverage grid shown on the home page and in the hero panel)
# ============================================================================

DOMAINS = [
    ("GOV", "Governance &amp; Risk", "Policy, risk register, board reporting, exceptions"),
    ("CMP", "Compliance &amp; Audit", "SOC 2, ISO 27001, HIPAA, CMMC, evidence"),
    ("IAM", "Identity &amp; Access", "SSO, MFA, PAM, joiner-mover-leaver, machine identity"),
    ("DAT", "Data Protection", "Classification, encryption, key management, DLP"),
    ("APP", "Product &amp; AppSec", "Threat modeling, secure SDLC, dependency and supply chain"),
    ("CLD", "Cloud &amp; Platform", "Landing zone, posture management, policy as code"),
    ("NET", "Network &amp; Segmentation", "Zero Trust, segmentation, egress control, telemetry"),
    ("END", "Endpoint &amp; Device", "EDR, patching, privilege, configuration baseline"),
    ("DET", "Detection &amp; Response", "Logging, detection engineering, IR, MSSP oversight"),
    ("RES", "Resilience &amp; Recovery", "BC, DR, backup integrity, tested recovery objectives"),
    ("TPR", "Third-Party Risk", "Tiering, assessment, contract terms, concentration risk"),
    ("AIG", "AI Governance", "Inventory, risk tiering, model and agent controls"),
]

# ============================================================================
# INDUSTRIES
# ============================================================================

INDUSTRIES = [
    ("Healthcare &amp; Life Sciences", "lock",
     "HIPAA and HITRUST, connected medical devices, clinical system uptime, and business associate risk across a sprawling vendor base.",
     ["HIPAA Security Rule", "HITRUST CSF", "FDA premarket cybersecurity", "42 CFR Part 2"]),
    ("Financial Services", "chart",
     "Examiner-ready programs, third-party concentration risk, and controls that hold up under regulatory scrutiny rather than just internal review.",
     ["GLBA Safeguards", "NYDFS Part 500", "FFIEC CAT", "PCI DSS 4.0"]),
    ("Technology &amp; SaaS", "code",
     "Enterprise buyers auditing your product. Multi-tenant isolation, SOC 2 and ISO 27001, and a security story that shortens the sales cycle.",
     ["SOC 2 Type II", "ISO 27001", "OWASP ASVS", "Customer security review"]),
    ("Government &amp; Defense", "shield",
     "CMMC Level 1 and 2, CUI enclave design, and the evidence discipline that survives a real assessment rather than a self-attestation.",
     ["CMMC 2.0", "NIST SP 800-171", "FedRAMP readiness", "DFARS 7012"]),
    ("Manufacturing &amp; Industrial", "layers",
     "IT/OT boundary security, ransomware resilience where downtime is measured in shifts, and supply chain requirements flowing down from primes.",
     ["IEC 62443", "NIST CSF 2.0", "CMMC flow-down", "OT segmentation"]),
    ("Professional &amp; Legal Services", "doc",
     "Client confidentiality obligations, outside counsel guidelines, and the security requirements your largest clients now impose contractually.",
     ["ISO 27001", "Client OCG compliance", "SOC 2", "Data residency"]),
    ("Energy &amp; Utilities", "radar",
     "Critical infrastructure resilience, regulator expectations, and OT environments that were never designed to be connected.",
     ["NERC CIP", "TSA directives", "IEC 62443", "NIST CSF 2.0"]),
    ("Education", "users",
     "Student data protection, research security obligations, and a decentralised IT reality that makes central policy hard to enforce.",
     ["FERPA", "GLBA Safeguards", "NIST SP 800-171", "Research security"]),
    ("Retail &amp; eCommerce", "cpu",
     "Payment security, fraud and account takeover, and a martech stack quietly moving customer data to places nobody approved.",
     ["PCI DSS 4.0", "CCPA / CPRA", "GDPR", "Fraud controls"]),
    ("Nonprofit &amp; NGO", "handshake",
     "Grant and donor data obligations, funder security requirements, and meaningful risk reduction on a budget that has no slack.",
     ["Donor data protection", "Grant requirements", "NIST CSF 2.0", "Cyber insurance"]),
]

# ============================================================================
# CASE STUDIES
# ============================================================================
# None yet. When real engagements are approved for publication, add them here as
# dicts with: slug, tag, title, teaser, facts, challenge, approach, outcome, quote
# (see the archived shape in the project notes), then set
# SITE["show_case_studies"] = True.

CASE_STUDIES = []

# ============================================================================
# GUIDES  (framework roadmaps)
# ============================================================================
# Facts checked against primary and legal sources on 4 September 2026. The CMMC
# guide in particular reflects the 13 July 2026 Phase 2 suspension; recheck
# before making claims about dates.

GUIDES = [
    {
        "slug": "soc-2-roadmap",
        "code": "SOC 2",
        "title": "The road to a SOC 2 report",
        "eyebrow": "SOC 2 Type I and Type II",
        "teaser": "What the year actually looks like, where the time really goes, and the "
                  "five ways companies turn a four-month project into a fourteen-month one.",
        "read": "9 min read",
        "summary": "SOC 2 is an attestation, not a certification. A CPA firm examines whether "
                   "the controls you described were designed properly and, for a Type II, "
                   "whether they operated over a period of time. Nobody grants you a "
                   "certificate. You get a report, and your customers read it.",
        "who": [
            "A customer contract or a security review is gating on it, with a date attached",
            "You sell software or a service that holds someone else's data",
            "You are between roughly 20 and 500 people and this is your first time",
            "You have bought a compliance automation platform and the percentage is not moving",
        ],
        "callout": ("Type I or Type II?",
                    "Type I says the controls were designed properly on one date. Type II says "
                    "they actually operated over a window, usually three to twelve months. "
                    "Enterprise buyers want Type II. Type I is worth doing only when you need "
                    "something to show a buyer within weeks and you are committed to the Type II "
                    "immediately after. Doing Type I as an end in itself buys you a document "
                    "most procurement teams will not accept."),
        "phases": [
            ("Scope the audit", "2 to 4 weeks",
             "Decide which systems, which trust services criteria and which entity are in scope. "
             "This single decision drives cost, effort and duration more than anything else "
             "you will do. Security is mandatory; Availability, Confidentiality, Processing "
             "Integrity and Privacy are each optional and each adds real work.",
             "A written scope and boundary, agreed with your executive team, and a defensible "
             "reason for every system left out."),
            ("Gap assessment", "2 to 3 weeks",
             "Compare current practice against the criteria in scope. Split findings three ways: "
             "audit-blocking, deal-blocking, and neither. Only the first two earn engineering time "
             "before the audit.",
             "A ranked remediation plan with owners, effort estimates and a critical path to your "
             "target report date."),
            ("Remediate and design controls", "4 to 12 weeks",
             "Build the controls that are missing and redesign the ones that exist but would not "
             "survive fieldwork. Design them around how your team already works, or you will be "
             "fighting them every quarter for years.",
             "Working controls, a policy set written to be followed, and a named human owner for "
             "every control who can explain it out loud."),
            ("Operate through the observation window", "3 to 12 months",
             "This is the part nobody can compress. For a Type II, the auditor examines evidence "
             "across a period. Three months is the shortest window most auditors will accept; six "
             "to twelve is what enterprise buyers prefer to see. The window starts when the "
             "controls genuinely operate, not when you decide it starts.",
             "Continuous evidence: access reviews performed, tickets closed, alerts triaged, "
             "onboarding and offboarding records, change approvals."),
            ("Auditor fieldwork", "3 to 6 weeks",
             "The auditor samples evidence, interviews control owners and tests operating "
             "effectiveness. Your job here is logistics and fast, accurate answers. Engineers "
             "should be involved only where they are genuinely needed.",
             "Requested evidence delivered on time, exceptions understood before they are written "
             "down, and management responses drafted for anything that lands."),
            ("Report and sustain", "2 to 4 weeks, then annual",
             "The report issues. Then the real question: will year two be a repeat of year one, "
             "or a routine? That is decided by whether evidence is produced by working normally "
             "or by a quarterly scramble.",
             "The report, a customer-facing trust package, and an annual calendar that keeps the "
             "next one boring."),
        ],
        "time_sinks": [
            "The observation window. It is calendar time and no amount of money shortens it.",
            "Access reviews across every in-scope system, done properly rather than as a signature on a CSV export.",
            "Vendor management, because SOC 2 asks about your subservice organizations and most companies have never listed them.",
            "The system description, a narrative document that auditors judge and customers read, and that no platform generates for you.",
            "Waiting for an auditor with capacity, which in Q4 can be six weeks on its own.",
        ],
        "artifacts": [
            ("Scope and boundary document", "What is in, what is out, and the reasoning for both"),
            ("Policy set", "Written to match reality, not a downloaded template library"),
            ("Risk assessment", "Documented, dated, and revisited, because the auditor will ask when you last did it"),
            ("System description", "The narrative at the front of the report describing your service and its controls"),
            ("Evidence repository", "Organized so an auditor can walk it without a guide"),
            ("Vendor inventory", "Subservice organizations, what they do, and their own reports"),
            ("Management assertion", "Your formal statement that the description is fair and controls operated"),
        ],
        "failures": [
            ("Scoping by accident",
             "Nobody makes a deliberate decision about the boundary, so the whole corporate estate "
             "ends up in scope. The control surface roughly doubles, the evidence load doubles with "
             "it, and the customer gets no additional assurance for any of it."),
            ("Believing the platform is the program",
             "Vanta, Drata and Secureframe collect evidence continuously and that is genuinely "
             "useful. None of them can scope an audit, design a control, write the system "
             "description or argue with an auditor. The dashboard goes green while the program "
             "underneath is not defensible."),
            ("Starting the window too early",
             "The observation period begins and the controls are not really operating yet. Three "
             "months later the sample comes back with gaps, and the choice is a qualified report "
             "or restarting the clock."),
            ("Treating the system description as boilerplate",
             "It is the part of the report your customers actually read. A vague or inaccurate one "
             "undermines an otherwise clean opinion, and a customer who spots the gap between the "
             "description and reality will ask about it."),
            ("Choosing the auditor on price alone",
             "The cheapest quote is often a firm that will sample lightly and issue quickly. That "
             "feels efficient until an enterprise buyer's security team recognizes the name and "
             "discounts the report."),
        ],
        "cost_drivers": [
            "Number of trust services criteria beyond Security",
            "Number of in-scope systems and cloud environments",
            "Length of the observation window",
            "Whether you have any control ownership internally, or none",
            "Headcount, because auditors price partly on the size of the population they sample",
        ],
        "faqs": [
            ("How long does it really take, start to finish?",
             "For a first Type II with a three-month window and controls that mostly do not exist "
             "yet: six to nine months. With a twelve-month window: twelve to fifteen. A Type I "
             "alone can be done in three to four months. Anyone promising a Type II in eight weeks "
             "is either selling a Type I or planning to start the window before the controls work."),
            ("Do we need a compliance platform?",
             "Not strictly, but by year two you will want one. Automated evidence collection turns "
             "the annual repeat from a project into a routine. Buy it for what it does, which is "
             "the evidence pipeline, and do not expect it to make the judgment calls."),
            ("What does it cost?",
             "The audit fee is usually the smaller number. Readiness work, remediation and the "
             "internal time to operate controls typically exceed it several times over. Be "
             "suspicious of any proposal that quotes only the audit."),
            ("Can we reuse this for ISO 27001?",
             "Substantially, yes. The control sets overlap heavily and the evidence often serves "
             "both. Carrying two frameworks should not mean maintaining two control sets, and if "
             "you know both are coming, map once at the start rather than twice."),
        ],
    },
    {
        "slug": "iso-27001-roadmap",
        "code": "ISO 27001",
        "title": "The road to ISO/IEC 27001:2022 certification",
        "eyebrow": "ISO/IEC 27001:2022",
        "teaser": "A management system, not a control checklist. What the standard actually "
                  "requires, why Stage 1 audits fail, and the records auditors ask for that "
                  "nobody thinks to keep.",
        "read": "10 min read",
        "summary": "ISO 27001 certifies a management system. The 93 controls in Annex A get most "
                   "of the attention, but they are the appendix. Clauses 4 through 10 are the "
                   "standard, and they are where certification is won or lost.",
        "who": [
            "You sell into Europe, the UK, or to enterprises that ask for ISO rather than SOC 2",
            "You want a certificate rather than an attestation report",
            "You already hold SOC 2 and want to reuse the work",
            "You are being asked for ISO by a customer who will not accept anything else",
        ],
        "callout": ("The 2013 version is gone",
                    "The transition window closed on 31 October 2025. Certificates against "
                    "ISO/IEC 27001:2013 are no longer valid, and every new or renewed certificate "
                    "is against the 2022 revision: 93 Annex A controls organized into four themes "
                    "rather than 114 across fourteen domains. If a supplier shows you a 2013 "
                    "certificate today, it has expired."),
        "phases": [
            ("Define scope and context", "3 to 5 weeks",
             "Clauses 4 and 5. Determine the boundary of the management system, identify "
             "interested parties and their requirements, and secure genuine leadership "
             "commitment. A scope statement that is too broad is the most expensive mistake "
             "available at this stage, and it is nearly impossible to narrow later.",
             "A written scope statement, context analysis, and an information security policy "
             "signed by top management."),
            ("Risk assessment and Statement of Applicability", "4 to 6 weeks",
             "Clause 6. Establish a repeatable risk methodology, run it, and produce a risk "
             "treatment plan. The Statement of Applicability then records all 93 Annex A controls "
             "with a decision and a justification for each, including the ones you exclude.",
             "A risk register with owners and treatment decisions, and an SoA you can defend "
             "line by line."),
            ("Build the management system", "6 to 12 weeks",
             "Clause 7 and the Annex A controls you have accepted. Policies, procedures, "
             "competence and awareness, documented information control. This is the bulk of the "
             "build, and the point where most organizations discover their existing documentation "
             "does not meet the requirement.",
             "A working ISMS: policies people follow, defined roles, training records, and "
             "controlled documents with version history."),
            ("Operate and generate records", "3 to 6 months",
             "Clause 8 and 9. The system has to run and produce evidence. Auditors will ask what "
             "you did, when, and who approved it. Records created retrospectively are visible as "
             "such and will be treated accordingly.",
             "Operational records, monitoring results, and measurable objectives with actual "
             "measurements against them."),
            ("Internal audit and management review", "3 to 5 weeks",
             "Clause 9.2 and 9.3. Both are mandatory and both must happen before Stage 2. The "
             "internal audit must be performed by someone independent of the area being audited, "
             "which usually means not the person who built the ISMS.",
             "An internal audit report with findings, corrective actions raised and closed, and "
             "management review minutes covering every required input."),
            ("Stage 1 audit", "1 to 2 days, then 4 to 8 weeks",
             "The certification body reviews your documentation and readiness. Failures here are "
             "almost always missing management system records rather than missing technical "
             "controls. You then get a gap to close whatever they found.",
             "A Stage 1 report and a corrective action plan for anything raised."),
            ("Stage 2 audit and certification", "3 to 5 days",
             "The full assessment of implementation and effectiveness. Findings are graded as "
             "minor or major nonconformities; majors must be closed before the certificate "
             "issues.",
             "The certificate, valid three years, with surveillance audits in years one and two "
             "and recertification in year three."),
        ],
        "time_sinks": [
            "The risk assessment, done properly rather than as a spreadsheet completed in an afternoon.",
            "The Statement of Applicability, because 93 justifications is genuinely a lot of writing.",
            "Accumulating operational records, which is calendar time and cannot be compressed.",
            "Internal audit, which needs a competent and independent person you may not have.",
            "Certification body scheduling, which can add six to ten weeks if you leave it late.",
        ],
        "artifacts": [
            ("Scope statement", "The boundary of the ISMS, precise enough to appear on the certificate"),
            ("Information security policy", "Approved by top management, not by IT"),
            ("Risk assessment methodology and register", "Repeatable, documented, with owners and treatment decisions"),
            ("Statement of Applicability", "All 93 Annex A controls, each included or excluded with justification"),
            ("Risk treatment plan", "What you are doing about the risks you did not accept"),
            ("Objectives and measurements", "Security objectives with actual numbers against them"),
            ("Internal audit program and reports", "Independent, covering the whole ISMS over the cycle"),
            ("Management review minutes", "Covering every input the standard lists"),
            ("Corrective action records", "Findings raised, root cause, action, verification"),
        ],
        "failures": [
            ("Treating Annex A as the standard",
             "Teams implement 93 controls beautifully and fail Stage 1 because there is no "
             "management review, no internal audit, and no evidence the risk assessment drove any "
             "of it. Clauses 4 to 10 are the certifiable part."),
            ("A scope statement written too wide",
             "Certifying the whole organization when the customer only cares about one platform "
             "multiplies the audit, the evidence and the ongoing burden. Narrowing scope after "
             "certification means a new scope and effectively starting over."),
            ("Copying someone else's Statement of Applicability",
             "The SoA has to reflect your risk assessment. An auditor who finds justifications "
             "that do not match your own risk register has found a systemic problem, not a "
             "paperwork one."),
            ("Internal audit performed by the ISMS owner",
             "Clause 9.2 requires objectivity and impartiality. Auditing your own work is a "
             "nonconformity in itself, regardless of how well the audit was done."),
            ("Retrospective records",
             "A year of management review minutes written the week before Stage 2 is obvious to "
             "anyone who has audited before. The dates, the language and the absence of any "
             "disagreement all give it away."),
        ],
        "cost_drivers": [
            "Scope: number of locations, legal entities and systems included",
            "Headcount, which drives certification body audit days directly",
            "How much documented management system already exists",
            "Whether you need an external internal auditor",
            "Certification body choice, where accreditation matters more than price",
        ],
        "faqs": [
            ("How long from a standing start?",
             "Six to twelve months for most organizations. Under six is possible only where a "
             "real management system already exists and only the ISO framing is missing. The "
             "floor is set by needing enough operational records to audit."),
            ("Is ISO 27001 harder than SOC 2?",
             "Different, not harder. SOC 2 asks whether your controls worked. ISO asks whether "
             "you have a system that decides which controls you need, checks that it is working, "
             "and improves itself. The documentation burden is heavier; the technical bar is "
             "often lower."),
            ("Can one program cover both ISO 27001 and SOC 2?",
             "Yes, and it should. The control overlap is substantial and most evidence serves "
             "both. Run the risk assessment and control design once, map to both, and collect "
             "evidence once. Doing them as separate projects is the expensive way."),
            ("What is the difference between accredited and unaccredited certification?",
             "An accredited certificate comes from a body overseen by a national accreditation "
             "authority. An unaccredited one is a company's opinion. Sophisticated buyers check, "
             "and the price difference is not worth the risk of being caught with a certificate "
             "that does not count."),
            ("What happens after we are certified?",
             "Surveillance audits in years one and two, recertification in year three, and the "
             "management system has to keep running throughout. The certificate can be suspended "
             "if surveillance finds the ISMS has stopped operating."),
        ],
    },
    {
        "slug": "cmmc-roadmap",
        "code": "CMMC",
        "title": "The road to CMMC, and what the Phase 2 suspension changed",
        "eyebrow": "CMMC Level 1 and Level 2",
        "teaser": "The certification timeline moved. The obligations did not. What defense "
                  "contractors actually have to do right now, and why pausing your program "
                  "would be the expensive reading of the news.",
        "read": "11 min read",
        "summary": "CMMC verifies something that has been contractually required since 2017. "
                   "DFARS 252.204-7012 already obliges contractors handling covered defense "
                   "information to implement all 110 controls in NIST SP 800-171. CMMC was the "
                   "mechanism to check. The checking has been paused; the requirement has not.",
        "who": [
            "You hold or bid on DoD contracts containing DFARS 252.204-7012",
            "A prime contractor has flowed CMMC requirements down to you",
            "You handle Federal Contract Information or Controlled Unclassified Information",
            "You paused your CMMC program after July 2026 and are wondering whether that was right",
        ],
        "callout_alert": ("Phase 2 was suspended on 13 July 2026",
                          "The Department of War suspended CMMC Phase 2 effective immediately, "
                          "halting the 10 November 2026 move to third-party C3PAO assessments, "
                          "and opened a review of the program. What did not change: DFARS "
                          "252.204-7012, all 110 NIST SP 800-171 controls, annual affirmations, "
                          "SPRS scoring, incident reporting, and flow-down to subcontractors. "
                          "Level 1 and Level 2 self-assessment obligations remain in force. "
                          "Contractors who stop work now will face the same requirements later "
                          "with less time, and misrepresenting a SPRS score carries False Claims "
                          "Act exposure whether or not anyone is coming to assess it."),
        "phases": [
            ("Determine what you actually hold", "2 to 4 weeks",
             "Federal Contract Information and Controlled Unclassified Information are different "
             "things with different obligations. FCI means Level 1 and 15 basic safeguarding "
             "requirements from FAR 52.204-21. CUI means Level 2 and all 110 controls. Read your "
             "contracts rather than assuming.",
             "A contract-by-contract determination of FCI and CUI, with the clauses that "
             "triggered each."),
            ("Map where CUI lives and moves", "3 to 6 weeks",
             "Follow it: email, file shares, engineering workstations, the ERP, the contract "
             "manager's laptop, the shop floor. This is the single highest-leverage activity in "
             "the whole program, because every system CUI touches falls in scope.",
             "A data flow map and an honest inventory of every system, person and process that "
             "handles CUI."),
            ("Design the boundary", "4 to 8 weeks",
             "Decide whether to bring the whole company into scope or build an enclave that CUI "
             "lives inside. For most small and mid-sized suppliers the enclave is dramatically "
             "cheaper, and the decision to build one is usually worth more than the entire rest "
             "of the engagement.",
             "A defensible system boundary, an architecture for the enclave, and a documented "
             "shared responsibility split with any cloud or managed provider."),
            ("Implement the 110 controls", "3 to 9 months",
             "NIST SP 800-171 across access control, audit, configuration, identification and "
             "authentication, incident response, maintenance, media protection, personnel, "
             "physical, risk, security assessment, communications and system integrity. Some are "
             "technical, many are procedural, and the procedural ones are the ones that get "
             "skipped.",
             "Implemented controls with evidence, and honest scoring rather than optimistic "
             "scoring."),
            ("SSP, POA&M and SPRS", "3 to 5 weeks, then continuous",
             "The System Security Plan documents how each control is met. The POA&M covers what "
             "is not yet met, with dates. The score goes into the Supplier Performance Risk "
             "System. Note that not every control can sit on a POA&M, and the ones that cannot "
             "are the ones assessors look at first.",
             "A current SSP, a POA&M with real dates, and a SPRS score you can defend line by "
             "line to someone hostile."),
            ("Self-assess and affirm", "2 to 3 weeks, then annual",
             "Phase 1 requirements are active: self-assessment and an annual affirmation from a "
             "senior official. Level 2 self-assessments continue every three years with annual "
             "affirmation. The affirmation is a signed statement, and that signature is what "
             "creates personal exposure if the score is wrong.",
             "A completed assessment, a submitted affirmation, and the evidence to support both."),
            ("Prepare for third-party assessment", "When Phase 2 resumes",
             "C3PAO assessment is paused, not cancelled. Organizations that keep their evidence "
             "current will need a mock assessment and a short readiness pass. Organizations that "
             "stopped will be starting the implementation again against a shorter runway.",
             "A mock assessment against the same criteria a C3PAO would use, and gaps closed "
             "before anyone external looks."),
        ],
        "time_sinks": [
            "Finding CUI, which is always in more places than anyone expects, particularly email and personal drives.",
            "The procedural controls, which need written procedures and evidence people follow them, not just technology.",
            "Segmenting operational technology without stopping production, where change windows are measured in shifts.",
            "Getting a straight answer from an MSP about which controls they cover and which are yours.",
            "Documenting the SSP properly, which is a substantial writing exercise and cannot be delegated to a tool.",
        ],
        "artifacts": [
            ("CUI and FCI determination", "Which contracts, which clauses, which data"),
            ("Data flow map", "Where CUI enters, lives, moves and leaves"),
            ("System Security Plan", "How each of the 110 controls is met, in your environment"),
            ("POA&M", "What is not met, who owns it, when it closes"),
            ("SPRS score and submission", "Calculated honestly, with the working shown"),
            ("Annual affirmation", "Signed by a senior official who understands what they signed"),
            ("Shared responsibility matrix", "What your cloud and managed providers cover, in writing"),
            ("Incident response plan", "With the 72-hour DFARS reporting obligation built in"),
        ],
        "failures": [
            ("Never defining the boundary",
             "Without a deliberate CUI enclave, the entire company falls in scope: every laptop, "
             "every server, every user. The cost difference between a scoped enclave and a "
             "whole-company implementation is routinely five to one."),
            ("Assuming your cloud provider covers you",
             "A FedRAMP authorized service is a component of your compliance, not a substitute "
             "for it. The controls that remain yours are numerous, and the shared responsibility "
             "split needs to be documented rather than assumed."),
            ("Using the POA&M as a parking lot",
             "Not every control is eligible to be deferred, and a POA&M loaded with the ones that "
             "are not is the fastest way to fail. Dates that have already slipped once are read "
             "as an indicator of everything else."),
            ("An inflated SPRS score",
             "Scoring generously feels harmless while nobody is checking. The affirmation is a "
             "signed representation to the government, and False Claims Act cases have already "
             "been brought on exactly this. The suspension of assessments does not suspend that "
             "exposure."),
            ("Treating the July 2026 suspension as a stand-down",
             "The obligations survived intact. The organizations that keep going will be ready "
             "when Phase 2 resumes and can say so to primes in the meantime, which is itself "
             "becoming a discriminator in flow-down decisions."),
        ],
        "cost_drivers": [
            "Whether you scope an enclave or bring the whole company in",
            "How much CUI has spread into email and unmanaged endpoints",
            "Whether operational technology touches the same network",
            "Existing maturity against NIST SP 800-171, which is usually lower than assumed",
            "Level 1 versus Level 2, which is 15 requirements versus 110",
        ],
        "faqs": [
            ("Should we pause our CMMC program after the suspension?",
             "No. Third-party assessment is paused; nothing else is. DFARS 252.204-7012, the 110 "
             "controls, self-assessment, annual affirmation, SPRS scoring, incident reporting and "
             "subcontractor flow-down all remain in force. Pausing means facing the same "
             "requirements later with a shorter runway, while carrying the same legal exposure in "
             "the meantime."),
            ("What is the difference between Level 1 and Level 2?",
             "Level 1 applies to Federal Contract Information and requires the 15 basic "
             "safeguarding requirements in FAR 52.204-21, self-assessed annually. Level 2 applies "
             "to Controlled Unclassified Information and requires all 110 NIST SP 800-171 "
             "controls. The gap between them is very large."),
            ("How long does Level 2 take?",
             "Nine to eighteen months for most suppliers starting from a typical commercial IT "
             "baseline. Scoping an enclave shortens it considerably. The implementation of "
             "procedural controls, not the technical ones, is usually the long pole."),
            ("Can our MSP just handle this?",
             "Partly. An MSP can implement and operate many technical controls, but the "
             "obligation stays with you, the SSP is yours to defend, and the affirmation is "
             "signed by your senior official. Get the shared responsibility split in writing "
             "before you rely on it."),
            ("What happens when Phase 2 resumes?",
             "Third-party C3PAO assessment returns for the contracts that require it. The "
             "practical difference between organizations at that point will be whether they have "
             "current evidence or a two-year gap in their records."),
        ],
    },
]

# ============================================================================
# INSIGHTS
# ============================================================================

INSIGHTS = [
    {
        "slug": "compliance-automation-is-not-a-program",
        "tag": "Compliance",
        "date": "2026-07-14",
        "date_display": "July 14, 2026",
        "read": "6 min read",
        "title": "Your compliance automation platform is a scoreboard, not a team",
        "teaser": "Vanta and Drata are genuinely good products. They also cannot design a control, "
                  "scope an audit, or argue with an auditor, and the gap between those two facts "
                  "is where most failed certifications live.",
        "body": [
            ("p", "Every few weeks we meet a company that bought a compliance automation platform "
                  "nine months ago, watched the percentage climb into the eighties, and then "
                  "discovered that the auditor did not care about the percentage."),
            ("p", "This is not a criticism of the tools. Automated evidence collection is a real "
                  "advance, and doing SOC 2 without it now feels like doing accounting on paper. "
                  "The problem is a category error: the platform measures whether a control is "
                  "producing evidence. It cannot tell you whether the control was the right one, "
                  "whether your scope is defensible, or whether the system description matches the "
                  "system."),
            ("h2", "What the platform genuinely does"),
            ("ul", ["Collects evidence continuously from systems it can integrate with",
                    "Tracks control status and flags drift",
                    "Gives you a policy template library and a place to store attestations",
                    "Reduces the year-two burden substantially once the program is correct"]),
            ("h2", "What it does not do"),
            ("p", "Scoping is the first and largest one. The platform inherits whatever boundary you "
                  "give it. We have seen companies bring their entire corporate estate into a SOC 2 "
                  "scope because nobody made a deliberate decision about the audit boundary, "
                  "roughly doubling the control surface, the evidence load and the cost, for zero "
                  "additional customer assurance."),
            ("p", "Control design is the second. A template policy says access is reviewed quarterly. "
                  "Whether your access review is a meaningful check or a rubber stamp on a CSV export "
                  "is a design question, and it is the question an experienced auditor asks in "
                  "fieldwork. The dashboard shows green either way."),
            ("p", "The third is the system description, the narrative document at the front of a "
                  "SOC 2 report describing what your service actually does and how it is controlled. "
                  "It is written by you, judged by the auditor, and read by your customers. No "
                  "platform generates it, and a weak one undermines an otherwise clean report."),
            ("h2", "The pattern that works"),
            ("p", "Use the platform for what it is good at, and put a person in front of it who has "
                  "been through the audit before. Concretely: decide scope deliberately and write "
                  "down why; design controls against how your team actually works before configuring "
                  "them; assign every control a human owner who can explain it out loud; and treat "
                  "the platform as the evidence pipeline rather than the program."),
            ("p", "The companies that sail through year two are the ones where the control set fits "
                  "the operating reality. The ones that struggle are the ones where the dashboard "
                  "went green before anyone asked whether the controls made sense."),
        ],
    },
    {
        "slug": "ai-governance-that-does-not-block-shipping",
        "tag": "AI Governance",
        "date": "2026-06-23",
        "date_display": "June 23, 2026",
        "read": "7 min read",
        "title": "AI governance that doesn't turn into a permission queue",
        "teaser": "Most AI governance frameworks fail the same way: every use case gets the same "
                  "review, the queue backs up, and teams route around it. Risk tiering is the fix, "
                  "and it is not complicated.",
        "body": [
            ("p", "The failure mode is predictable. Legal and security, reasonably alarmed, stand up "
                  "an AI review process. Every proposed use goes through the same intake. The intake "
                  "takes six weeks. Within a quarter, half the AI in the company is running outside "
                  "the process, because a marketing team summarising public documents is not going to "
                  "wait six weeks for the same review as a model making clinical recommendations."),
            ("p", "Governance that people route around is worse than no governance, because it "
                  "produces the illusion of control plus the reality of shadow usage."),
            ("h2", "Tier by consequence, not by technology"),
            ("p", "The useful variable is not which model or which vendor. It is what happens when "
                  "the system is wrong, and what data it can reach. A workable three-tier split:"),
            ("ul", ["<strong>Low</strong>: public or internal non-sensitive data, human reviews every output, no automated action. Self-service registration, no review. Approve in a day.",
                    "<strong>Medium</strong>: confidential data, or output that materially informs a human decision. Lightweight structured review against a checklist. Days, not weeks.",
                    "<strong>High</strong>: regulated or personal data, automated action without a human in the loop, safety or legal consequence, or external-facing autonomy. Full threat model, named accountable owner, monitoring and a kill switch."]),
            ("p", "Most usage lands in the low tier. That is the point: it frees your reviewers to "
                  "spend real time on the ten percent that deserves it."),
            ("h2", "The controls that matter for agentic systems"),
            ("p", "Agents change the calculus, because the blast radius is no longer the answer text "
                  ",  it is whatever the tools can do. Scope tool permissions to the minimum, and "
                  "scope them per agent rather than per platform. Require human confirmation for any "
                  "irreversible or externally visible action. Log the full chain: prompt, tool "
                  "calls, arguments, results. You cannot investigate what you did not "
                  "record. And test with adversarial inputs, since prompt injection through retrieved "
                  "content is the practical attack, not the theoretical one."),
            ("h2", "Map to a framework so it survives audit"),
            ("p", "NIST AI RMF gives you the functions and language. ISO/IEC 42001 gives you a "
                  "certifiable management system if customers are starting to ask. OWASP's LLM Top 10 "
                  "gives your engineers a concrete threat list. You do not need all three on day one, "
                  "but pick one to anchor on early, retrofitting structure onto an improvised "
                  "process costs more than starting with it."),
            ("p", "The test of an AI governance program is not whether it has a policy. It is whether "
                  "the fastest path to shipping an AI feature runs through the process rather than "
                  "around it."),
        ],
    },
    {
        "slug": "questions-a-board-should-ask",
        "tag": "Security Leadership",
        "date": "2026-05-19",
        "date_display": "May 19, 2026",
        "read": "5 min read",
        "title": "Six questions a board should ask, and what a good answer sounds like",
        "teaser": "“Are we secure?” is unanswerable and everyone in the room knows it. "
                  "These six are answerable, and the quality of the answer tells you more than any "
                  "maturity score.",
        "body": [
            ("p", "Board security reporting has a bad equilibrium. The board asks a question that "
                  "cannot be answered honestly, the security lead responds with a heat map, and "
                  "everyone leaves slightly less informed than they arrived. Better questions produce "
                  "better programs, so here are six that work."),
            ("h2", "1. What are the three events that would hurt us most, and what would they cost?"),
            ("p", "A good answer is specific and quantified: named scenarios, a dollar and downtime "
                  "estimate, and the reasoning behind the estimate. A weak answer lists threat "
                  "categories such as ransomware, insider or nation-state, without connecting any of "
                  "them to your business."),
            ("h2", "2. Which risks have we deliberately accepted?"),
            ("p", "Every organization accepts risk. A healthy program has a written, dated, owned list "
                  "of accepted risks reviewed on a schedule. If the answer is “none,” the "
                  "acceptance is happening informally, which means nobody senior has actually agreed "
                  "to it."),
            ("h2", "3. If we were compromised right now, how long until we knew?"),
            ("p", "Look for a number derived from actual detection coverage and tested response, not a "
                  "vendor's marketing figure. “We don't know” is an acceptable first answer "
                  "if it comes with a plan to find out."),
            ("h2", "4. What did last quarter's spend buy us in risk reduction?"),
            ("p", "This is the question that separates a program from a procurement habit. A good "
                  "answer ties spend to specific movement on specific risks. A weak answer lists tools "
                  "deployed."),
            ("h2", "5. Which third parties could take us down?"),
            ("p", "Expect a short, ranked list with the dependency named, and ideally an answer "
                  "about fourth parties too. Most organizations discover their concentration risk "
                  "during someone else's outage."),
            ("h2", "6. What would you fix if I gave you unbudgeted money tomorrow?"),
            ("p", "The most revealing question of the six. If the answer is immediate and specific, "
                  "there is a real prioritized plan behind it. If it takes a week to produce, the "
                  "prioritization does not exist yet."),
            ("h2", "The meta-question"),
            ("p", "Notice that none of these ask for a maturity score, a framework percentage or a "
                  "color. Those are useful internal instruments and poor governance instruments. "
                  "Boards govern by understanding consequence, ownership and trade-off, and "
                  "security is not special in that respect."),
        ],
    },
]

# ============================================================================
# FAQ
# ============================================================================

FAQS = [
    ("How is this different from hiring a security consultancy?",
     "Two things. First, the person who scopes your engagement is the person who does the work, "
     "there is no pyramid where a partner sells and an analyst delivers. Second, we operate programs "
     "rather than just recommending them. If we tell you to build a control, we will help you build "
     "it and stay through the first audit cycle."),
    ("We're small. Are we too early for this?",
     "Usually not, but the shape changes. A 30-person company does not need a governance committee; "
     "it needs the four or five controls that remove most of its real exposure and an honest answer "
     "for its enterprise customers. We scope to your stage. If the right advice is “do three "
     "things and call us in a year,” that is what you will get."),
    ("What does a first conversation look like?",
     "Thirty minutes, no deck. You describe what triggered the call: a customer requirement, an "
     "audit date, an incident, a board question. Then we tell you what we would do about it and "
     "roughly what it takes. If we are not the right fit, we will say so and point you somewhere "
     "better."),
    ("Can you work alongside our existing MSSP or IT provider?",
     "Yes, and often that is the point. Your MSSP monitors and responds; they are generally not "
     "accountable for your risk decisions, your compliance posture or your architecture. We fill that "
     "gap and hold the provider to a measurable standard on your behalf."),
    ("Do you actually implement, or only advise?",
     "Both. Assessments and strategy are how most engagements start, but our architecture, AppSec and "
     "operations work is hands-on, building the guardrails, wiring the pipeline, tuning the "
     "detections, sitting in the design review. Advice that stops at the recommendation is where most "
     "security money is wasted."),
    ("How do you charge?",
     "Three ways, chosen to fit the work. Fixed fee for scoped projects like assessments and "
     "certification programs. A monthly retainer for ongoing work such as fractional CISO or "
     "embedded architecture. And hourly for advisory support that is genuinely open-ended, where "
     "pretending to know the scope in advance would only cost you money. Whichever applies, the "
     "rate and the shape of the engagement are agreed in writing before we start."),
]

# ============================================================================
# TEMPLATE PARTS
# ============================================================================

LOGO_IMG = (
    '<img class="brand-mark" src="/assets/img/logo.png" '
    'srcset="/assets/img/logo.png 1x, /assets/img/logo@2x.png 2x, /assets/img/logo@3x.png 3x" '
    'width="123" height="76" alt="NPS" decoding="async">'
)


def nav_menu():
    items = []
    for s in SERVICES:
        items.append(
            '<a class="menu-item" href="/services/%s.html">%s<span class="visually-hidden"></span>'
            '<span><b>%s</b><span>%s</span></span></a>'
            % (s["slug"], icon(s["icon"], "ico"), s["title"], s["menu_desc"])
        )
    return "".join(items)


def header_html(active):
    def cls(key):
        return ' is-active' if active == key else ''
    cases_nav = ('      <a class="nav-link%s" href="/case-studies.html">Case Studies</a>\n' % cls('cases')
                 if SITE.get("show_case_studies") else '')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="{SITE['name']} home">
      {LOGO_IMG}
      <span class="brand-rule" aria-hidden="true"></span>
      <span class="brand-sub">Security<br>Advisory</span>
    </a>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="primary-nav">
      {icon('menu')}{icon('close')}
    </button>
    <nav class="nav" id="primary-nav" aria-label="Primary">
      <div class="has-menu">
        <a class="nav-link{cls('services')}" href="/services.html">Services {icon('chev', 'chev')}</a>
        <div class="menu">{nav_menu()}</div>
      </div>
      <a class="nav-link{cls('industries')}" href="/industries.html">Industries</a>
      <a class="nav-link{cls('guides')}" href="/guides.html">Guides</a>
{cases_nav}      <a class="nav-link{cls('insights')}" href="/insights.html">Insights</a>
      <a class="nav-link{cls('about')}" href="/about.html">About</a>
      <a class="btn btn-primary btn-sm header-cta" data-cta="header" href="{SITE['booking_url']}" rel="noopener">Book a call</a>
    </nav>
  </div>
</header>"""


def footer_html():
    cases_foot = ('          <li><a href="/case-studies.html">Case studies</a></li>\n'
                  if SITE.get("show_case_studies") else '')
    svc_links = "".join(
        '<li><a href="/services/%s.html">%s</a></li>' % (s["slug"], s["title"]) for s in SERVICES[:6]
    )
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="/" aria-label="{SITE['name']} home">
          {LOGO_IMG}
          <span class="brand-rule" aria-hidden="true"></span>
          <span class="brand-sub">Security<br>Advisory</span>
        </a>
        <p style="margin-top:16px">Senior cybersecurity advisory, compliance and security
        engineering for organizations that are held to a standard.</p>
        <div class="social">
          <a href="{SITE['linkedin']}" aria-label="LinkedIn" rel="noopener">{icon('linkedin')}</a>
          <a href="mailto:{SITE['email']}" aria-label="Email">{icon('mail')}</a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        <ul>{svc_links}<li><a href="/services.html">All services</a></li></ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="/about.html">About</a></li>
          <li><a href="/industries.html">Industries</a></li>
          <li><a href="/guides.html">Guides</a></li>
{cases_foot}          <li><a href="/insights.html">Insights</a></li>
          <li><a href="/contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
          <li><a href="{SITE['booking_url']}" rel="noopener">Book a call</a></li>
          <li style="color:var(--text-3)">{SITE['address_1']}<br>{SITE['address_2']}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> {SITE['legal_name']}. All rights reserved.</span>
      <nav aria-label="Legal">
        <a href="/privacy.html">Privacy</a>
        <a href="/terms.html">Terms</a>
        <a href="/contact.html">Contact</a>
      </nav>
    </div>
  </div>
</footer>"""


def cta_band(head="Start with a straight conversation",
             body="Thirty minutes, no deck, no pitch. Tell us what prompted the call and we will "
                  "tell you what we would do about it, including when the answer is that you "
                  "do not need us yet.",
             primary=("Book a call", None), secondary=("See our services", "/services.html")):
    p_href = primary[1] or SITE["booking_url"]
    sec = ""
    if secondary:
        sec = '<a class="btn btn-ghost" href="%s">%s</a>' % (secondary[1], secondary[0])
    return f"""<section class="section">
  <div class="wrap">
    <div class="cta-band reveal">
      <h2>{head}</h2>
      <p>{body}</p>
      <div class="btn-row" style="margin-top:28px">
        <a class="btn btn-primary" data-cta="cta-band" href="{p_href}">{primary[0]} {icon('arrow')}</a>
        {sec}
      </div>
    </div>
  </div>
</section>"""


def relativise(doc, depth):
    """Rewrite root-relative links (href="/x") into path-relative ones.

    This is what lets the same build work at https://nilaproservices.com/ AND at
    https://sahasraja.github.io/NPS/ (a project-Pages subpath) with no config.
    `https://` and `mailto:` are untouched because they never match `="/`.
    """
    prefix = "../" * depth
    doc = doc.replace('href="/"', 'href="%sindex.html"' % prefix)
    doc = doc.replace('href="/', 'href="%s' % prefix)
    doc = doc.replace('src="/', 'src="%s' % prefix)

    def _srcset(m):
        cands = []
        for c in m.group(1).split(","):
            c = c.strip()
            cands.append(prefix + c[1:] if c.startswith("/") else c)
        return 'srcset="%s"' % ", ".join(cands)

    doc = re.sub(r'srcset="([^"]+)"', _srcset, doc)
    return doc


def page(path, title, description, body, active="", schema=None, canonical=None):
    canon = canonical or (SITE["domain"] + "/" + path.lstrip("/"))
    if canon.endswith("/index.html"):
        canon = canon[: -len("index.html")]
    robots_meta = ('<meta name="robots" content="noindex,nofollow">\n'
                   '<!-- PREVIEW MODE: set SITE["preview_mode"] = False before launch -->'
                   if SITE.get("preview_mode") else
                   '<meta name="robots" content="index,follow">')
    ga_id = SITE.get("ga_measurement_id", "").strip()
    ga_block = ""
    if ga_id:
        group = "service" if path.startswith("services/") else (
                "insight" if path.startswith("insights/") else "site")
        ga_block = (
            "<script>\n"
            "  window.dataLayer = window.dataLayer || [];\n"
            "  function gtag(){dataLayer.push(arguments);}\n"
            "  gtag('consent', 'default', {\n"
            "    ad_storage: 'denied', ad_user_data: 'denied',\n"
            "    ad_personalization: 'denied', analytics_storage: 'denied',\n"
            "    wait_for_update: 500\n"
            "  });\n"
            "  try {\n"
            "    if (localStorage.getItem('nps-analytics-consent') === 'granted') {\n"
            "      gtag('consent', 'update', { analytics_storage: 'granted' });\n"
            "    }\n"
            "  } catch (e) {}\n"
            "  var npsHost = location.hostname;\n"
            "  var npsBlocked = %s.some(function (h) {\n"
            "    return h === npsHost || (h && npsHost.slice(-h.length) === h);\n"
            "  });\n"
            "  gtag('js', new Date());\n"
            "  if (!npsBlocked) {\n"
            "    gtag('config', '%s', { content_group: '%s', anonymize_ip: true });\n"
            "  }\n"
            "  window.npsAnalyticsOff = npsBlocked;\n"
            "</script>\n"
            "<script>if (!window.npsAnalyticsOff) {\n"
            "  var s = document.createElement('script'); s.async = true;\n"
            "  s.src = 'https://www.googletagmanager.com/gtag/js?id=%s';\n"
            "  document.head.appendChild(s);\n"
            "}</script>"
            % (json.dumps(SITE.get("analytics_exclude_hosts", [])), ga_id, group, ga_id)
        )
    schema_block = ""
    if schema:
        schema_block = ('<script type="application/ld+json">%s</script>'
                        % json.dumps(schema, separators=(",", ":")))
    consent_banner = ""
    if ga_id:
        consent_banner = (
            '<div class="consent" id="consent" hidden>\n'
            '  <p><b>Analytics only.</b> We use Google Analytics to see which pages get read '
            'and where visitors come from. No advertising, no profiling, no data sold. '
            'Decline and nothing is stored.</p>\n'
            '  <div class="consent-actions">\n'
            '    <button class="btn btn-primary btn-sm" data-consent="granted">Accept</button>\n'
            '    <button class="btn btn-ghost btn-sm" data-consent="denied">Decline</button>\n'
            '  </div>\n'
            '</div>'
        )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{robots_meta}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE['name']} Security Advisory">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE['domain']}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#06090F">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/assets/img/icon-512.png" sizes="512x512" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/manrope-latin-wght-normal.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/bricolage-grotesque-latin-wght-normal.woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
{ga_block}
{schema_block}
</head>
<body>
{header_html(active)}
<main id="main">
{body}
</main>
{footer_html()}
{consent_banner}
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""
    # Every booking link opens in a new tab so visitors do not lose the site.
    doc = re.sub(
        r'<a ([^>]*?)href="(https://outlook\.office\.com/bookwithme[^"]*)"([^>]*)>',
        lambda m: '<a %shref="%s"%s target="_blank" rel="noopener noreferrer">'
                  % (m.group(1), m.group(2), m.group(3).replace(' rel="noopener"', '')),
        doc)
    doc = relativise(doc, path.count("/"))
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def page_hero(crumbs, eyebrow, h1, lede, buttons=True):
    crumb_html = ""
    parts = []
    for label, href in crumbs:
        parts.append('<a href="%s">%s</a>' % (href, label) if href else "<span>%s</span>" % label)
    crumb_html = '<div class="breadcrumb">' + '<span class="sep">/</span>'.join(parts) + "</div>"
    btns = ""
    if buttons:
        btns = f"""<div class="btn-row" style="margin-top:30px">
      <a class="btn btn-primary" data-cta="page-hero" href="{SITE['booking_url']}">Book a call {icon('arrow')}</a>
      <a class="btn btn-ghost" href="/services.html">All services</a>
    </div>"""
    return f"""<section class="page-hero">
  <div class="wrap">
    {crumb_html}
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    {btns}
  </div>
</section>"""


def checks(items, cls="checks"):
    lis = "".join("<li>%s<span>%s</span></li>" % (icon("check"), i) for i in items)
    return '<ul class="%s">%s</ul>' % (cls, lis)


def faq_block(items):
    out = []
    for q, a in items:
        out.append(
            "<details><summary>%s<span class=\"plus\">%s</span></summary>"
            "<div class=\"answer\">%s</div></details>" % (q, icon("plus"), a)
        )
    return '<div class="faq">%s</div>' % "".join(out)


# ============================================================================
# PAGES
# ============================================================================

def build_home():
    metric_html = "".join(
        '<div class="metric"><div class="n">%s</div><div class="t">%s</div></div>' % (n, t)
        for n, t in METRICS
    )
    service_cards = "".join(
        f"""<a class="card card--edge" href="/services/{s['slug']}.html">
          <div class="card-ico">{icon(s['icon'])}</div>
          <h3>{s['title']}</h3>
          <p>{s['summary']}</p>
          <div class="card-foot"><span class="link-arrow">Explore {icon('arrow')}</span></div>
        </a>""" for s in SERVICES
    )
    logos = "".join("<span>%s</span>" % l for l in CLIENT_LOGOS)
    cases = "".join(
        f"""<a class="card card--edge" href="/case-studies/{c['slug']}.html">
          <span class="tag">{c['tag']}</span>
          <h3 style="margin-top:16px">{c['title']}</h3>
          <p>{c['teaser']}</p>
          <div class="card-foot"><span class="link-arrow">Read the case study {icon('arrow')}</span></div>
        </a>""" for c in CASE_STUDIES
    )
    domain_chips = "".join(
        '<span class="dcode">%s</span>' % code for code, _, _ in DOMAINS
    )
    dmap = "".join(
        '<div class="dtile"><span class="code">%s</span><span><b>%s</b><span>%s</span></span></div>'
        % (code, name, desc) for code, name, desc in DOMAINS
    )
    cases_section = ""
    if SITE.get("show_case_studies"):
        cases_section = (
            '<section class="section"><div class="wrap">'
            '<div class="section-head"><span class="eyebrow">Selected work</span>'
            '<h2>What the work actually looks like.</h2>'
            '<p>Three engagements, described the way we would describe them to you on a call.</p>'
            '</div><div class="grid grid-3">' + cases + '</div></div></section>'
        )
    framework_chips = "".join(
        '<span class="chip">%s%s</span>' % (icon("check", "tick"), f)
        for f in ["NIST CSF 2.0", "ISO/IEC 27001", "SOC 2", "HIPAA / HITRUST", "CMMC 2.0",
                  "NIST SP 800-171", "PCI DSS 4.0", "GDPR", "NIST AI RMF", "ISO/IEC 42001",
                  "CIS Controls v8", "OWASP ASVS", "MITRE ATT&amp;CK", "FedRAMP"]
    )

    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-sub">
      <div>
        <h1>Security advice from people who have actually run the program.</h1>
        <p class="lede">We are a senior cybersecurity advisory practice. We assess real risk, build
        the controls, run the certification and stay through the audit, so security stops being
        the thing that slows your business down and starts being the reason enterprise buyers say yes.</p>
        <div class="btn-row">
          <a class="btn btn-primary" data-cta="hero" href="{SITE['booking_url']}">Book a call {icon('arrow')}</a>
          <a class="btn btn-ghost" href="/services.html">See what we do</a>
        </div>
      </div>
      <div class="hero-visual">
        <div class="pulse" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="deck" aria-hidden="true">
          <div class="deck-inner">
            <div class="plane"></div><div class="plane"></div><div class="plane"></div>
          </div>
        </div>
        <div class="readout" aria-label="Illustrative security program view">
          <div class="readout-head"><span>Program view</span><span class="dot"></span></div>
          <div class="domains-label">Twelve domains, one map</div>
          <div class="domains">{domain_chips}</div>
          <div class="readout-row"><span class="label">Risk register</span><span class="value">ranked &amp; owned</span>
            <span class="bar"><i data-w="86%"></i></span></div>
          <div class="readout-row"><span class="label">Audit readiness</span><span class="value">evidence live</span>
            <span class="bar"><i data-w="74%"></i></span></div>
          <div class="readout-row"><span class="label">Detection coverage</span><span class="value">ATT&amp;CK mapped</span>
            <span class="bar"><i data-w="68%"></i></span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- PLACEHOLDER: confirm you have permission to name these organizations -->
<section class="trust">
  <div class="wrap">
    <div class="trust-label">Trusted by teams at</div>
  </div>
  <div class="trust-marquee">
    <div class="trust-track">
      <div class="trust-set">{logos}</div>
      <div class="trust-set" aria-hidden="true">{logos}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split">
      <div>
        <span class="eyebrow">Why NPS</span>
        <h2>Most security advice is written by people who have never had to live with it.</h2>
        <p class="lede">We have sat in the seat. We have owned the budget, argued with the auditor,
        briefed the board on a bad week and explained to a customer why their questionnaire answer
        is what it is. That experience is what you are buying.</p>
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn-ghost" href="/about.html">How we work {icon('arrow')}</a>
        </div>
      </div>
      <div class="grid" style="gap:16px">
        <div class="card reveal"><h3>Senior people, on your work</h3>
          <p>The person who scopes the engagement is the person who does it. No pyramid, no
          hand-off to a team you have never met.</p></div>
        <div class="card reveal"><h3>Plain language, always</h3>
          <p>If your CFO cannot follow the argument, the argument is not finished. We write for
          the decision-maker and keep the depth underneath for your engineers.</p></div>
        <div class="card reveal"><h3>We build, not just recommend</h3>
          <p>Findings are cheap. We stay through implementation, through the audit, and through
          the first cycle where you run it yourselves.</p></div>
      </div>
    </div>
  </div>
</section>

<!-- PLACEHOLDER: replace every figure below with verified numbers -->
<section class="section--tight">
  <div class="wrap">
    <div class="metrics reveal">{metric_html}</div>
  </div>
</section>

<section class="section section--alt" id="services">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What we do</span>
      <h2>Eight practices, one accountable team.</h2>
      <p>Engagements usually start in one area and grow into a program. You are never handed to a
      different firm halfway through.</p>
    </div>
    <div class="grid grid-3 reveal">{service_cards}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Coverage</span>
      <h2>Twelve domains. You choose the scope, deliberately.</h2>
      <p>Everything here is optional. What you leave out, you are choosing to accept,
      and we write that down so the decision is yours rather than an oversight.</p>
    </div>
    <div class="dmap reveal">
      {dmap}
      <div class="dtile dtile--note">
        <span class="k">Scoping in practice</span>
        <p>Under roughly 500 staff, NET, END and DET usually run as one operations
        domain. Under roughly 150, most of the value sits in GOV, CMP, IAM, DAT and
        a single operations function. Bigger is not better, matched is better.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">How an engagement runs</span>
      <h2>No mystery, no ninety-day discovery phase.</h2>
    </div>
    <div class="steps reveal">
      <div class="step"><h3>Orient</h3><p>A working session, not an interrogation. We learn what the
      business does, what is at stake, and what triggered the call. Usually one week.</p></div>
      <div class="step"><h3>Assess</h3><p>Evidence-based review of the domains in scope. You get the
      findings as we find them, no surprises saved for the final read-out.</p></div>
      <div class="step"><h3>Sequence</h3><p>A ranked plan with owners, effort and dates. Sequenced by
      risk reduced per dollar, agreed with you before anyone starts building.</p></div>
      <div class="step"><h3>Execute</h3><p>We build alongside your team, then hand over with the
      documentation and cadence that lets you run it without us.</p></div>
    </div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="split">
      <div>
        <span class="eyebrow">Frameworks we operate in</span>
        <h2>We have run these, not just read them.</h2>
        <p class="lede">Framework fluency matters less than knowing which one applies to you, how much
        of it applies, and where the overlap is. Carrying four standards should not mean four
        control sets.</p>
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn-ghost" href="/services/compliance.html">Compliance &amp; audit readiness {icon('arrow')}</a>
        </div>
      </div>
      <div class="chips reveal">{framework_chips}</div>
    </div>
  </div>
</section>

{cases_section}

<section class="section">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">Common questions</span>
      <h2>Before you get in touch.</h2>
    </div>
    {faq_block(FAQS)}
  </div>
</section>

{cta_band()}
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": SITE["legal_name"],
        "alternateName": SITE["name"],
        "url": SITE["domain"],
        "description": "Senior cybersecurity advisory, compliance and security engineering.",
        "email": SITE["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["address_1"],
            "addressLocality": "South Amboy",
            "addressRegion": "NJ",
            "postalCode": "08879",
            "addressCountry": "US",
        },
        "areaServed": "US",
        "serviceType": [s["title"].replace("&amp;", "&") for s in SERVICES],
    }
    page("index.html",
         "Cybersecurity Advisory, vCISO &amp; Compliance | NPS",
         "Senior cybersecurity advisory: virtual CISO, risk strategy, SOC 2 / ISO 27001 / HIPAA / "
         "CMMC compliance, security architecture, AppSec, AI governance and incident readiness.",
         body, active="home", schema=schema)


def build_services_index():
    cards = "".join(
        f"""<a class="card card--edge" href="/services/{s['slug']}.html">
          <div class="card-ico">{icon(s['icon'])}</div>
          <h3>{s['title']}</h3>
          <p>{s['summary']}</p>
          <div class="card-foot"><span class="link-arrow">Explore {icon('arrow')}</span></div>
        </a>""" for s in SERVICES
    )
    body = f"""
{page_hero([("Home", "/"), ("Services", None)], "Services",
           "Depth where it matters, across the whole security program.",
           "Eight practice areas that fit together. Most clients start with one: an audit "
           "deadline, a board question, an incident, and grow into a program run by the same "
           "people who did the first assessment.")}

<section class="section">
  <div class="wrap">
    <div class="grid grid-2 reveal">{cards}</div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="split">
      <div>
        <span class="eyebrow">Engagement models</span>
        <h2>Scoped so you know what you are buying.</h2>
        <p class="lede">Fixed fee for defined projects. Monthly retainer for ongoing leadership and
        embedded work. Scope, deliverables and dates written down before we start, no hourly
        billing surprises.</p>
      </div>
      <div class="table-wrap reveal">
        <table>
          <thead><tr><th>Model</th><th>Shape</th><th>Best for</th></tr></thead>
          <tbody>
            <tr><td>Diagnostic</td><td>2–4 weeks, fixed fee</td><td>You need an honest read and a ranked plan</td></tr>
            <tr><td>Program</td><td>3–9 months, fixed fee</td><td>Certification, architecture build, AppSec stand-up</td></tr>
            <tr><td>Fractional leadership</td><td>Monthly retainer</td><td>Ongoing CISO ownership without a full-time hire</td></tr>
            <tr><td>Embedded specialist</td><td>Monthly retainer</td><td>A senior architect or AppSec lead inside your team</td></tr>
            <tr><td>On-call advisory</td><td>Light retainer</td><td>You have a leader; they need a senior bench</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

{cta_band(head="Not sure which one you need?",
          body="That is a normal place to start. Describe the situation and we will tell you which "
               "of these fits, or that none of them do yet.",
          secondary=("See our insights", "/insights.html"))}
"""
    page("services.html",
         "Cybersecurity Services, vCISO, Compliance, Architecture | NPS",
         "Eight security practice areas: virtual CISO, risk strategy, compliance and audit readiness, "
         "security architecture, product security, AI governance, security operations and third-party risk.",
         body, active="services")


def build_service_pages():
    for s in SERVICES:
        others = [x for x in SERVICES if x["slug"] != s["slug"]][:3]
        related = "".join(
            f"""<a class="card card--edge" href="/services/{o['slug']}.html">
              <div class="card-ico">{icon(o['icon'])}</div>
              <h3>{o['title']}</h3><p>{o['short']}</p>
              <div class="card-foot"><span class="link-arrow">Explore {icon('arrow')}</span></div>
            </a>""" for o in others
        )
        deliverables = "".join(
            "<tr><td>%s</td><td>%s</td></tr>" % (n, d) for n, d in s["deliverables"]
        )
        engagements = "".join(
            f"""<div class="card reveal"><div class="card-num">{dur}</div>
              <h3>{name}</h3><p>{desc}</p></div>"""
            for name, dur, desc in s["engagements"]
        )
        problem_items = "".join("<li>%s<span>%s</span></li>" % (icon("check"), p) for p in s["problem"])
        fw = ""
        if s.get("frameworks"):
            chips = "".join('<span class="chip">%s%s</span>' % (icon("check", "tick"), f)
                            for f in s["frameworks"])
            fw = f"""<section class="section section--panel">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Coverage</span>
      <h2>Frameworks we take clients through.</h2>
      <p>Carrying several of these should not mean maintaining several control sets. We map once and
      reuse the evidence.</p></div>
    <div class="chips reveal">{chips}</div>
  </div>
</section>"""

        body = f"""
{page_hero([("Home", "/"), ("Services", "/services.html"), (s['title'], None)],
           s['short'], s['title'], s['summary'])}

<section class="section">
  <div class="wrap">
    <div class="split">
      <div>
        <span class="eyebrow">The situation</span>
        <h2>{s['problem_head']}</h2>
        <ul class="checks" style="margin-top:24px">{problem_items}</ul>
      </div>
      <div class="card reveal" style="padding:30px">
        <div class="card-ico">{icon(s['icon'])}</div>
        <h3>What we do</h3>
        {checks(s['does'])}
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Deliverables</span>
      <h2>What you actually receive.</h2>
      <p>Artefacts your team can operate after we leave, not a slide deck and a wave goodbye.</p>
    </div>
    <div class="table-wrap reveal">
      <table>
        <thead><tr><th style="width:34%">Deliverable</th><th>What it contains</th></tr></thead>
        <tbody>{deliverables}</tbody>
      </table>
    </div>
  </div>
</section>

{fw}

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Ways to engage</span>
      <h2>Sized to the problem in front of you.</h2>
    </div>
    <div class="grid grid-3">{engagements}</div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Related</span><h2>Often paired with</h2></div>
    <div class="grid grid-3">{related}</div>
  </div>
</section>

{cta_band(head="Talk it through with someone senior",
          body="Thirty minutes on your situation specifically, what is driving the timeline, "
               "what you have already tried, and what we would do first.",
          secondary=("All services", "/services.html"))}
"""
        clean_title = s["title"].replace("&amp;", "&")
        page("services/%s.html" % s["slug"],
             "%s | NPS" % clean_title,
             html.escape(s["summary"].replace("&amp;", "&").replace(", ", "-"))[:300],
             body, active="services")


def build_industries():
    cards = "".join(
        f"""<div class="card card--hover card--edge reveal">
          <div class="card-ico">{icon(ic)}</div>
          <h3>{name}</h3>
          <p>{desc}</p>
          <div class="card-foot">
            <div class="chips">{"".join('<span class="chip">%s</span>' % t for t in tags)}</div>
          </div>
        </div>""" for name, ic, desc, tags in INDUSTRIES
    )
    body = f"""
{page_hero([("Home", "/"), ("Industries", None)], "Industries",
           "Regulated, audited, and accountable to somebody.",
           "We work best where security is not optional, where a regulator, a prime contractor, "
           "an insurer or your largest customer is going to check. Context matters: the same control "
           "means different things in a hospital and a factory.")}

<section class="section">
  <div class="wrap">
    <div class="grid grid-2">{cards}</div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">Not on the list?</span>
    <h2>The pattern travels further than the vertical does.</h2>
    <p class="lede">If your organization holds data somebody else cares about, depends on systems
    that cannot go down, or has to prove its controls to a third party, the work looks broadly
    similar. Tell us the specifics and we will tell you honestly whether we are the right firm.</p>
    <div class="btn-row" style="margin-top:28px">
      <a class="btn btn-primary" href="{SITE['booking_url']}">Book a call {icon('arrow')}</a>
    </div>
  </div>
</section>

{cta_band()}
"""
    page("industries.html", "Industries We Serve | NPS",
         "Cybersecurity advisory for healthcare, financial services, SaaS, government and defense, "
         "manufacturing, legal, energy, education, retail and nonprofit organizations.",
         body, active="industries")


def build_case_studies():
    if not SITE.get("show_case_studies"):
        return
    cards = "".join(
        f"""<a class="card card--edge" href="/case-studies/{c['slug']}.html">
          <span class="tag">{c['tag']}</span>
          <h3 style="margin-top:16px">{c['title']}</h3>
          <p>{c['teaser']}</p>
          <div class="card-foot"><span class="link-arrow">Read the case study {icon('arrow')}</span></div>
        </a>""" for c in CASE_STUDIES
    )
    body = f"""
{page_hero([("Home", "/"), ("Case Studies", None)], "Case studies",
           "Engagements, described honestly.",
           "Including the part where the most valuable advice was about what not to do. Client "
           "details are generalised where confidentiality requires it.")}

<section class="section">
  <div class="wrap">
    <div class="grid grid-3">{cards}</div>
  </div>
</section>

{cta_band(head="Your situation is probably not identical",
          body="It rarely is. Describe it and we will tell you what we would actually do, "
               "and roughly what it takes.",
          secondary=("See our services", "/services.html"))}
"""
    page("case-studies.html", "Case Studies | NPS",
         "Real cybersecurity engagements: SOC 2 certification for a SaaS platform, CMMC Level 2 "
         "readiness for a defense manufacturer, and incident response readiness for a health system.",
         body, active="cases")

    for c in CASE_STUDIES:
        facts = "".join(
            f'<div class="readout-row"><span class="label">{k}</span>'
            f'<span class="value">{v}</span></div>' for k, v in c["facts"]
        )
        approach = "".join("<li>%s<span>%s</span></li>" % (icon("check"), a) for a in c["approach"])
        outcome = "".join("<li>%s<span>%s</span></li>" % (icon("check"), o) for o in c["outcome"])
        others = [x for x in CASE_STUDIES if x["slug"] != c["slug"]]
        more = "".join(
            f"""<a class="card card--edge" href="/case-studies/{o['slug']}.html">
              <span class="tag">{o['tag']}</span><h3 style="margin-top:16px">{o['title']}</h3>
              <p>{o['teaser']}</p>
              <div class="card-foot"><span class="link-arrow">Read {icon('arrow')}</span></div>
            </a>""" for o in others
        )
        body = f"""
{page_hero([("Home", "/"), ("Case Studies", "/case-studies.html"), (c['tag'], None)],
           c['tag'], c['title'], c['teaser'], buttons=False)}

<section class="section">
  <div class="wrap">
    <div class="split" style="align-items:start">
      <div class="prose">
        <h2 style="margin-top:0">The challenge</h2>
        <p>{c['challenge']}</p>
        <h2>What we did</h2>
        <ul class="checks" style="margin-top:20px">{approach}</ul>
        <h2>Outcome</h2>
        <ul class="checks" style="margin-top:20px">{outcome}</ul>
        <figure class="quote" style="margin-top:36px">
          <div class="mark">&ldquo;</div>
          <blockquote>{c['quote'][0]}</blockquote>
          <figcaption><b>{c['quote'][1]}</b>Client, {c['tag']}</figcaption>
        </figure>
      </div>
      <aside class="readout reveal">
        <div class="readout-head"><span>Engagement</span><span class="dot"></span></div>
        {facts}
        <div style="margin-top:22px">
          <a class="btn btn-primary btn-block" href="{SITE['booking_url']}">Discuss a similar problem</a>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">More work</span><h2>Other engagements</h2></div>
    <div class="grid grid-2">{more}</div>
  </div>
</section>

{cta_band()}
"""
        page("case-studies/%s.html" % c["slug"],
             "%s | NPS Case Study" % html.escape(c["title"].replace("&amp;", "&"))[:80],
             html.escape(c["teaser"].replace("&amp;", "&"))[:300],
             body, active="cases")


def build_insights():
    cards = "".join(
        f"""<a class="card card--edge" href="/insights/{a['slug']}.html">
          <span class="tag">{a['tag']}</span>
          <h3 style="margin-top:16px">{a['title']}</h3>
          <p>{a['teaser']}</p>
          <div class="card-foot">
            <div class="meta-row">{a['date_display']} <span>&middot;</span> {a['read']}</div>
          </div>
        </a>""" for a in INSIGHTS
    )
    body = f"""
{page_hero([("Home", "/"), ("Insights", None)], "Insights",
           "Opinions we are willing to defend.",
           "Short, specific writing on the security questions we get asked most. No gated PDFs, "
           "no newsletter wall.", buttons=False)}

<section class="section">
  <div class="wrap">
    <div class="grid grid-3">{cards}</div>
  </div>
</section>

{cta_band(head="Want this applied to your organization?",
          body="Reading about it is the cheap part. Book thirty minutes and we will tell you which "
               "of it actually applies to you.",
          secondary=("See our services", "/services.html"))}
"""
    page("insights.html", "Insights | NPS",
         "Practical writing on compliance programs, AI governance, board reporting and security "
         "leadership from the NPS advisory team.",
         body, active="insights")

    for a in INSIGHTS:
        parts = []
        for kind, val in a["body"]:
            if kind == "p":
                parts.append("<p>%s</p>" % val)
            elif kind == "h2":
                parts.append("<h2>%s</h2>" % val)
            elif kind == "ul":
                parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in val))
            elif kind == "quote":
                parts.append("<blockquote>%s</blockquote>" % val)
        others = [x for x in INSIGHTS if x["slug"] != a["slug"]]
        more = "".join(
            f"""<a class="card card--edge" href="/insights/{o['slug']}.html">
              <span class="tag">{o['tag']}</span><h3 style="margin-top:16px">{o['title']}</h3>
              <p>{o['teaser']}</p></a>""" for o in others
        )
        body = f"""
<section class="page-hero">
  <div class="wrap wrap-narrow">
    <div class="breadcrumb"><a href="/">Home</a><span class="sep">/</span>
      <a href="/insights.html">Insights</a><span class="sep">/</span><span>{a['tag']}</span></div>
    <span class="tag">{a['tag']}</span>
    <h1 style="margin-top:18px">{a['title']}</h1>
    <div class="meta-row" style="margin-top:18px">
      <time datetime="{a['date']}">{a['date_display']}</time><span>&middot;</span>{a['read']}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap wrap-narrow">
    <article class="prose">
      <p class="lede">{a['teaser']}</p>
      {''.join(parts)}
    </article>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Keep reading</span><h2>More insights</h2></div>
    <div class="grid grid-2">{more}</div>
  </div>
</section>

{cta_band()}
"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": a["title"],
            "datePublished": a["date"],
            "author": {"@type": "Organization", "name": SITE["legal_name"]},
            "publisher": {"@type": "Organization", "name": SITE["legal_name"]},
            "description": a["teaser"],
        }
        page("insights/%s.html" % a["slug"],
             "%s | NPS Insights" % html.escape(a["title"])[:80],
             html.escape(a["teaser"])[:300], body, active="insights", schema=schema)


def build_guides():
    cards = "".join(
        f"""<a class="card card--edge guide-card" href="/guides/{g['slug']}.html">
          <div class="card-num">{g['code']}</div>
          <h3>{g['title']}</h3>
          <p>{g['teaser']}</p>
          <div class="card-foot">
            <div class="guide-meta">{len(g['phases'])} phases <span>&middot;</span> {g['read']}</div>
            <span class="link-arrow" style="margin-top:14px">Read the roadmap {icon('arrow')}</span>
          </div>
        </a>""" for g in GUIDES
    )
    body = f"""
{page_hero([("Home", "/"), ("Guides", None)], "Guides",
           "How these programs actually run.",
           "Framework roadmaps written from having run them: the real phases, the durations "
           "nobody quotes you, the artifacts you have to produce, and the specific ways these "
           "programs go wrong. No gate, no email required.")}

<section class="section">
  <div class="wrap">
    <div class="grid grid-3">{cards}</div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">Why we publish these</span>
    <h2>Because the hard part is never the control list.</h2>
    <p class="lede">Every framework publishes its requirements. What nobody publishes is how long
    each phase really takes, which decisions cost the most, and what an assessor looks at first.
    That is the part we have learned by doing it, and it is more useful to you in the open than
    behind a form.</p>
  </div>
</section>

{cta_band(head="Working to one of these deadlines?",
          body="Tell us the framework, the date and what you have already done. We will tell you "
               "whether the date is realistic and what we would do first.",
          secondary=("Compliance services", "/services/compliance.html"))}
"""
    page("guides.html", "Compliance Roadmaps: SOC 2, ISO 27001, CMMC | NPS",
         "Practitioner roadmaps for SOC 2, ISO/IEC 27001:2022 and CMMC. Real phases, real "
         "durations, required artifacts, and how these programs fail.",
         body, active="guides")

    for g in GUIDES:
        who = "".join("<li>%s<span>%s</span></li>" % (icon("check"), w) for w in g["who"])

        call = ""
        if g.get("callout"):
            t, d = g["callout"]
            call = ('<div class="callout">%s<div><b>%s</b><p>%s</p></div></div>'
                    % ('<span class="ico">%s</span>' % icon("compass"), t, d))
        if g.get("callout_alert"):
            t, d = g["callout_alert"]
            call = ('<div class="callout callout--alert">%s<div><b>%s</b><p>%s</p></div></div>'
                    % ('<span class="ico">%s</span>' % icon("radar"), t, d))

        phases = "".join(
            f"""<div class="phase">
              <div class="phase-head"><h3>{name}</h3><span class="phase-dur">{dur}</span></div>
              <p>{what}</p>
              <div class="out"><b>You come out with:</b> {out}</div>
            </div>""" for name, dur, what, out in g["phases"]
        )
        sinks = "".join("<li>%s<span>%s</span></li>" % (icon("clock"), x) for x in g["time_sinks"])
        arts = "".join("<tr><td>%s</td><td>%s</td></tr>" % (n, d) for n, d in g["artifacts"])
        fails = "".join(
            '<div class="fail"><h3>%s</h3><p>%s</p></div>' % (h, b) for h, b in g["failures"]
        )
        costs = "".join("<li>%s<span>%s</span></li>" % (icon("chart"), c) for c in g["cost_drivers"])
        others = [x for x in GUIDES if x["slug"] != g["slug"]]
        more = "".join(
            f"""<a class="card card--edge" href="/guides/{o['slug']}.html">
              <div class="card-num">{o['code']}</div><h3>{o['title']}</h3>
              <p>{o['teaser']}</p></a>""" for o in others
        )

        body = f"""
{page_hero([("Home", "/"), ("Guides", "/guides.html"), (g['code'], None)],
           g['eyebrow'], g['title'], g['teaser'])}

<section class="section">
  <div class="wrap">
    <div class="split" style="align-items:start">
      <div class="prose">
        {call}
        <p class="lede">{g['summary']}</p>
      </div>
      <div class="card" style="padding:28px">
        <div class="card-ico">{icon('clipboard')}</div>
        <h3>Read this if</h3>
        {checks(g['who'])}
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The roadmap</span>
      <h2>What the program actually looks like.</h2>
      <p>Durations assume a first attempt with a team that has other work to do. They are the
      numbers we would give you on a call, not the ones in a sales deck.</p>
    </div>
    <div class="wrap-narrow" style="padding:0">
      <div class="roadmap">{phases}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split" style="align-items:start">
      <div>
        <span class="eyebrow">Where the time goes</span>
        <h2>The five things that consume the calendar.</h2>
        <p class="lede" style="margin-bottom:26px">None of these are the parts people budget for,
        and all of them are the parts that slip.</p>
        <ul class="checks">{sinks}</ul>
      </div>
      <div>
        <span class="eyebrow">Cost drivers</span>
        <h2>What moves the number.</h2>
        <p class="lede" style="margin-bottom:26px">Two organizations of the same size can differ
        several-fold on price. This is usually why.</p>
        <ul class="checks">{costs}</ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--panel">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Deliverables</span>
      <h2>What you have to produce.</h2>
      <p>Every one of these will be asked for. Missing any of them is a finding.</p>
    </div>
    <div class="table-wrap reveal">
      <table>
        <thead><tr><th style="width:34%">Artifact</th><th>What it has to contain</th></tr></thead>
        <tbody>{arts}</tbody>
      </table>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">How it goes wrong</span>
      <h2>Five failures we see repeatedly.</h2>
      <p>Each of these turns a manageable program into an expensive one. All five are avoidable
      at the start and very hard to fix in the middle.</p>
    </div>
    <div class="fails">{fails}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">Questions</span>
      <h2>What people ask us about {g['code']}.</h2>
    </div>
    {faq_block(g['faqs'])}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Other roadmaps</span><h2>Keep reading</h2></div>
    <div class="grid grid-2">{more}</div>
  </div>
</section>

{cta_band(head="Want this run for you?",
          body="We run these programs end to end: scoping, control design, evidence, auditor "
               "management, and the operating rhythm that keeps year two boring.",
          secondary=("Compliance services", "/services/compliance.html"))}
"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": g["title"],
            "description": g["teaser"],
            "author": {"@type": "Organization", "name": "NPS"},
            "publisher": {"@type": "Organization", "name": "NPS"},
        }
        page("guides/%s.html" % g["slug"],
             "%s | NPS" % html.escape(g["title"]),
             html.escape(g["teaser"])[:300], body, active="guides", schema=schema)


def build_about():
    values = [
        ("Clarity over jargon", "If a smart non-specialist cannot follow the argument, we have not "
                                "finished writing it. Complexity is not the same as depth."),
        ("Say the uncomfortable thing", "You are paying for judgment, and judgment that only ever "
                                        "agrees with you is worthless. We will tell you when the "
                                        "answer is that you have a people problem, not a tool problem."),
        ("Own the outcome", "We do not hand over a findings list and call it delivery. We stay "
                            "until the control works and someone on your team owns it."),
        ("Proportion, always", "Security that costs more than the risk it removes is a bad trade. "
                               "Part of our job is telling you what not to do."),
    ]
    value_cards = "".join(
        f'<div class="card reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in values
    )
    creds = ["CISSP", "CISM", "CCSP", "CISA", "ISO 27001 Lead Auditor", "ISO 27001 Lead Implementer",
             "CMMC RP", "AWS Security", "Azure Security Engineer", "CIPP/E", "GIAC", "CRISC"]
    cred_chips = "".join('<span class="chip">%s%s</span>' % (icon("check", "tick"), c) for c in creds)
    body = f"""
{page_hero([("Home", "/"), ("About", None)], "About NPS",
           "A security practice, not a staffing desk.",
           "NPS is a cybersecurity advisory firm. We work with "
           "organizations that are accountable to somebody: a regulator, a prime contractor, an "
           "insurer, or the enterprise customer whose security review is holding up the contract.")}

<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="prose">
        <h2 style="margin-top:0">Why we exist</h2>
        <p>Security advice has a delivery problem. The large firms sell partner credibility and
        deliver junior hours. The tooling vendors sell a platform and leave the program to you.
        Both models produce documents. Neither reliably produces a security posture you could
        defend in a room with someone who knows what they are looking at.</p>
        <p>We built NPS around the opposite arrangement. Senior practitioners doing the work
        directly, staying long enough to see the control actually operate, and writing in language
        the person signing the cheque can evaluate.</p>
        <h2>What we are not</h2>
        <p>We are not a managed security service, and we will not pretend that monitoring is a
        strategy. We are not a reseller dressed as an advisor, which is why we can tell you that
        the tool you are about to buy will not fix the problem you have. And we are not a body
        shop: every engagement is scoped to an outcome, not to a headcount.</p>
      </div>
      <div class="readout reveal">
        <div class="readout-head"><span>At a glance</span><span class="dot"></span></div>
        <div class="readout-row"><span class="label">Practice</span><span class="value">Security advisory</span></div>
        <div class="readout-row"><span class="label">Based</span><span class="value">New Jersey, USA</span></div>
        <div class="readout-row"><span class="label">Practice areas</span><span class="value">8</span></div>
        <div class="readout-row"><span class="label">Delivery</span><span class="value">Senior-led, always</span></div>
        <div style="margin-top:22px">
          <a class="btn btn-primary btn-block" href="{SITE['booking_url']}">Book a call</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">How we operate</span>
      <h2>Four commitments we will be held to.</h2>
    </div>
    <div class="grid grid-4">{value_cards}</div>
  </div>
</section>

<!-- PLACEHOLDER: list only credentials your team actually holds -->
<section class="section section--panel">
  <div class="wrap">
    <div class="split">
      <div>
        <span class="eyebrow">Credentials</span>
        <h2>Certification is table stakes. Experience is the differentiator.</h2>
        <p class="lede">Our practitioners hold the credentials you would expect and, more
        usefully, have run the programs those credentials describe. Ask us about the engagement,
        not the acronym.</p>
      </div>
      <div class="chips reveal">{cred_chips}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap wrap-narrow">
    <div class="section-head center"><span class="eyebrow">Questions</span>
      <h2>Things people ask before engaging.</h2></div>
    {faq_block(FAQS)}
  </div>
</section>

{cta_band()}
"""
    page("about.html", "About NPS | Security Advisory Practice",
         "NPS is a senior-led cybersecurity advisory firm based in New Jersey, serving regulated "
         "and audited organizations across the United States.",
         body, active="about")


def build_contact():
    svc_options = "".join('<option>%s</option>' % s["title"].replace("&amp;", "&") for s in SERVICES)
    body = f"""
{page_hero([("Home", "/"), ("Contact", None)], "Contact",
           "Tell us what prompted the call.",
           "A customer requirement, an audit date, an incident, a board question, or a quiet feeling "
           "that nobody actually owns this. All of those are good reasons to get in touch.",
           buttons=False)}

<section class="section">
  <div class="wrap">
    <div class="split" style="align-items:start">
      <div>
        <h2 style="margin-top:0">Send us a note</h2>
        <p class="lede" style="margin-bottom:30px">We reply to every message from a real
        organization within one business day.</p>
        <form class="form" data-contact method="POST" action="{SITE['form_action']}">
          <input type="hidden" name="_subject" value="Website enquiry via nilaproservices.com">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_captcha" value="false">
          <input type="hidden" name="_next" value="{SITE['domain']}/thank-you.html">
          <input type="text" name="_honey" tabindex="-1" autocomplete="off"
                 aria-hidden="true" class="visually-hidden">
          <div class="field-row">
            <div class="field">
              <label for="name">Name <span class="req">*</span></label>
              <input id="name" name="name" type="text" required autocomplete="name" placeholder="Your name">
            </div>
            <div class="field">
              <label for="company">Company <span class="req">*</span></label>
              <input id="company" name="company" type="text" required autocomplete="organization" placeholder="Organization">
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="email">Work email <span class="req">*</span></label>
              <input id="email" name="email" type="email" required autocomplete="email" placeholder="you@company.com">
            </div>
            <div class="field">
              <label for="phone">Phone</label>
              <input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="Optional">
            </div>
          </div>
          <div class="field">
            <label for="topic">What is this about?</label>
            <select id="topic" name="topic">
              <option>Not sure yet, let's talk</option>
              {svc_options}
              <option>Something else</option>
            </select>
          </div>
          <div class="field">
            <label for="timeline">Is there a deadline driving this?</label>
            <select id="timeline" name="timeline">
              <option>No fixed deadline</option>
              <option>Within 30 days</option>
              <option>This quarter</option>
              <option>This year</option>
              <option>Active incident, urgent</option>
            </select>
          </div>
          <div class="field">
            <label for="message">Tell us more <span class="req">*</span></label>
            <textarea id="message" name="message" required
              placeholder="What triggered this, what you have already tried, and what a good outcome looks like."></textarea>
          </div>
          <button class="btn btn-primary" type="submit">Send message {icon('arrow')}</button>
          <p class="form-note form-status">We will never share your information. No mailing list,
          no drip sequence.</p>
        </form>
      </div>

      <aside>
        <div class="card" style="padding:30px">
          <h3 style="margin-bottom:22px">Reach us directly</h3>
          <div class="info-list">
            <div class="info-item"><span class="ico">{icon('calendar')}</span>
              <div><b>Book directly</b><a href="{SITE['booking_url']}" rel="noopener">30 minutes with Raj Kumar</a></div></div>
            <div class="info-item"><span class="ico">{icon('mail')}</span>
              <div><b>Email</b><a href="mailto:{SITE['email']}">{SITE['email']}</a></div></div>
            <div class="info-item"><span class="ico">{icon('pin')}</span>
              <div><b>Office</b><span>{SITE['address_1']}<br>{SITE['address_2']}</span></div></div>
            <div class="info-item"><span class="ico">{icon('clock')}</span>
              <div><b>Hours</b><span>Monday to Friday, 9:00 AM to 6:00 PM ET</span></div></div>
          </div>
        </div>

        <div class="card card--alert" style="padding:30px;margin-top:22px">
          <div class="card-ico">{icon('radar')}</div>
          <h3>Active incident?</h3>
          <p>If you are dealing with a live security incident, email us with
          <strong>INCIDENT</strong> in the subject line. Those go straight to a senior
          practitioner rather than into the normal queue.</p>
          <div class="card-foot">
            <a class="btn btn-alert btn-block"
               href="mailto:{SITE['email']}?subject=INCIDENT%20-%20urgent%20security%20support">
              Email the incident line</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>
"""
    page("contact.html", "Contact NPS | Cybersecurity Advisory",
         "Get in touch with NPS for cybersecurity advisory, vCISO services, compliance programs and "
         "incident readiness. Based in South Amboy, New Jersey.",
         body, active="contact")


def build_legal():
    thanks_cards = "".join(
        f'''<a class="card card--edge" href="/insights/{a['slug']}.html">
          <span class="tag">{a['tag']}</span>
          <h3 style="margin-top:14px">{a['title']}</h3>
        </a>''' for a in INSIGHTS
    )
    privacy = f"""
{page_hero([("Home", "/"), ("Privacy", None)], "Legal", "Privacy Policy",
           "How NPS handles the information you share with us.".format(),
           buttons=False)}
<section class="section"><div class="wrap"><article class="prose">
  <p><em>Last updated: August 5, 2026. This is a starting template, have counsel review it
  before launch.</em></p>
  <h2>What we collect</h2>
  <p>When you submit our contact form we collect the name, organization, email address, phone number
  and message you provide. We collect standard web server logs, including IP address and user agent,
  for security and reliability purposes.</p>
  <h2>How we use it</h2>
  <p>We use your contact details solely to respond to your enquiry and to carry out any engagement
  that follows. We do not sell personal information, and we do not add enquiries to a marketing list
  without explicit opt-in.</p>
  <h2>Analytics and cookies</h2>
  <p>This site uses no advertising cookies and no cross-site trackers. If analytics are enabled, they
  are privacy-preserving and aggregate only.</p>
  <h2>Retention</h2>
  <p>Enquiry records are retained for as long as needed to serve the relationship and to meet legal
  and contractual obligations, and are deleted on request where no such obligation applies.</p>
  <h2>Your rights</h2>
  <p>Depending on your jurisdiction you may have the right to access, correct, delete or restrict
  processing of your personal information. Email <a href="mailto:{SITE['email']}">{SITE['email']}</a>
  and we will respond within the applicable statutory period.</p>
  <h2>Client confidentiality</h2>
  <p>Information obtained during a client engagement is governed by the engagement agreement and
  applicable non-disclosure terms, which take precedence over this policy.</p>
  <h2>Contact</h2>
  <p>{SITE['legal_entity']} (NPS), {SITE['address_1']}, {SITE['address_2']}.
  <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
</article></div></section>
"""
    page("privacy.html", "Privacy Policy | NPS", "How NPS handles personal information.",
         privacy)

    terms = f"""
{page_hero([("Home", "/"), ("Terms", None)], "Legal", "Terms of Use",
           "The terms that apply to your use of this website.", buttons=False)}
<section class="section"><div class="wrap"><article class="prose">
  <p><em>Last updated: August 5, 2026. This is a starting template, have counsel review it
  before launch.</em></p>
  <h2>Website content</h2>
  <p>Content on this site is provided for general information. It does not constitute security,
  legal, regulatory or financial advice, and no client relationship is created by reading it or by
  contacting us through this site.</p>
  <h2>Intellectual property</h2>
  <p>All content, design and materials on this site are the property of {SITE['legal_entity']} unless
  otherwise stated, and may not be reproduced commercially without written permission.</p>
  <h2>Third-party links</h2>
  <p>We link to external resources for convenience. We do not control and are not responsible for
  their content or practices.</p>
  <h2>Limitation of liability</h2>
  <p>To the fullest extent permitted by law, {SITE['legal_entity']} is not liable for any loss arising
  from reliance on information published on this site. Engagement-specific obligations are governed
  exclusively by the applicable signed agreement.</p>
  <h2>Governing law</h2>
  <p>These terms are governed by the laws of the State of New Jersey, United States.</p>
</article></div></section>
"""
    page("terms.html", "Terms of Use | NPS", "Terms governing use of the NPS website.",
         terms)

    thanks = f"""
<section class="page-hero" style="padding-block:110px">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">Message received</span>
    <h1>Thank you. We have it.</h1>
    <p class="lede">Someone senior reads every enquiry that comes through this form, and you
    will hear back within one business day. If what you sent is time sensitive, you can also
    book a call directly and pick a slot that works.</p>
    <div class="btn-row" style="margin-top:32px;justify-content:center">
      <a class="btn btn-primary" data-cta="thank-you" href="{SITE['booking_url']}">Book a call {icon('arrow')}</a>
      <a class="btn btn-ghost" href="/">Back to home</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">While you wait</span>
      <h2>Some of what we think.</h2>
    </div>
    <div class="grid grid-3">{thanks_cards}</div>
  </div>
</section>
"""
    page("thank-you.html", "Thank you | NPS",
         "Your message has been received. NPS replies to every enquiry within one business day.",
         thanks)

    notfound = f"""
<section class="page-hero" style="padding-block:120px">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">Error 404</span>
    <h1>That page does not exist.</h1>
    <p class="lede">Which, on a security firm's website, is at least a correctly enforced default
    deny. Try one of these instead.</p>
    <div class="btn-row" style="margin-top:30px;justify-content:center">
      <a class="btn btn-primary" href="/">Back to home {icon('arrow')}</a>
      <a class="btn btn-ghost" href="/services.html">Services</a>
      <a class="btn btn-ghost" href="/contact.html">Contact</a>
    </div>
  </div>
</section>
"""
    page("404.html", "Page not found | NPS", "The page you requested could not be found.", notfound)


def build_seo_assets():
    urls = ["/", "/services.html", "/industries.html", "/guides.html", "/insights.html",
            "/about.html", "/contact.html", "/privacy.html", "/terms.html"]
    if SITE.get("show_case_studies"):
        urls.insert(3, "/case-studies.html")
    urls += ["/services/%s.html" % s["slug"] for s in SERVICES]
    if SITE.get("show_case_studies"):
        urls += ["/case-studies/%s.html" % c["slug"] for c in CASE_STUDIES]
    urls += ["/guides/%s.html" % g["slug"] for g in GUIDES]
    urls += ["/insights/%s.html" % a["slug"] for a in INSIGHTS]

    entries = "\n".join(
        "  <url><loc>%s%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>"
        % (SITE["domain"], u, "1.0" if u == "/" else "0.7")
        for u in urls
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + entries + "\n</urlset>\n")

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        if SITE.get("preview_mode"):
            f.write("# PREVIEW MODE, site is not ready to be indexed.\n"
                    "# Set SITE[\"preview_mode\"] = False in build.py before launch.\n"
                    "User-agent: *\nDisallow: /\n")
        else:
            f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["domain"])

    # Icons and the OG card are real image assets derived from the NPS logo
    # (see assets/img/). They are checked in, not generated here.

    # GitHub Pages needs this so /assets and folder paths are served as-is
    open(os.path.join(ROOT, ".nojekyll"), "w").close()


def main():
    for d in ("services", "case-studies", "insights", "guides"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    # Remove pages that a feature flag has turned off, so a stale file from a
    # previous build cannot stay live and reachable by direct URL.
    if not SITE.get("show_case_studies"):
        stale = os.path.join(ROOT, "case-studies.html")
        if os.path.exists(stale):
            os.remove(stale)
    build_home()
    build_services_index()
    build_service_pages()
    build_industries()
    build_guides()
    build_case_studies()
    build_insights()
    build_about()
    build_contact()
    build_legal()
    build_seo_assets()
    count = sum(len(files) for _, _, files in os.walk(ROOT)
                for _ in [0]) if False else None
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "assets", ".github")]
        for fn in filenames:
            if fn.endswith(".html"):
                pages.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))
    print("Built %d HTML pages:" % len(pages))
    for p in sorted(pages):
        print("  " + p)


if __name__ == "__main__":
    main()
