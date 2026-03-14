"""
Framework Recommender — Phase 1 specialist module.

Enhances the baseline framework selection from risk_agent.py with
contextual rationale — explaining *why* each framework applies to the
specific combination of industry, experience level, cultural archetype,
and time pressure for this project manager.
"""
from __future__ import annotations

from typing import List

from agent.knowledge_base import DECISION_FRAMEWORKS
from agent.models import ProjectContext, RiskItem


def _has_high_external_risk(risks: List[RiskItem]) -> bool:
    return any(r.category == "external" and r.level in ("High", "Critical") for r in risks)


class FrameworkRecommender:
    """
    Recommends decision frameworks with personalised rationale.

    Each recommendation dict contains the standard keys from
    :data:`agent.knowledge_base.DECISION_FRAMEWORKS` plus:

    * ``rationale`` — why this framework matters for *this* PM profile
    * ``blind_spot_addressed`` — which personal blind spot it mitigates
    """

    def recommend_frameworks(
        self, ctx: ProjectContext, risks: List[RiskItem]
    ) -> List[dict]:
        """Return a list of framework dicts with personalised rationale."""
        recommendations: List[dict] = []

        # ── Safety Premium — always recommended ──────────────────────────────
        sp = dict(DECISION_FRAMEWORKS["safety_premium"])
        sp["name"] = "Safety Premium"
        if ctx.time_pressure == "high":
            sp["rationale"] = (
                "High time pressure is present — the temptation to under-specify "
                "materials and skip buffers is highest right now. Investing 10–15% "
                "upfront is your single most cost-effective risk mitigation."
            )
            sp["blind_spot_addressed"] = (
                "Cutting corners under pressure: a pattern that creates 200%+ rework costs."
            )
        elif ctx.experience_level == "junior":
            sp["rationale"] = (
                "Junior PMs often optimise for initial budget approval. The Safety "
                "Premium reframes quality investment as risk mitigation, not overspend."
            )
            sp["blind_spot_addressed"] = (
                "Prioritising short-term approval over long-term risk reduction."
            )
        else:
            sp["rationale"] = (
                "93% of experienced PMs deliberately invest a Safety Premium. "
                "It is the single intervention with the highest ROI across all "
                "industries and experience levels studied in this research."
            )
            sp["blind_spot_addressed"] = (
                "Under-provisioning for uncertainty in early planning stages."
            )
        recommendations.append(sp)

        # ── Two-Way Team Model — always recommended ───────────────────────────
        tw = dict(DECISION_FRAMEWORKS["two_way_team_model"])
        tw["name"] = "Two-Way Team Model"
        if ctx.experience_level == "senior":
            tw["rationale"] = (
                "Senior PMs are vulnerable to 'normalising' minor deviations that "
                "juniors immediately flag. Pairing a junior for micro-checks is your "
                "fastest route to catching the blind spots experience creates."
            )
            tw["blind_spot_addressed"] = (
                "Pattern-match overconfidence that filters out weak but important signals."
            )
        elif ctx.experience_level == "junior":
            tw["rationale"] = (
                "As a junior PM, the Two-Way Team Model gives you a structured shield "
                "for legal and strategic risk decisions you have not yet encountered."
            )
            tw["blind_spot_addressed"] = (
                "Underestimating external, regulatory, and contractual risk dimensions."
            )
        else:
            tw["rationale"] = (
                "Mid-level PMs benefit most from structured perspective pairing: your "
                "technical grounding paired with a senior's strategic view covers the "
                "complete risk spectrum."
            )
            tw["blind_spot_addressed"] = (
                "Context-switch gaps when transitioning from technical to strategic risk."
            )
        recommendations.append(tw)

        # ── Somatic Verification — for physical industries or high pressure ───
        if ctx.industry in ("construction", "manufacturing") or ctx.time_pressure == "high":
            sv = dict(DECISION_FRAMEWORKS["somatic_verification"])
            sv["name"] = "Somatic Verification"
            if ctx.cultural_region == "process_guardian":
                sv["rationale"] = (
                    "Process Guardians trust BIM models and digital dashboards more "
                    "than on-site reality. Physical inspections catch what the model "
                    "cannot: soil variations, material quality, human factors."
                )
                sv["blind_spot_addressed"] = (
                    "Over-reliance on digital tools as the sole source of truth."
                )
            else:
                sv["rationale"] = (
                    "Physical verification complements your intuition-driven approach "
                    "by grounding decisions in observable, tamper-resistant evidence."
                )
                sv["blind_spot_addressed"] = (
                    "Acting on incomplete or informally-sourced information."
                )
            recommendations.append(sv)

        # ── Bureaucratic Shield — for senior/formal-tools/high-liability ─────
        if ctx.experience_level == "senior" or ctx.decision_style == "formal_tools":
            bs = dict(DECISION_FRAMEWORKS["bureaucratic_shield"])
            bs["name"] = "Bureaucratic Shield"
            bs["rationale"] = (
                "Formal documentation of risk decisions is a personal liability shield "
                "as much as a technical tool — especially critical in high-stakes, "
                "multi-stakeholder environments."
            )
            bs["blind_spot_addressed"] = (
                "Relying on experience and intuition without creating an audit trail."
            )
            recommendations.append(bs)

        # ── Truth-Link Technology — for manufacturing and IT ─────────────────
        if ctx.industry in ("manufacturing", "it"):
            tl = dict(DECISION_FRAMEWORKS["truth_link_technology"])
            tl["name"] = "Truth-Link Technology"
            if ctx.industry == "manufacturing":
                tl["rationale"] = (
                    "93.3% of manufacturing managers distrust manual status reports. "
                    "IoT sensors, acoustic monitors, and digital twins provide "
                    "continuous, tamper-resistant production health data."
                )
                tl["blind_spot_addressed"] = (
                    "Calibration drift and micro-deviations that self-reports miss."
                )
            else:
                tl["rationale"] = (
                    "In IT projects, manual sprint reports mask hidden integration "
                    "complexity. Automated CI/CD telemetry and SLA dashboards provide "
                    "the objective data stream that replaces trust with evidence."
                )
                tl["blind_spot_addressed"] = (
                    "Velocity metrics that hide technical debt and integration failures."
                )
            recommendations.append(tl)

        # ── Reverse Training — for cultural archetypes ────────────────────────
        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            rt = dict(DECISION_FRAMEWORKS["reverse_training"])
            rt["name"] = "Reverse Training"
            if ctx.cultural_region == "process_guardian":
                rt["rationale"] = (
                    "Process Guardians have systematic blind spots in crisis improvisation. "
                    "Deliberate exposure to Resource Navigator approaches (Jugaad-style "
                    "thinking) builds the adaptability that processes alone cannot provide."
                )
                rt["blind_spot_addressed"] = (
                    "Decision paralysis when formal tools fail or situations are novel."
                )
            else:
                rt["rationale"] = (
                    "Resource Navigators are highly adaptive but create auditability gaps. "
                    "Structured digital accountability training complements your "
                    "relationship-based strength with repeatable documentation discipline."
                )
                rt["blind_spot_addressed"] = (
                    "Compliance and scalability gaps when moving into formal environments."
                )
            recommendations.append(rt)

        return recommendations
