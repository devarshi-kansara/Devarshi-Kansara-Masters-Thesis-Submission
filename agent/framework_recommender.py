"""
Framework Recommender — dynamically selects and rationale-enriches decision
frameworks based on project context and identified risks.

Includes all six thesis frameworks plus three additional frameworks
(Pre-Mortem, Black Swan Awareness, 3-Scenario Analysis) drawn from
established PM research.
"""
from __future__ import annotations

from typing import List, Dict, Any

from agent.knowledge_base import DECISION_FRAMEWORKS
from agent.models import ProjectContext, RiskItem


# ── Extended framework library (thesis + new) ─────────────────────────────────
_EXTENDED_FRAMEWORKS: Dict[str, Dict[str, Any]] = {
    # --- Thesis frameworks (re-exported with extended metadata) ---------------
    "safety_premium": {
        **DECISION_FRAMEWORKS["safety_premium"],
        "success_rate": "93%",
        "blind_spot_it_addresses": "Underestimating early-stage investment to avoid late-stage cost explosions.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["universal", "construction", "manufacturing", "it", "high_pressure", "low_pressure"],
    },
    "somatic_verification": {
        **DECISION_FRAMEWORKS["somatic_verification"],
        "success_rate": "87%",
        "blind_spot_it_addresses": "Over-trust in digital dashboards and BIM models vs. ground truth.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["construction", "manufacturing", "high_pressure", "process_guardian", "senior"],
    },
    "bureaucratic_shield": {
        **DECISION_FRAMEWORKS["bureaucratic_shield"],
        "success_rate": "89%",
        "blind_spot_it_addresses": "Personal liability exposure in high-stakes regulatory environments.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["senior", "formal_tools", "construction", "manufacturing", "high_pressure"],
    },
    "two_way_team_model": {
        **DECISION_FRAMEWORKS["two_way_team_model"],
        "success_rate": "91%",
        "blind_spot_it_addresses": "Single-perspective risk blindness — neither junior nor senior sees the full picture alone.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["universal", "construction", "manufacturing", "it", "junior", "mid", "senior"],
    },
    "reverse_training": {
        **DECISION_FRAMEWORKS["reverse_training"],
        "success_rate": "84%",
        "blind_spot_it_addresses": "Cross-cultural assumption mismatches that neither team member sees.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["cross_cultural", "process_guardian", "resource_navigator"],
    },
    "truth_link_technology": {
        **DECISION_FRAMEWORKS["truth_link_technology"],
        "success_rate": "86%",
        "blind_spot_it_addresses": "Manual reporting distortion — 93.3% of managers distrust manual status reports.",
        "academic_source": "Kansara, D. (2026). HDBW Master's Thesis.",
        "tags": ["manufacturing", "it", "formal_tools", "high_pressure"],
    },
    # --- New frameworks beyond the thesis ------------------------------------
    "pre_mortem": {
        "description": (
            "Conduct a structured 'Pre-Mortem' session: ask the team to imagine the project has "
            "already failed catastrophically and work backwards to identify what caused it. "
            "This reverses normal optimism bias and surfaces risks that positive planning misses. "
            "Originated by Gary Klein (1989) and popularised by Daniel Kahneman (Thinking, Fast and Slow, 2011)."
        ),
        "when_to_apply": (
            "Before finalising the project plan; whenever the team shows high confidence or optimism bias; "
            "ideal for low-to-medium time pressure contexts where planning depth is possible."
        ),
        "example": (
            "A construction team runs a 90-minute Pre-Mortem workshop: 'It is 12 months from now and the "
            "project is a disaster — what happened?' The team identifies 3 risks that were not on the "
            "official register, including a supplier bankruptcy and a permit interpretation dispute."
        ),
        "success_rate": "78%",
        "blind_spot_it_addresses": "Optimism bias and planning fallacy — teams systematically underestimate risk frequency.",
        "academic_source": "Klein, G. (1989). Performing a Project Pre-Mortem. Harvard Business Review.",
        "tags": ["universal", "low_pressure", "medium_pressure", "junior", "mid"],
    },
    "black_swan_awareness": {
        "description": (
            "Systematically scan for low-probability, high-impact events ('Black Swans') that fall "
            "outside the standard risk register. Use the 'Inverse Pareto' method: identify the 20% of "
            "risks that could cause 80% of total project damage, even if their probability is very low. "
            "Based on Taleb, N.N. (2007) The Black Swan."
        ),
        "when_to_apply": (
            "High-stakes projects; novel environments (new regions, new technologies); "
            "projects with single points of failure or cascading dependencies."
        ),
        "example": (
            "An IT project includes a Black Swan scan and identifies: 'What if the cloud provider "
            "has a 72-hour outage during go-live?' A contingency plan is drafted for local failover, "
            "costing €2K but preventing a potential €500K SLA breach."
        ),
        "success_rate": "71%",
        "blind_spot_it_addresses": "Normalcy bias — assuming the future will resemble the past when it may not.",
        "academic_source": "Taleb, N.N. (2007). The Black Swan: The Impact of the Highly Improbable. Random House.",
        "tags": ["it", "manufacturing", "senior", "high_pressure", "formal_tools"],
    },
    "three_scenario_analysis": {
        "description": (
            "Develop three explicit scenarios for the project outcome: Best Case (optimistic), "
            "Most Likely Case (realistic), and Worst Case (pessimistic). Plan the response for each. "
            "This prevents the common trap of planning only for the expected case and being "
            "unprepared for variance. Rooted in scenario planning literature (Schwartz, P. 1991)."
        ),
        "when_to_apply": (
            "Early project planning phase; when facing high uncertainty about external conditions "
            "(regulatory, market, supplier); ideal for junior and mid-level PMs building planning discipline."
        ),
        "example": (
            "A manufacturing PM creates three scenarios: Best (all suppliers deliver on time, 6-month timeline), "
            "Most Likely (one supplier delay, 7-month timeline with 5% budget increase), "
            "Worst (supply chain disruption + regulatory review, 10-month timeline + 20% budget increase). "
            "The client approves the budget buffer for the 'Most Likely' scenario upfront."
        ),
        "success_rate": "82%",
        "blind_spot_it_addresses": "Single-point estimation — planning only for the expected case leaves no resilience.",
        "academic_source": "Schwartz, P. (1991). The Art of the Long View. Doubleday.",
        "tags": ["universal", "low_pressure", "medium_pressure", "junior", "mid", "construction", "manufacturing", "it"],
    },
}


class FrameworkRecommender:
    """
    Dynamically selects and enriches decision frameworks based on the user's
    project context and identified risk register.

    Each recommended framework includes: name, description, why_for_you,
    when_to_apply, example, success_rate, blind_spot_it_addresses, academic_source.
    """

    def recommend_frameworks(
        self, ctx: ProjectContext, risks: List[RiskItem]
    ) -> List[Dict[str, Any]]:
        """
        Select the most relevant frameworks for this context and risk profile,
        enriched with personalised rationale ('why_for_you').

        Args:
            ctx: The project context gathered during the interview.
            risks: The full risk register (used to detect risk-specific triggers).

        Returns:
            A list of framework dicts, each including all standard fields plus
            'why_for_you' (personalised rationale) and 'name'.
        """
        selected: List[Dict[str, Any]] = []
        seen: set = set()

        def _add(key: str, why: str) -> None:
            if key not in seen and key in _EXTENDED_FRAMEWORKS:
                fw = dict(_EXTENDED_FRAMEWORKS[key])
                fw["name"] = self._get_display_name(key)
                fw["why_for_you"] = why
                selected.append(fw)
                seen.add(key)

        # ── Universal frameworks (always recommended) ─────────────────────
        _add(
            "safety_premium",
            f"As a {ctx.experience_level} PM in {ctx.industry}, investing upfront in quality "
            f"materials and larger buffers is the single highest-return action in the first 20%. "
            f"93% of experienced PMs use this approach to avoid late-stage cost explosions.",
        )
        _add(
            "two_way_team_model",
            f"The Two-Way Team Model is critical for every project. At {ctx.experience_level} level, "
            + (
                "you excel at micro-checks — pair with a senior for the strategic shield."
                if ctx.experience_level == "junior"
                else (
                    "mandate a junior Micro-Check review on your risk register before finalising it."
                    if ctx.experience_level == "senior"
                    else "you bridge both roles — use this consciously to cover the full risk spectrum."
                )
            ),
        )

        # ── Industry-specific frameworks ──────────────────────────────────
        if ctx.industry in ("construction", "manufacturing"):
            _add(
                "somatic_verification",
                f"In {ctx.industry}, digital dashboards often lag physical reality by days or weeks. "
                "Somatic Verification — walking the site or production floor yourself — catches what "
                "BIM models and sensor reports miss. This is especially critical under high time pressure "
                "when the temptation to rely on remote data is highest.",
            )

        if ctx.industry in ("manufacturing", "it"):
            _add(
                "truth_link_technology",
                f"In {ctx.industry}, manual status reporting has a 93.3% distrust rate among "
                "experienced PMs. Truth-Link Technology (IoT sensors, digital twins, automated CI/CD "
                "dashboards) eliminates the human-reporting gap and gives you tamper-resistant data.",
            )

        # ── Experience-level frameworks ───────────────────────────────────
        if ctx.experience_level == "senior" or ctx.decision_style == "formal_tools":
            _add(
                "bureaucratic_shield",
                f"As a {'senior PM' if ctx.experience_level == 'senior' else 'formal-tools user'}, "
                "the Bureaucratic Shield protects you personally in high-liability situations. "
                "Documented FMEA and risk registers are not just technical tools — they are your "
                "legal defence if a risk materialises and decisions are audited.",
            )

        # ── Cross-cultural frameworks ─────────────────────────────────────
        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            _add(
                "reverse_training",
                f"As a {ctx.cultural_region.replace('_', ' ').title()}, your cultural archetype has "
                "specific blind spots that the opposite archetype can address. Reverse Training "
                "deliberately cross-trains you in the skills your culture undervalues — "
                + (
                    "crisis adaptability and improvised problem-solving (Jugaad)."
                    if ctx.cultural_region == "process_guardian"
                    else "formal documentation and digital standardisation."
                ),
            )

        # ── High-pressure additional frameworks ───────────────────────────
        if ctx.time_pressure == "high":
            _add(
                "black_swan_awareness",
                "Under high time pressure, teams compress risk analysis and systematically miss "
                "low-probability, high-impact events. A 30-minute Black Swan scan before starting "
                "is your cheapest insurance — it costs almost nothing but can prevent catastrophic surprises.",
            )

        # ── Risk-register triggered frameworks ───────────────────────────
        high_critical_risks = [r for r in risks if r.level in ("High", "Critical")]
        if high_critical_risks:
            _add(
                "pre_mortem",
                f"You have {len(high_critical_risks)} High/Critical risk(s) in your register. "
                "A Pre-Mortem session will surface additional risks the team is currently "
                "optimising away — the 'imagined failure' technique is proven to catch what "
                "standard risk registers miss.",
            )

        # ── Low/medium pressure — planning depth frameworks ───────────────
        if ctx.time_pressure in ("low", "medium"):
            _add(
                "three_scenario_analysis",
                f"With {ctx.time_pressure} time pressure, you have the planning bandwidth for "
                "3-Scenario Analysis. This prevents the most common planning failure: optimising "
                "only for the expected case. Develop Best/Most Likely/Worst Case scenarios and "
                "get sponsor sign-off on the 'Most Likely' budget buffer now.",
            )

        # ── Soil risk specific ────────────────────────────────────────────
        soil_keywords = {"soil", "ground", "foundation", "excavation", "geotechnical"}
        has_soil_risk = any(
            any(kw in r.description.lower() for kw in soil_keywords) for r in risks
        )
        if has_soil_risk and ctx.industry == "construction":
            # Ensure somatic verification is present for soil risks
            _add(
                "somatic_verification",
                "You have a soil-related risk in your register. Somatic Verification is essential: "
                "physically inspect the excavation area before approving foundation work. "
                "73% of German PMs who relied solely on BIM reports for soil conditions "
                "encountered surprises during excavation (Dodge Data 2024).",
            )
            if ctx.cultural_region == "process_guardian":
                # Also push safety premium with specific soil context
                if "safety_premium" in seen:
                    # Update why_for_you for safety premium
                    for fw in selected:
                        if fw["name"] == "Safety Premium":
                            fw["why_for_you"] += (
                                " For soil risks specifically: specify a higher-grade concrete and "
                                "a geotechnical survey BEFORE any site commitment. The €5K–€15K "
                                "survey cost avoids the €15K–€200K rework that 34% of German "
                                "construction PMs face (Dodge Data 2024)."
                            )

        return selected

    @staticmethod
    def _get_display_name(key: str) -> str:
        """Convert framework key to display name."""
        _NAMES: Dict[str, str] = {
            "safety_premium": "Safety Premium",
            "somatic_verification": "Somatic Verification",
            "bureaucratic_shield": "Bureaucratic Shield",
            "two_way_team_model": "Two-Way Team Model",
            "reverse_training": "Reverse Training",
            "truth_link_technology": "Truth-Link Technology",
            "pre_mortem": "Pre-Mortem Analysis",
            "black_swan_awareness": "Black Swan Awareness",
            "three_scenario_analysis": "3-Scenario Analysis",
        }
        return _NAMES.get(key, key.replace("_", " ").title())
