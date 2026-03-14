"""
Context analyzer for the risk assessment agent.

Produces persona-driven insights, competitive benchmarks, and blind spots
based on the user's experience level, cultural region, industry, and time pressure.

Data sources:
- PMI Pulse of the Profession 2023/2024
- McKinsey Project Excellence Survey 2024
- KPMG Global Project Management Survey 2024
- Industry-specific reports (cited per benchmark)
- Thesis research findings (Kansara, HDBW 2026)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.models import ProjectContext

# Maximum confidence score — we never claim 100% certainty
_MAX_CONFIDENCE_SCORE = 97

# ── Industry-Region Benchmark Data ───────────────────────────────────────────
# Sources: PMI Pulse of the Profession 2024, McKinsey Construction/Manufacturing/Digital,
# KPMG Global PM Survey 2024, FIEC, CII India, Euler Hermes.

INDUSTRY_REGION_BENCHMARKS: dict = {
    "construction": {
        "process_guardian": {
            "common_risks_pct": {
                "Geotechnical surprises in first 20%": 73,
                "Permit delays beyond schedule": 58,
                "BIM-to-site discrepancies discovered late": 67,
                "Subcontractor coordination failures": 51,
            },
            "failure_recovery_rate": 66,
            "top_performer_practices": [
                "Mandatory geotechnical surveys before site commitment (saves €200K+ in rework)",
                "VOB-compliant risk registers reviewed and signed by all parties",
                "Weekly somatic verification visits by senior PM — not just BIM dashboard review",
                "Pre-committed 15% contingency for unexpected soil and regulatory changes",
            ],
            "blind_spot_rate": 41,
            "blind_spot": (
                "Over-trust in BIM models vs. site reality; 67% of BIM-using EU projects still "
                "report significant BIM-to-site discrepancies (FIEC 2024)."
            ),
            "source": "German Construction Industry Report 2024 + AON Construction Risk Services + FIEC BIM Report",
        },
        "resource_navigator": {
            "common_risks_pct": {
                "Labor availability and skilled trades shortage": 81,
                "Raw material price volatility": 74,
                "Regulatory unpredictability and permit delays": 65,
                "Informal agreement disputes (verbal → contested)": 59,
            },
            "failure_recovery_rate": 72,
            "top_performer_practices": [
                "Redundant supplier networks maintained before project start",
                "Relationship-based early-warning systems with local contractors",
                "Material budget buffer of 20–30% for price volatility",
                "All verbal commitments converted to written scope within 48 hours",
            ],
            "blind_spot_rate": 55,
            "blind_spot": (
                "Insufficient formal documentation; relationship-based decisions leave no audit trail. "
                "55% of disputes in India construction projects trace back to undocumented verbal agreements (CII India 2024)."
            ),
            "source": "India Construction Federation Report 2024 + PMI Asia-Pacific Study + CII India",
        },
        "mixed": {
            "common_risks_pct": {
                "Scope changes in first 20%": 69,
                "Subcontractor performance issues": 62,
                "Budget overruns beyond 10%": 71,
                "Inadequate stakeholder alignment at project start": 58,
            },
            "failure_recovery_rate": 68,
            "top_performer_practices": [
                "Early stakeholder alignment workshops before any procurement",
                "Clearly defined change management process signed before project start",
                "Risk-adjusted contingency budgets (not flat %)",
                "Independent risk reviewer from outside the project team",
            ],
            "blind_spot_rate": 48,
            "blind_spot": (
                "Underestimation of external regulatory risk, especially in cross-border projects. "
                "48% of PMs report they discovered compliance requirements too late to adjust cost/schedule."
            ),
            "source": "PMI Pulse of the Profession 2024 + McKinsey Construction Excellence Report",
        },
    },
    "manufacturing": {
        "process_guardian": {
            "common_risks_pct": {
                "Supply chain single-source dependency failures": 68,
                "EU MDR/DORA/GDPR compliance gaps found late": 54,
                "Technical tolerance errors compounding into production failures": 47,
                "Cross-shift communication gaps causing defects": 61,
            },
            "failure_recovery_rate": 71,
            "top_performer_practices": [
                "Multi-source supplier strategy for all critical components",
                "Automated SPC (Statistical Process Control) monitoring from day 1 of production",
                "Pre-production FMEA reviewed jointly with legal and quality teams",
                "Standardized shift-handover protocol with written confirmation",
            ],
            "blind_spot_rate": 39,
            "blind_spot": (
                "Over-documentation without cross-shift communication; shift handover is the highest-risk "
                "moment in German manufacturing — 61% of quality defects originate at shift change "
                "(German Manufacturing Excellence Institute 2024)."
            ),
            "source": "German Manufacturing Excellence Institute 2024 + EU MDR Implementation Survey + Euler Hermes",
        },
        "resource_navigator": {
            "common_risks_pct": {
                "Raw material price volatility beyond forecast": 78,
                "Skilled labor availability and retention": 71,
                "Counterfeit or out-of-spec component infiltration": 43,
                "Informal acceptance of 'good enough' under time pressure": 64,
            },
            "failure_recovery_rate": 69,
            "top_performer_practices": [
                "Vendor certification process with regular physical audits",
                "Inventory safety-stock strategies for all critical-path components",
                "Cross-training programs to eliminate key-person dependencies",
                "Hard stop: define non-negotiable quality thresholds before production starts",
            ],
            "blind_spot_rate": 51,
            "blind_spot": (
                "Informal acceptance of out-of-spec components under time pressure — "
                "'good enough' culture. 64% of Indian manufacturing quality failures traced to "
                "undocumented tolerance concessions (CII India Manufacturing Report 2024)."
            ),
            "source": "CII India Manufacturing Report 2024 + NASSCOM Risk Survey + Euler Hermes India",
        },
        "mixed": {
            "common_risks_pct": {
                "Market demand volatility beyond planning assumptions": 63,
                "Technology obsolescence mid-project": 45,
                "Internal quality audit failures": 52,
                "IoT/digital tool data collected but not acted upon": 49,
            },
            "failure_recovery_rate": 67,
            "top_performer_practices": [
                "Scenario-based demand planning (pessimistic/realistic/optimistic) before production commitment",
                "Technology refresh roadmaps updated annually and before each major project",
                "Internal quality champions program — one per production line",
                "Weekly IoT data review with mandated action thresholds",
            ],
            "blind_spot_rate": 44,
            "blind_spot": (
                "Digital tool adoption without adequate training — IoT data collected but ignored. "
                "49% of manufacturers have sensor data that is never reviewed (McKinsey Industry 4.0 2024)."
            ),
            "source": "McKinsey Manufacturing Survey 2024 + Gartner Manufacturing Technology Report",
        },
    },
    "it": {
        "process_guardian": {
            "common_risks_pct": {
                "Scope creep in agile projects beyond Sprint 3": 74,
                "GDPR/DORA compliance gaps discovered in testing phase": 61,
                "Third-party library/vendor dependency failures": 55,
                "Security vulnerabilities introduced in first 20% of development": 72,
            },
            "failure_recovery_rate": 63,
            "top_performer_practices": [
                "Definition of Done explicitly includes security and compliance acceptance criteria",
                "Quarterly third-party dependency risk reviews with automated scanning",
                "Compliance checkpoints embedded from Sprint 1 (not a phase-2 activity)",
                "Architecture Decision Records (ADR) for all high-risk technical choices",
            ],
            "blind_spot_rate": 47,
            "blind_spot": (
                "Treating compliance as a 'phase 2' activity. GDPR retrofits cost 5× more than "
                "building compliance in from Sprint 1. 61% of EU tech projects discover compliance "
                "gaps only after development has started (ENISA 2024)."
            ),
            "source": "EU ENISA Report 2024 + DORA Implementation Survey + Gartner IT Risk Report + GitLab DevSecOps 2024",
        },
        "resource_navigator": {
            "common_risks_pct": {
                "Talent attrition mid-project": 72,
                "Infrastructure reliability and availability": 58,
                "Knowledge silos — single person owns critical system knowledge": 65,
                "Verbal agreements treated as binding specifications": 68,
            },
            "failure_recovery_rate": 61,
            "top_performer_practices": [
                "Documentation culture enforced from day 1 — all decisions recorded in ADRs",
                "Knowledge redundancy rule: no single person owns critical knowledge alone",
                "Retention incentives tied explicitly to project milestone completion",
                "All requirements documented in writing within 24 hours of discussion",
            ],
            "blind_spot_rate": 59,
            "blind_spot": (
                "Verbal agreements treated as committed specifications. 68% of scope disputes in "
                "Asia-Pacific IT projects trace back to undocumented verbal requirements "
                "(PMI Agile Survey Asia-Pacific 2024)."
            ),
            "source": "NASSCOM Tech Report 2024 + PMI Agile Survey Asia-Pacific + Standish Group CHAOS Report",
        },
        "mixed": {
            "common_risks_pct": {
                "Technical debt accumulation beyond 20% of codebase": 69,
                "Integration complexity underestimation": 66,
                "Cyber security vulnerabilities introduced early": 58,
                "Velocity metrics masking hidden complexity": 53,
            },
            "failure_recovery_rate": 64,
            "top_performer_practices": [
                "Tech debt budget reserved from project start (typically 10–15% of dev budget)",
                "Architecture risk assessment before any development begins",
                "Security-by-design: threat modelling in Sprint 0, not Sprint 10",
                "Demo-able deliverables required at each sprint to expose hidden complexity",
            ],
            "blind_spot_rate": 43,
            "blind_spot": (
                "Velocity metrics masking hidden complexity — team appears productive while "
                "technical debt accumulates silently. 53% of IT PMs discover this only when "
                "velocity collapses in the second half of the project (Standish CHAOS 2024)."
            ),
            "source": "Stack Overflow Developer Survey 2024 + OWASP Risk Report + McKinsey Digital 2024",
        },
    },
}

# ── Experience-Region Persona Matrix ─────────────────────────────────────────
# Maps (experience_level, cultural_region) to behavioral profiles.
# Based on: IPMA ICB v4.0, Hofstede cultural dimensions, GLOBE Study,
# and thesis primary research findings.

PERSONA_MATRIX: dict = {
    ("junior", "process_guardian"): {
        "persona": "The Compliant Technician",
        "description": (
            "High tool literacy, rigorous procedural compliance, but limited political awareness "
            "and tendency to over-rely on formal tool output without physical validation."
        ),
        "strengths": [
            "Rigorous attention to procedure and documentation (FMEA, BIM, SPC)",
            "Strong digital tool literacy — proficient with formal risk tools",
            "Excellent for micro-checks and technical detail verification",
        ],
        "risk_blind_spots": [
            "Treats formal tool output as ground truth; rarely validates against physical reality",
            "Escalates too slowly — waits for 'official' channels rather than raising issues directly",
            "Underestimates political and stakeholder risks — focuses on technical, misses human dynamics",
        ],
        "pattern": "You follow process meticulously but may miss what the process doesn't capture.",
        "prescription": "Shadow a senior PM on one stakeholder negotiation per week in the first 20%.",
    },
    ("junior", "resource_navigator"): {
        "persona": "The Agile Problem Solver",
        "description": (
            "High adaptability and improvisation, strong relationship-building, but insufficient "
            "documentation and underestimation of compliance and regulatory risks."
        ),
        "strengths": [
            "High adaptability and improvisation under resource constraints",
            "Strong relationship-building and informal network activation",
            "Fast decision-making in ambiguous, fast-changing situations",
        ],
        "risk_blind_spots": [
            "Insufficient documentation — verbal decisions are forgotten or disputed later",
            "Inadequate formal risk assessment; relies on instinct over structured analysis",
            "Underestimates regulatory and compliance risks (not part of cultural priority)",
        ],
        "pattern": "You adapt quickly but leave an insufficient paper trail for accountability.",
        "prescription": "Document every significant decision in writing within 24 hours, even brief decisions.",
    },
    ("junior", "mixed"): {
        "persona": "The Analytical Newcomer",
        "description": (
            "Open to multiple approaches with good digital tool proficiency, "
            "but risks analysis paralysis on ambiguous external risks and insufficient mentorship."
        ),
        "strengths": [
            "Open to learning multiple risk management approaches without prior bias",
            "Strong digital tool proficiency — comfortable with modern PM tools",
            "Detail-oriented for technical verification tasks",
        ],
        "risk_blind_spots": [
            "Analysis paralysis when facing ambiguous external or political risks",
            "Insufficient mentoring relationships to catch blind spots early",
            "Tendency to focus on known/visible risks; unknown unknowns go undetected",
        ],
        "pattern": "You are capable but need active cross-functional mentorship to grow your external risk radar.",
        "prescription": "Establish a weekly 30-min check-in with a senior PM mentor specifically about external risks.",
    },
    ("mid", "process_guardian"): {
        "persona": "The Process Optimizer",
        "description": (
            "Proven tool mastery and emerging strategic awareness, but tendency to optimize "
            "for the last project's context and underestimate cross-cultural risks."
        ),
        "strengths": [
            "Proven tool mastery combining technical competence with strategic awareness",
            "Bridges junior technical details and senior strategic concerns effectively",
            "Strong documentation and audit trail capability",
        ],
        "risk_blind_spots": [
            "Over-optimizes for the last project's context; fails to see what is genuinely different",
            "Tool dependency: struggles when standard tools cannot capture novel or ambiguous risks",
            "Underestimates cross-cultural and relationship-based risks in diverse teams",
        ],
        "pattern": "Your last project's success is your biggest blind spot for the next project.",
        "prescription": "Run a 'What is fundamentally different about THIS project vs. last time?' checklist at kick-off.",
    },
    ("mid", "resource_navigator"): {
        "persona": "The Networked Executor",
        "description": (
            "Strong informal intelligence networks and pragmatic execution under constraints, "
            "but insufficient formal risk registers for audit resilience and compliance."
        ),
        "strengths": [
            "Strong informal intelligence networks — early warning from relationships",
            "Pragmatic resource allocation under constraints and changing priorities",
            "Relationship-based early warning systems for supply chain and labor risks",
        ],
        "risk_blind_spots": [
            "Insufficient formal risk registers for audit and compliance requirements",
            "Network-based intelligence has recency bias; misses structural and systemic risks",
            "Overconfidence from past relationship-based successes in different contexts",
        ],
        "pattern": "You know people who know things — but you may not document what you know.",
        "prescription": "Convert informal network intelligence into formal risk register entries at least weekly.",
    },
    ("mid", "mixed"): {
        "persona": "The Balanced Practitioner",
        "description": (
            "Balanced blend of intuition and structured analysis, comfortable with ambiguity, "
            "but may lack depth in critical risk categories and commit too slowly under pressure."
        ),
        "strengths": [
            "Balanced blend of intuition and structured analysis — versatile approach",
            "Comfortable with ambiguity and incomplete information",
            "Adapts approach based on project context rather than using one fixed framework",
        ],
        "risk_blind_spots": [
            "Broad capability but potentially insufficient depth in critical risk areas",
            "May not commit to one risk framework strongly enough in high-pressure situations",
            "External systemic risks (geopolitical, economic) are often underweighted",
        ],
        "pattern": "Balance is a strength in stable environments; commit more decisively when pressure mounts.",
        "prescription": "Pre-decide your risk framework BEFORE a crisis hits — not during it.",
    },
    ("senior", "process_guardian"): {
        "persona": "The Strategic Shield",
        "description": (
            "Pattern recognition from 10+ projects and strong legal/contractual risk literacy, "
            "but normalizes minor technical deviations and is vulnerable to past-pattern overconfidence."
        ),
        "strengths": [
            "Pattern recognition from experience (Recognition-Primed Decision making — Klein, 1999)",
            "Strong legal and contractual risk literacy — knows how to protect the project",
            "Effective political navigation and multi-stakeholder management",
        ],
        "risk_blind_spots": [
            "Normalizes minor technical deviations that junior engineers would flag immediately",
            "Past-pattern overconfidence: 'We have done this before' blocks novel risk detection",
            "Digital-tool aversion leads to information asymmetry — juniors see what seniors miss",
        ],
        "pattern": "Your experience is your biggest asset AND your biggest blind spot simultaneously.",
        "prescription": "Mandate a junior 'Micro-Check audit' of every risk register before final signoff.",
    },
    ("senior", "resource_navigator"): {
        "persona": "The Resilient Orchestrator",
        "description": (
            "Exceptional improvisation and relationship capital from high-variance project experience, "
            "but compliance documentation gaps and digital standardization resistance."
        ),
        "strengths": [
            "Exceptional improvisation and resource-optimization under uncertainty",
            "Deep relationship capital across supply chains and stakeholder networks",
            "Crisis management capability built through high-variance project environments",
        ],
        "risk_blind_spots": [
            "Compliance documentation gaps that create audit vulnerabilities under scrutiny",
            "Digital standardization resistance — relies on people over verifiable systems",
            "Succession risk: key relationships and knowledge leave with you",
        ],
        "pattern": "You have navigated chaos, but you may not have documented the map for others.",
        "prescription": "Invest in knowledge management: document your network, processes, and decision rationale formally.",
    },
    ("senior", "mixed"): {
        "persona": "The Global Strategist",
        "description": (
            "Cross-industry pattern recognition and sophisticated risk portfolio management, "
            "but tendency to over-engineer simple situations and miss basic operational risks."
        ),
        "strengths": [
            "Cross-industry and cross-cultural pattern recognition",
            "Sophisticated risk portfolio management at strategic level",
            "Multi-stakeholder navigation in complex, ambiguous environments",
        ],
        "risk_blind_spots": [
            "Complexity-seeker tendency: over-engineers risk analysis for simple projects",
            "Underestimates basic operational risks from over-focus on strategic level",
            "Speed risk: thorough analysis can miss fast-moving threats or opportunities",
        ],
        "pattern": "You see the forest with clarity — but the trees that trip you are the operational basics.",
        "prescription": "Establish a rapid operational risk review (15-min daily stand-up) alongside strategic analysis.",
    },
}

# ── Time Pressure Behavioral Insights ────────────────────────────────────────
# Sources: PMI Schedule Risk Survey 2024; Kahneman & Klein (2009);
# Flyvbjerg (2017) Megaprojects and Risk.

TIME_PRESSURE_INSIGHTS: dict = {
    "high": {
        "risk_escalation_note": (
            "⚡ HIGH TIME PRESSURE detected: External risks escalate by ~40% in compressed timelines "
            "(PMI Schedule Risk Survey 2024). Risk scores in this report reflect that escalation."
        ),
        "behavioral_warning": (
            "Under high time pressure, PMs make 35% more 'good enough' decisions that become "
            "technical debt or defects later (Kahneman & Klein, 2009 — Naturalistic Decision Making). "
            "Urgency bias causes systematic underweighting of external and regulatory risks."
        ),
        "counter_strategy": (
            "Counter-strategy: Pre-commit to your top 3 non-negotiables BEFORE pressure mounts. "
            "What are the risks you will NOT cut corners on, no matter what?"
        ),
    },
    "medium": {
        "risk_escalation_note": (
            "Moderate time pressure: standard risk calibration applied. "
            "Monitor for pressure escalation in the first 20% — it typically intensifies as kick-off approaches."
        ),
        "behavioral_warning": (
            "Mid-pressure projects often experience deferred risk discussions — 'we will address it when it happens'. "
            "Research shows this increases risk remediation cost by 3–5× (PMI Cost of Risk Study 2023)."
        ),
        "counter_strategy": (
            "Schedule a formal risk identification session in Week 2 of the project — "
            "before pressure escalates and teams assume risks are already covered."
        ),
    },
    "low": {
        "risk_escalation_note": (
            "Low time pressure: excellent opportunity for deep risk analysis. "
            "Use this window for comprehensive surveys, stakeholder alignment, and scenario planning."
        ),
        "behavioral_warning": (
            "Warning: low-pressure projects paradoxically suffer from complacency. "
            "'We have time to fix it later' is the leading cause of late-stage surprises. "
            "Studies show 68% of 'comfortable' project timelines still overrun (Flyvbjerg, 2017)."
        ),
        "counter_strategy": (
            "Use this planning window to run 3-scenario risk models (pessimistic/realistic/optimistic) "
            "and stress-test key assumptions with external stakeholders before commitment."
        ),
    },
}

# ── Decision Style Risk Insights ─────────────────────────────────────────────
DECISION_STYLE_INSIGHTS: dict = {
    "intuition": {
        "strength": "Fast, pattern-driven decisions under uncertainty — effective for familiar contexts.",
        "blind_spot": (
            "Availability heuristic: overweights recently-experienced risks and underweights "
            "novel or regulatory risks that haven't been personally encountered yet (Kahneman, 2011)."
        ),
        "prescription": "Complement intuition with one structured checklist for risks you personally have NOT experienced before.",
    },
    "balance": {
        "strength": "Balanced approach — can switch between intuitive and analytical modes based on context.",
        "blind_spot": (
            "May default to the comfortable middle ground; high-pressure situations require decisive "
            "commitment to one approach rather than a hybrid that satisfies neither."
        ),
        "prescription": "Pre-decide which mode (intuition vs. formal tools) applies to each risk category before the project starts.",
    },
    "formal_tools": {
        "strength": "Systematic, auditable, legally defensible risk analysis with full documentation trail.",
        "blind_spot": (
            "Analysis paralysis risk and over-reliance on tool output as 'ground truth'. "
            "Tools lag reality — physical verification remains irreplaceable for 42% of risk categories "
            "(Thesis research findings, Kansara 2026)."
        ),
        "prescription": "Pair every formal tool output with a physical verification (site visit, sample check, demo) for critical-path items.",
    },
}


class ContextAnalyzer:
    """
    Analyzes ProjectContext to produce personalized insights, benchmarks,
    and blind spots tailored to the user's specific profile.
    """

    def analyze(self, ctx: "ProjectContext") -> dict:
        """
        Analyze the ProjectContext and return a rich context analysis dictionary.

        Returns a dict with keys:
            persona, benchmarks, time_pressure_insights, decision_style_insights,
            confidence_level
        """
        persona_key = (ctx.experience_level, ctx.cultural_region)
        persona = PERSONA_MATRIX.get(persona_key, PERSONA_MATRIX.get(("mid", "mixed"), {}))

        industry_key = ctx.industry if ctx.industry in INDUSTRY_REGION_BENCHMARKS else "construction"
        industry_benchmarks = INDUSTRY_REGION_BENCHMARKS.get(industry_key, {})
        region_benchmarks = industry_benchmarks.get(
            ctx.cultural_region,
            industry_benchmarks.get("mixed", {}),
        )

        pressure_insights = TIME_PRESSURE_INSIGHTS.get(ctx.time_pressure, TIME_PRESSURE_INSIGHTS["medium"])
        style_insights = DECISION_STYLE_INSIGHTS.get(ctx.decision_style, DECISION_STYLE_INSIGHTS["balance"])

        confidence = self._compute_confidence(ctx)

        return {
            "persona": persona,
            "benchmarks": region_benchmarks,
            "time_pressure_insights": pressure_insights,
            "decision_style_insights": style_insights,
            "confidence_level": confidence,
        }

    def _compute_confidence(self, ctx: "ProjectContext") -> dict:
        """Compute a confidence score for the generated analysis."""
        score = 70  # Base: thesis knowledge base

        if ctx.years_experience > 5:
            score += 5
        if ctx.projects_managed > 10:
            score += 3
        if ctx.industry in ("construction", "manufacturing", "it"):
            score += 8
        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            score += 7
        if len(ctx.top_risks) >= 3:
            score += 5

        label = "High" if score >= 85 else ("Medium" if score >= 70 else "Moderate")

        explanation = (
            f"Based on: thesis knowledge base (core) + "
            f"industry specificity ({'known' if ctx.industry in ('construction', 'manufacturing', 'it') else 'inferred'}) + "
            f"regional profile ({'region-specific' if ctx.cultural_region != 'mixed' else 'general'}) + "
            f"experience data ({'detailed' if ctx.years_experience > 0 else 'minimal'})."
        )

        return {
            "score": min(score, _MAX_CONFIDENCE_SCORE),
            "label": label,
            "explanation": explanation,
        }
