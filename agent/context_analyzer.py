"""
Context Analyzer — Phase 1 specialist module.

Performs deep analysis of the project manager's profile to surface
persona archetypes, experience-specific blind spots, and industry
benchmarks sourced from the thesis knowledge base.
"""
from __future__ import annotations

from typing import List

from agent.models import ProjectContext

# ── Persona profiles keyed by (cultural_region, experience_level) ─────────────
_PERSONA_PROFILES: dict = {
    ("process_guardian", "junior"): {
        "archetype": "Process Guardian — Emerging",
        "strengths": [
            "Strong compliance instinct from early in career",
            "High digital-tool proficiency (BIM, FMEA)",
            "Accurate technical micro-checks",
        ],
        "blind_spots": [
            "Trusts model outputs over physical site inspections",
            "Underestimates informal relationship-based risk intelligence",
            "May be paralysed by procedure when improvisation is needed",
        ],
        "decision_pattern": "Defaults to formal tools; seeks approval before acting",
        "risk_tolerance": "Low — prefers documented justification for every decision",
    },
    ("process_guardian", "mid"): {
        "archetype": "Process Guardian — Consolidating",
        "strengths": [
            "Excellent compliance and documentation culture",
            "Strong legal and contractual awareness (VOB / EU frameworks)",
            "Formal tool mastery (BIM, FMEA, HAZOP)",
        ],
        "blind_spots": [
            "Over-reliance on BIM / digital dashboards vs. on-site reality",
            "Risk of decision paralysis from documentation perfectionism",
            "Underestimates informal networks and relationship intelligence",
        ],
        "decision_pattern": "Trusts processes; adapts only under sustained pressure",
        "risk_tolerance": "Risk-averse — consistently invests Safety Premium",
    },
    ("process_guardian", "senior"): {
        "archetype": "Process Guardian — Expert",
        "strengths": [
            "Deep pattern recognition from complex European projects",
            "Outstanding legal and regulatory risk literacy",
            "Highly effective stakeholder and political navigation",
        ],
        "blind_spots": [
            "Normalises minor technical deviations that juniors would flag",
            "Over-relies on historical patterns that may not fit novel contexts",
            "Digital-tool aversion in later career creates information asymmetry",
        ],
        "decision_pattern": "Pattern-matches rapidly; reluctant to revise established heuristics",
        "risk_tolerance": "Moderate — experience reduces perceived uncertainty",
    },
    ("resource_navigator", "junior"): {
        "archetype": "Resource Navigator — Emerging",
        "strengths": [
            "Natural adaptability and improvisation under constraints",
            "Strong informal network awareness from cultural background",
            "Creative cross-functional problem-solving",
        ],
        "blind_spots": [
            "Skips formal risk documentation, creating auditability gaps",
            "Underestimates regulatory and compliance obligations",
            "Relies too heavily on relationship trust rather than contractual clarity",
        ],
        "decision_pattern": "Acts quickly based on network intelligence; documents afterwards",
        "risk_tolerance": "High — confident in ability to improvise recovery",
    },
    ("resource_navigator", "mid"): {
        "archetype": "Resource Navigator — Consolidating",
        "strengths": [
            "High environmental adaptability (Jugaad-style improvisation)",
            "Rich relationship network as primary risk-intelligence channel",
            "Effective under resource constraints",
        ],
        "blind_spots": [
            "Informal decision-making creates compliance and audit vulnerabilities",
            "Digital standardisation and data-driven accountability gaps",
            "Adapts reactively rather than planning contingencies in advance",
        ],
        "decision_pattern": "Uses relationships and intuition first; formal tools last",
        "risk_tolerance": "Moderately high — trusts improvisation; underweights regulatory risk",
    },
    ("resource_navigator", "senior"): {
        "archetype": "Resource Navigator — Expert",
        "strengths": [
            "Exceptional crisis-management and rapid-recovery skills",
            "Extensive stakeholder network across geographies",
            "Strong intuitive pattern recognition under ambiguity",
        ],
        "blind_spots": [
            "Audit trails and regulatory documentation often neglected",
            "Digital platform adoption resisted in favour of proven relationships",
            "Scalability gaps when moving to larger, more formal organisations",
        ],
        "decision_pattern": "Trusts experience and network; sceptical of formal analysis",
        "risk_tolerance": "High — relies on recovery skills to manage residual risk",
    },
}

_DEFAULT_PERSONA = {
    "archetype": "Balanced Practitioner",
    "strengths": [
        "Combines formal tools with practical experience",
        "Adaptable to various project environments",
    ],
    "blind_spots": [
        "May lack depth in either formal processes or improvisational recovery",
        "Risk of inconsistency when switching between approaches",
    ],
    "decision_pattern": "Situational — balances tools and intuition based on context",
    "risk_tolerance": "Moderate",
}

# ── Industry benchmarks ───────────────────────────────────────────────────────
_BENCHMARKS: dict = {
    "construction": {
        "soil_and_ground_conditions": {
            "label": "Unexpected ground/soil conditions",
            "frequency": "87% of construction PMs encounter this in the first 20%",
            "success_rate": "66% successfully mitigate with upfront surveys",
            "typical_mitigation_cost": "€5 000 – €15 000 (geotechnical survey)",
            "typical_failure_cost": "€200 000 – €500 000 (rework / programme extension)",
        },
        "permit_and_regulatory": {
            "label": "Permit or regulatory delays",
            "frequency": "74% of European construction projects experience at least one permit delay",
            "success_rate": "81% who engage authorities in week 1 avoid critical-path delays",
            "typical_mitigation_cost": "1–2 days of PM engagement time",
            "typical_failure_cost": "4–12 weeks of programme delay",
        },
        "subcontractor_performance": {
            "label": "Subcontractor over-run or failure",
            "frequency": "63% of construction projects experience a subcontractor deviation",
            "success_rate": "78% who apply Two-Way Team monitoring contain costs",
            "typical_mitigation_cost": "5–10% uplift on subcontract value for supervision",
            "typical_failure_cost": "15–40% budget overrun if undetected until late",
        },
    },
    "manufacturing": {
        "supply_chain_disruption": {
            "label": "Supply chain disruption",
            "frequency": "79% of manufacturers experienced significant supply disruptions (post-2020)",
            "success_rate": "70% who mapped single-source dependencies avoided critical stoppages",
            "typical_mitigation_cost": "2–3% of procurement budget for dual-sourcing",
            "typical_failure_cost": "Production line stoppage: €10 000 – €50 000 per day",
        },
        "machine_calibration_drift": {
            "label": "Machine calibration drift / tolerance failure",
            "frequency": "68% of precision manufacturing projects record at least one calibration incident",
            "success_rate": "82% who implement IoT monitoring catch drift before product failure",
            "typical_mitigation_cost": "€2 000 – €8 000 for sensor infrastructure per line",
            "typical_failure_cost": "€50 000 – €500 000 in scrapped product and rework",
        },
        "regulatory_compliance": {
            "label": "Regulatory compliance failure (EU MDR / FDA)",
            "frequency": "55% of new manufacturing projects underestimate compliance lead time",
            "success_rate": "89% who engage compliance specialists in week 1 avoid critical delays",
            "typical_mitigation_cost": "3–5% of project budget for early compliance work",
            "typical_failure_cost": "Market launch delayed 6–18 months; potential recall costs",
        },
    },
    "it": {
        "scope_creep": {
            "label": "Scope creep / requirements volatility",
            "frequency": "82% of IT projects experience significant scope change",
            "success_rate": "71% who define a hard Definition of Done in week 1 contain scope drift",
            "typical_mitigation_cost": "2–4 hours of stakeholder workshop time",
            "typical_failure_cost": "30–50% budget overrun; 40–60% timeline extension",
        },
        "third_party_dependency": {
            "label": "Third-party API / vendor failure",
            "frequency": "67% of IT projects are blocked by an external dependency at least once",
            "success_rate": "76% who conduct dependency SLA review upfront avoid critical blockers",
            "typical_mitigation_cost": "1–2 days of architectural spike / proof-of-concept",
            "typical_failure_cost": "1–4 weeks of blocked development per dependency failure",
        },
        "technical_debt": {
            "label": "Underestimated technical debt",
            "frequency": "74% of projects that inherit legacy code exceed their initial schedule estimate",
            "success_rate": "65% who run an early code-quality audit set realistic expectations",
            "typical_mitigation_cost": "1 sprint of dedicated refactoring per major debt area",
            "typical_failure_cost": "2–5x velocity reduction over project lifetime",
        },
    },
}


class ContextAnalyzer:
    """Analyses a :class:`ProjectContext` to surface persona insights and benchmarks."""

    def get_persona_profile(self, ctx: ProjectContext) -> dict:
        """Return a persona profile dict for the given context."""
        key = (ctx.cultural_region, ctx.experience_level)
        profile = _PERSONA_PROFILES.get(key, _DEFAULT_PERSONA).copy()
        # Enrich with time-pressure note
        if ctx.time_pressure == "high":
            profile = dict(profile)
            profile["time_pressure_note"] = (
                "⚠ High time pressure detected: your blind spots are amplified. "
                "Shortcuts taken now are the primary source of critical failures in the first 20%."
            )
        return profile

    def get_benchmarks(self, ctx: ProjectContext) -> dict:
        """Return industry-relevant benchmark data for the given context."""
        return _BENCHMARKS.get(ctx.industry, {})

    def get_blind_spots(self, ctx: ProjectContext) -> List[str]:
        """Return a list of blind spots specific to this profile."""
        profile = self.get_persona_profile(ctx)
        blind_spots: List[str] = list(profile.get("blind_spots", []))

        # Add industry-specific blind spots
        from agent.knowledge_base import INDUSTRY_RISKS
        ind_data = INDUSTRY_RISKS.get(ctx.industry, {})
        for bs in ind_data.get("blind_spots_for_outsiders", []):
            if bs not in blind_spots:
                blind_spots.append(bs)

        return blind_spots
