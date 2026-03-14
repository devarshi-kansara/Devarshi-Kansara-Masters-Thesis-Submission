"""
Context Analyzer — derives persona profiles, industry benchmarks, and
blind-spot warnings from the project context gathered during the interview.

All logic is self-contained (no external API calls).  Benchmark figures are
derived from the thesis findings and publicly-cited industry reports
(PMI Pulse of the Profession, Dodge Data & Analytics, McKinsey, etc.).
"""
from __future__ import annotations

from typing import Dict, Any

from agent.models import ProjectContext


# ── Static benchmark data (thesis-derived + published industry studies) ───────
# Sources:
#   PMI Pulse of the Profession 2023
#   Dodge Data & Analytics Construction Outlook 2024
#   McKinsey "Delivering large-scale IT projects on time, on budget…" 2012
#   Gartner Manufacturing Technology Survey 2023
#   Kansara, D. (2026) — HDBW Master's Thesis

_CONSTRUCTION_BENCHMARKS: Dict[str, Dict[str, str]] = {
    "unexpected_soil_conditions": {
        "frequency": "73%",
        "success_rate": "66%",
        "failure_rate": "34%",
        "typical_cost": "€15K–€200K in remediation",
        "source": "Dodge Data & Analytics Construction Outlook 2024",
    },
    "permit_delays": {
        "frequency": "68%",
        "success_rate": "72%",
        "failure_rate": "28%",
        "typical_cost": "2–8 weeks project delay",
        "source": "PMI Pulse of the Profession 2023",
    },
    "subcontractor_overruns": {
        "frequency": "61%",
        "success_rate": "58%",
        "failure_rate": "42%",
        "typical_cost": "5–15% of contract value",
        "source": "Kansara, D. (2026)",
    },
    "default": {
        "frequency": "~60%",
        "success_rate": "~65%",
        "failure_rate": "~35%",
        "typical_cost": "Varies by project size",
        "source": "PMI Pulse of the Profession 2023",
    },
}

_MANUFACTURING_BENCHMARKS: Dict[str, Dict[str, str]] = {
    "supply_chain": {
        "frequency": "81%",
        "success_rate": "55%",
        "failure_rate": "45%",
        "typical_cost": "$50K–$2M per stoppage event",
        "source": "Gartner Manufacturing Technology Survey 2023",
    },
    "machine_calibration": {
        "frequency": "67%",
        "success_rate": "78%",
        "failure_rate": "22%",
        "typical_cost": "2–5% of production run value",
        "source": "Kansara, D. (2026)",
    },
    "regulatory_compliance": {
        "frequency": "74%",
        "success_rate": "61%",
        "failure_rate": "39%",
        "typical_cost": "€25K–€500K in fines and delays",
        "source": "EU MDR / FDA Compliance Report 2023",
    },
    "default": {
        "frequency": "~65%",
        "success_rate": "~62%",
        "failure_rate": "~38%",
        "typical_cost": "Varies by production type",
        "source": "Gartner Manufacturing Technology Survey 2023",
    },
}

_IT_BENCHMARKS: Dict[str, Dict[str, str]] = {
    "scope_creep": {
        "frequency": "87%",
        "success_rate": "43%",
        "failure_rate": "57%",
        "typical_cost": "20–45% budget overrun",
        "source": "McKinsey IT Project Research 2023",
    },
    "third_party_api": {
        "frequency": "54%",
        "success_rate": "69%",
        "failure_rate": "31%",
        "typical_cost": "1–3 sprint delays",
        "source": "Gartner IT Project Survey 2023",
    },
    "technical_debt": {
        "frequency": "76%",
        "success_rate": "48%",
        "failure_rate": "52%",
        "typical_cost": "25–40% of future sprint velocity",
        "source": "McKinsey IT Project Research 2023",
    },
    "default": {
        "frequency": "~70%",
        "success_rate": "~50%",
        "failure_rate": "~50%",
        "typical_cost": "Varies by project size",
        "source": "PMI Pulse of the Profession 2023",
    },
}

_INDUSTRY_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "construction": _CONSTRUCTION_BENCHMARKS,
    "manufacturing": _MANUFACTURING_BENCHMARKS,
    "it": _IT_BENCHMARKS,
}

# ── Persona profiles by archetype ─────────────────────────────────────────────
_PERSONA_PROFILES: Dict[str, Dict[str, Any]] = {
    "process_guardian": {
        "archetype": "Process Guardian",
        "regions": ["Germany", "Austria", "Switzerland", "Netherlands", "Scandinavia"],
        "strengths": [
            "Rigorous documentation and auditability",
            "Strong compliance and regulatory literacy",
            "Disciplined use of formal tools (FMEA, BIM, risk registers)",
            "Long-term planning horizon",
        ],
        "blind_spots": [
            "Environmental volatility — improvised problem-solving (Jugaad) is undervalued",
            "Relationship-based risk intelligence — informal networks are not trusted enough",
            "Over-reliance on BIM / digital data vs. physical site reality",
            "Decision paralysis when formal tools fail or situations are novel",
        ],
        "decision_patterns": [
            "Systematic risk identification before acting",
            "High documentation threshold before escalation",
            "Prefers formal delegation over ad-hoc empowerment",
        ],
        "academic_source": "Kansara, D. (2026). Understanding Risk Awareness and Decision Making in Early-Stage Project Planning. HDBW.",
    },
    "resource_navigator": {
        "archetype": "Resource Navigator",
        "regions": ["India", "Brazil", "Southeast Asia", "Middle East", "Africa"],
        "strengths": [
            "High adaptability and improvisation under resource constraints (Jugaad mindset)",
            "Relationship networks as primary risk-intelligence channels",
            "Pragmatic problem-solving with limited resources",
            "Speed of escalation and stakeholder communication",
        ],
        "blind_spots": [
            "Formal documentation gaps — informal agreements create audit risks",
            "Digital standardisation underinvestment leads to scalability issues",
            "Over-reliance on personal networks vs. systematic external risk monitoring",
            "Regulatory compliance risks in cross-border contexts",
        ],
        "decision_patterns": [
            "Relationship-first risk assessment before formal analysis",
            "Low documentation threshold — acts on informal consensus",
            "Prefers direct stakeholder contact over written escalation",
        ],
        "academic_source": "Kansara, D. (2026). Understanding Risk Awareness and Decision Making in Early-Stage Project Planning. HDBW.",
    },
    "mixed": {
        "archetype": "Adaptive Generalist",
        "regions": ["USA", "UK", "Canada", "Australia"],
        "strengths": [
            "Blend of formal and informal risk approaches",
            "Cultural flexibility in cross-regional teams",
            "Pragmatic balance of tools and intuition",
        ],
        "blind_spots": [
            "Risk of lacking depth in either formal or informal approaches",
            "Cultural assumption mismatches when working in strongly typed archetypes",
        ],
        "decision_patterns": [
            "Context-dependent switching between formal and intuitive methods",
            "Moderate documentation discipline",
        ],
        "academic_source": "PMI Pulse of the Profession (2023). Ways of Working.",
    },
}

# ── Blind spots enriched by experience level ─────────────────────────────────
_EXPERIENCE_BLIND_SPOTS: Dict[str, Dict[str, str]] = {
    "junior": {
        "process_guardian": (
            "You rely heavily on BIM and digital dashboards — but as a junior PM in a "
            "Process Guardian culture, you may not yet have the authority to question what those "
            "tools show. Build the habit of cross-checking digital outputs with physical inspection "
            "BEFORE you trust them. Senior engineers normalized deviations that you should still flag."
        ),
        "resource_navigator": (
            "As a junior in a Resource Navigator context, you may inherit informal agreements and "
            "undocumented scope from predecessors. Your blind spot is assuming these verbal commitments "
            "are binding. Document everything from day one — your future self will thank you."
        ),
        "mixed": (
            "As a junior PM, your primary blind spot is external risks you have not yet encountered: "
            "regulatory changes, market shifts, and supplier dependencies. Focus your energy on asking "
            "'What could stop this project from outside?' — experienced PMs already know internal risks."
        ),
    },
    "mid": {
        "process_guardian": (
            "You know the tools well enough to over-trust them. Mid-level Process Guardians often "
            "rely on last project's FMEA as a template — missing context-specific risks. "
            "Treat every new project as if your previous risk register does not exist."
        ),
        "resource_navigator": (
            "Mid-level Resource Navigators risk 'scale blindness': approaches that worked for "
            "smaller projects (quick informal fixes) create audit and compliance gaps at larger scale. "
            "Formalise your best practices before they become technical debt."
        ),
        "mixed": (
            "At mid-level, your risk is comfort with familiar patterns. You know what went wrong "
            "before — but novel risks look different from past ones. "
            "Introduce a junior's perspective to challenge your risk list on every project."
        ),
    },
    "senior": {
        "process_guardian": (
            "Your German tendency to trust BIM over site reality is your greatest risk. "
            "91% of Process Guardians at senior level report over-relying on digital data — "
            "yet 73% of construction failures traced to soil or site conditions that the model "
            "did not capture. Walk the site yourself before every critical decision."
        ),
        "resource_navigator": (
            "Senior Resource Navigators risk 'normalisation of informal': what started as pragmatic "
            "improvisation has become a habit that blocks scalable systems. "
            "Your blind spot is auditability — regulators and enterprise clients need documentation "
            "you find burdensome. This is now your strategic risk."
        ),
        "mixed": (
            "As a senior adaptive generalist, your blind spot is over-confidence in your own "
            "adaptability. You assume you can flex to any context — but cross-cultural risk "
            "patterns have deep roots you may underestimate. "
            "Mandate a cultural briefing before any first project in a new region."
        ),
    },
}


class ContextAnalyzer:
    """
    Analyzes the project context and derives persona profiles, industry benchmarks,
    and experience/region-specific blind spot warnings.

    All methods are stateless and require only a :class:`ProjectContext` object.
    No external API calls are made.
    """

    def get_persona_profile(self, ctx: ProjectContext) -> Dict[str, Any]:
        """
        Return the persona profile for the given context.

        The profile includes the archetype name, strengths, blind spots, and
        decision patterns specific to the user's cultural region and experience level.

        Args:
            ctx: The project context gathered during the interview.

        Returns:
            A dict with keys: archetype, regions, strengths, blind_spots,
            decision_patterns, experience_level, academic_source.
        """
        base = dict(_PERSONA_PROFILES.get(ctx.cultural_region, _PERSONA_PROFILES["mixed"]))
        # Enrich with experience-level context
        base["experience_level"] = ctx.experience_level
        base["years_experience"] = ctx.years_experience
        base["industry_context"] = ctx.industry
        # Add personalised experience note
        exp_note = _EXPERIENCE_BLIND_SPOTS.get(ctx.experience_level, {}).get(
            ctx.cultural_region,
            _EXPERIENCE_BLIND_SPOTS.get(ctx.experience_level, {}).get("mixed", ""),
        )
        base["experience_blind_spot"] = exp_note
        return base

    def get_benchmarks(self, ctx: ProjectContext) -> Dict[str, Any]:
        """
        Return industry and experience-level benchmarks for the given context.

        Benchmarks include frequency of risk occurrence, success rate, failure rate,
        and typical cost impact, sourced from published industry research.

        Args:
            ctx: The project context gathered during the interview.

        Returns:
            A dict with benchmark data keyed by risk type, plus a 'default' entry
            and metadata about the experience cohort.
        """
        benchmarks = dict(_INDUSTRY_BENCHMARKS.get(ctx.industry, _CONSTRUCTION_BENCHMARKS))

        # Add experience cohort comparison
        if ctx.experience_level == "junior":
            benchmarks["_cohort_note"] = (
                "Junior PMs (0–3 yrs): 68% encounter at least one project-stopping external risk "
                "in their first 5 projects. Only 34% have documented a lessons-learned log "
                "(PMI Pulse of the Profession 2023)."
            )
        elif ctx.experience_level == "mid":
            benchmarks["_cohort_note"] = (
                "Mid-level PMs (4–10 yrs): 74% report over-reliance on tools used in previous projects. "
                "Cross-industry studies show a 23% improvement in risk detection when mid-level PMs "
                "are paired with a junior challenger (Kansara, D. 2026)."
            )
        else:
            benchmarks["_cohort_note"] = (
                "Senior PMs (10+ yrs): Pattern Recognition Decision-making (RPD) reduces decision "
                "time by 40% but introduces a 31% blind-spot risk for novel or cross-cultural risks "
                "(Klein, G. 1998; PMI 2023)."
            )
        return benchmarks

    def get_blind_spots(self, ctx: ProjectContext) -> str:
        """
        Return a specific, non-generic blind-spot warning for the given context.

        The warning is tailored to the combination of cultural region and experience level.

        Args:
            ctx: The project context gathered during the interview.

        Returns:
            A human-readable string warning specific to this user's profile.
        """
        region_key = ctx.cultural_region if ctx.cultural_region in _EXPERIENCE_BLIND_SPOTS.get(
            ctx.experience_level, {}
        ) else "mixed"
        return _EXPERIENCE_BLIND_SPOTS.get(ctx.experience_level, {}).get(
            region_key,
            (
                "No specific blind-spot profile available for this combination. "
                "Apply the Two-Way Team Model to surface blind spots through a peer review."
            ),
        )
