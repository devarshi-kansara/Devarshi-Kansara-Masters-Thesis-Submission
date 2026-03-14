"""
Knowledge base derived from the thesis findings.
Contains industry-specific risk patterns, decision-making frameworks,
and cross-cultural insights.
"""

# ── Industry Risk Profiles ────────────────────────────────────────────────────
INDUSTRY_RISKS = {
    "construction": {
        "primary_external": [
            "Weather and environmental conditions (soil, water table, temperature swings)",
            "Regulatory delays / permit approvals",
            "Site safety and liability (VOB / contractual law)",
            "Supplier lead-times for specialist materials",
        ],
        "primary_internal": [
            "Design changes and scope creep",
            "Sub-contractor performance and coordination",
            "Measurement / surveying errors (hidden until excavation)",
            "BIM model accuracy vs. on-site reality",
        ],
        "blind_spots_for_outsiders": [
            "Legal disputes are far more common than in other industries — contract law expertise is non-negotiable",
            "Weather-driven delays compound exponentially; build double buffers",
            "Somatic truth: dashboards lie — always physically inspect the site",
            "VOB clauses can shift personal liability; document everything",
        ],
        "first_20_percent_actions": [
            "Conduct a mandatory geotechnical survey before any commitment",
            "Review all permits and regulatory requirements upfront",
            "Pair a junior engineer (micro-check on technical details) with a senior PM (legal / strategic shield)",
            "Benchmark against 3+ similar completed projects for realistic baselines",
            "Establish a '20% Reality Check' workshop with the full team",
        ],
        "typical_tools": ["FMEA", "BIM dashboards", "Risk register", "HAZOP", "Lessons-learned database"],
    },
    "manufacturing": {
        "primary_external": [
            "Supply chain disruptions and inventory degradation",
            "Regulatory compliance (EU MDR, FDA, GDPR, DORA)",
            "Market demand volatility",
            "Raw material price fluctuations",
        ],
        "primary_internal": [
            "Compounding effect of minor technical errors (1 mm deviation → production failure)",
            "Machine health and calibration drift",
            "Process documentation gaps",
            "Change management for new equipment introduction",
        ],
        "blind_spots_for_outsiders": [
            "Small tolerance errors cascade into full production stoppages — precision is everything",
            "Inventory degradation is a silent killer; monitor shelf-life continuously",
            "FMEA is a legal shield as much as a technical tool",
            "Cross-shift communication gaps are a leading root cause of defects",
        ],
        "first_20_percent_actions": [
            "Run a detailed FMEA on the critical production path before kick-off",
            "Map the entire supply chain and identify single-source dependencies",
            "Deploy acoustic / IoT sensors for real-time machine-health monitoring (Truth-Link)",
            "Align junior staff on micro-checks (calibration, tolerances) and seniors on strategic/regulatory oversight",
            "Review historical failure logs from the last 3–5 comparable production runs",
        ],
        "typical_tools": ["FMEA", "HAZOP", "Statistical Process Control (SPC)", "Digital Twin / IoT dashboards", "Risk register"],
    },
    "it": {
        "primary_external": [
            "Shifting stakeholder requirements and scope creep",
            "Regulatory and data-privacy compliance (GDPR, DORA)",
            "Third-party API / vendor dependency",
            "Cyber-security threats",
        ],
        "primary_internal": [
            "Underestimated technical debt",
            "Team skill gaps and knowledge silos",
            "Integration complexity between systems",
            "Timeline pressure causing shortcuts",
        ],
        "blind_spots_for_outsiders": [
            "Agile velocity metrics can mask hidden complexity — require demo-able deliverables early",
            "Cloud cost overruns are rarely scoped in initial budgets",
            "Security vulnerabilities surface late — include security reviews from sprint 1",
            "Invisible dependencies: a single library deprecation can block an entire release",
        ],
        "first_20_percent_actions": [
            "Define a clear, agreed-upon Definition of Done before any development starts",
            "Run a technology spike / proof-of-concept for the highest-uncertainty components",
            "Identify all third-party dependencies and assess their stability / SLA",
            "Schedule a security-threat modelling session in the first sprint",
            "Create a risk-adjusted roadmap with explicit buffer sprints",
        ],
        "typical_tools": ["Risk register", "Probability-Impact matrix", "JIRA / ADO risk boards", "Threat modelling tools", "SLA tracking dashboards"],
    },
}

# ── Decision-Making Frameworks from the thesis ───────────────────────────────
DECISION_FRAMEWORKS = {
    "safety_premium": {
        "description": (
            "93% of experienced project managers deliberately pay a 'Safety Premium': "
            "they invest in better materials, higher-spec equipment, or larger buffers upfront "
            "rather than risk costly stoppages later."
        ),
        "when_to_apply": "When facing uncertainty about material quality, subcontractor reliability, or site conditions.",
        "example": "Specify a higher-grade concrete than the minimum requirement to avoid rework if ground conditions are worse than expected.",
    },
    "somatic_verification": {
        "description": (
            "Veterans distrust pure digital reporting. 'Somatic Truth' means physically visiting "
            "the site, handling the material, or listening to the machine — sensory evidence that "
            "dashboards cannot replicate."
        ),
        "when_to_apply": "Whenever a digital status report is the sole source of truth for a critical path item.",
        "example": "Walk the excavation yourself before approving the foundation pour, regardless of what the BIM model shows.",
    },
    "bureaucratic_shield": {
        "description": (
            "Formal tools (FMEA, HAZOP, risk registers) serve a dual purpose: technical "
            "analysis AND personal liability deflection. Documenting that due diligence was "
            "performed protects the PM if something goes wrong."
        ),
        "when_to_apply": "High-stakes, high-liability decisions; regulatory environments; projects with many stakeholders.",
        "example": "Complete a documented FMEA even if intuition already identified the key risk, so the analysis is on record.",
    },
    "two_way_team_model": {
        "description": (
            "Replace top-down hierarchy with a 'Two-Way Team Model': "
            "Junior PMs perform detailed 'Micro-Checks' (technical accuracy, site measurements), "
            "while Senior PMs maintain the 'Strategic Shield' (legal, budget, stakeholder management). "
            "Neither can cover the full risk spectrum alone."
        ),
        "when_to_apply": "Every project — especially in the first 20% where perspective pairing has the highest leverage.",
        "example": "Junior reviews soil test reports and flags a 2-point bearing-capacity shortfall; senior escalates to client and triggers a scope-change procedure.",
    },
    "reverse_training": {
        "description": (
            "German 'Process Guardians' benefit from crisis-adaptability training (Jugaad-style improvisation). "
            "Indian 'Resource Navigators' benefit from digital-standardisation training. "
            "Each archetype has blind spots the other can teach."
        ),
        "when_to_apply": "Cross-cultural or cross-regional teams; organisations expanding into new geographies.",
        "example": "A German PM running a project in India should shadow a local PM for one site visit before taking control.",
    },
    "truth_link_technology": {
        "description": (
            "Move from manual reports (which 93.3% of managers distrust) to 'Truth-Link' "
            "socio-technical systems: IoT sensors, acoustic monitors, and digital twins that "
            "provide continuous, tamper-resistant data streams."
        ),
        "when_to_apply": "Projects where the cost of rework or stoppage exceeds the cost of sensor infrastructure.",
        "example": "Deploy foundation-curing sensors on a critical concrete pour so the PM receives real-time strength data instead of relying on a contractor's self-report.",
    },
}

# ── Experience-Level Guidance ─────────────────────────────────────────────────
EXPERIENCE_GUIDANCE = {
    "junior": {
        "strengths": [
            "Technical micro-accuracy — spot measurement errors and site discrepancies that seniors overlook",
            "Fresh perspective — identify risks that are 'normalised' by veterans",
            "Digital-tool proficiency",
        ],
        "development_areas": [
            "External risk identification (regulatory, political, market)",
            "Legal and contractual risk literacy",
            "Network-based intelligence (talking to the right people early)",
        ],
        "recommended_actions": [
            "Focus your energy on the 'Micro-Check' role in the Two-Way Team Model",
            "Shadow a senior PM specifically during client/stakeholder meetings in the first 20%",
            "Build a personal lessons-learned log from day one",
            "Ask: 'What is the one thing that could physically stop this project?' before every milestone",
        ],
    },
    "mid": {
        "strengths": [
            "Blend of technical knowledge and emerging strategic awareness",
            "Can bridge junior and senior perspectives",
        ],
        "development_areas": [
            "Avoid over-reliance on the tools that worked last time (context changes)",
            "Develop the habit of probing external risk sources (regulatory bodies, suppliers, clients) early",
        ],
        "recommended_actions": [
            "Introduce structured reverse audits — ask a junior to challenge your risk list",
            "Practice decision-making under incomplete information: document why you decided, not just what",
            "Seek cross-industry exposure to break industry-specific blind spots",
        ],
    },
    "senior": {
        "strengths": [
            "Pattern recognition from experience (RPD — Recognition-Primed Decision making)",
            "Strategic and legal risk literacy",
            "Stakeholder management and political navigation",
        ],
        "development_areas": [
            "Internal technical blind spots (normalisation of minor deviations)",
            "Over-reliance on past patterns that may not apply to novel contexts",
            "Digital-tool aversion leading to information asymmetry",
        ],
        "recommended_actions": [
            "Mandate junior Micro-Check reviews on your risk register before finalising it",
            "Re-engage with on-site/operational technical details periodically — avoid the 'CYA trap'",
            "Embrace Truth-Link technologies to replace intuition with data where possible",
        ],
    },
}

# ── The 20% Reality Check Framework ──────────────────────────────────────────
REALITY_CHECK_FRAMEWORK = {
    "description": (
        "A mandatory milestone at the end of the first 20% of the project timeline. "
        "This is not a progress meeting — it is a structured risk-validation workshop."
    ),
    "participants": [
        "Project Manager (facilitator)",
        "1–2 Junior team members (Technical Micro-Check validators)",
        "Senior stakeholder or sponsor (Strategic Shield review)",
        "Key sub-contractor or supplier representative (external reality check)",
    ],
    "agenda_items": [
        "Ground Truth Validation: Do measurements, soil/material test results, and site conditions match the original assumptions?",
        "Legal & Permit Review: Are all required approvals in place or firmly scheduled?",
        "Budget Reality Check: Has a 'Safety Premium' buffer been formally approved?",
        "Risk Register Walk-Through: Have all three primary risk categories been addressed (external, internal, cross-cultural)?",
        "Two-Way Team Model Assignment: Is every critical risk owned by a named junior+senior pair?",
        "Truth-Link Readiness: Are monitoring/sensor systems in place for the highest-uncertainty elements?",
    ],
    "output": "A signed-off Risk Baseline Document that serves as the reference for all subsequent decisions.",
}

# ── Cross-Cultural Risk Archetypes ────────────────────────────────────────────
CULTURAL_ARCHETYPES = {
    "process_guardian": {
        "regions": ["Germany", "Western Europe"],
        "characteristics": [
            "91% rely on formal digital tools (FMEA, BIM) as primary evidence",
            "Strong compliance and documentation culture",
            "Digital tools are a 'legal shield' as well as a technical aid",
            "Risk of decision paralysis when tools fail or situations are novel",
        ],
        "blind_spots": [
            "Environmental volatility and improvised problem-solving (Jugaad)",
            "Relationship-based risk intelligence (informal networks)",
        ],
        "recommended_development": "Crisis Simulation training — deliberately remove digital tools and require decisions based on sensory observation and team discussion.",
    },
    "resource_navigator": {
        "regions": ["India", "Emerging Markets"],
        "characteristics": [
            "92% use digital tools as advisory aids, not definitive authorities",
            "High environmental adaptability — improvisation under resource constraints",
            "Relationship networks are primary risk-intelligence channels",
            "Risk of auditability and scalability gaps",
        ],
        "blind_spots": [
            "Formal documentation and auditability",
            "Digital standardisation and data-driven accountability",
        ],
        "recommended_development": "Digital Accountability training — practice documenting every risk decision in a structured register, even for intuition-driven calls.",
    },
}

# ── Risk Scoring Reference (derived from thesis findings) ────────────────────
RISK_SCORE_WEIGHTS = {
    "probability_of_occurrence": {"low": 1, "medium": 2, "high": 3},
    "impact_on_project": {"low": 1, "medium": 2, "high": 3, "critical": 4},
    "detectability": {"early": 1, "late": 2, "post_occurrence": 3},
}

RISK_LEVELS = [
    (1, 4, "Low", "Monitor only; no immediate action required."),
    (5, 9, "Medium", "Assign owner; add mitigation task to schedule."),
    (10, 18, "High", "Immediate mitigation plan required; escalate to sponsor."),
    (19, 36, "Critical", "Stop-and-fix: do not proceed until risk is resolved or fully accepted by sponsor."),
]


def get_risk_level(probability: str, impact: str, detectability: str) -> dict:
    """Return the composite risk level and recommended action based on input ratings."""
    p = RISK_SCORE_WEIGHTS["probability_of_occurrence"].get(probability, 2)
    i = RISK_SCORE_WEIGHTS["impact_on_project"].get(impact, 2)
    d = RISK_SCORE_WEIGHTS["detectability"].get(detectability, 2)
    score = p * i * d
    for low, high, label, action in RISK_LEVELS:
        if low <= score <= high:
            return {"score": score, "level": label, "action": action}
    return {"score": score, "level": "Critical", "action": RISK_LEVELS[-1][3]}
