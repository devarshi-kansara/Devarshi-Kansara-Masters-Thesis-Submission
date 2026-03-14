"""
Dynamic framework recommender for the risk assessment agent.

Goes beyond the six core thesis frameworks to include emerging methodologies:
Black Swan Analysis, Bayesian Risk Updating, Lean Risk Buffers,
Pre-Mortem Analysis, and 3-Scenario Risk Planning.

Framework selection is context-driven: experience level, cultural region,
industry, time pressure, and decision style all influence which frameworks
are recommended and in what order.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from agent.knowledge_base import DECISION_FRAMEWORKS

if TYPE_CHECKING:
    from agent.models import ProjectContext

# ── Extended Framework Definitions ───────────────────────────────────────────
# These frameworks go beyond the original thesis frameworks.

EXTENDED_FRAMEWORKS: dict = {
    "black_swan_analysis": {
        "name": "Black Swan Analysis",
        "description": (
            "Developed by Nassim Taleb (2007), Black Swan Analysis focuses on identifying and "
            "preparing for rare, high-impact events that are invisible to standard probability–impact "
            "matrices. Rather than estimating probability, it asks: 'If this happens, can we survive?' "
            "The goal is robustness and anti-fragility, not prediction."
        ),
        "when_to_apply": (
            "When the project operates in a volatile, geopolitically exposed, or rapidly-evolving "
            "industry. Especially relevant for tail risks (high impact, low probability) that would "
            "be project-ending if they materialise."
        ),
        "example": (
            "Construction in Germany: 'What if EU building codes change fundamentally due to a "
            "structural disaster elsewhere? Can we redesign within 10% of budget?' "
            "Answer: maintain a 15% 'regulatory shock' contingency buffer built into the contract."
        ),
        "academic_basis": "Taleb, N.N. (2007). The Black Swan: The Impact of the Highly Improbable. Random House.",
        "best_for_industries": ["construction", "manufacturing", "it"],
        "best_for_experience": ["mid", "senior"],
    },
    "bayesian_risk_updating": {
        "name": "Bayesian Risk Updating",
        "description": (
            "Bayesian networks enable risk assessments to be continuously updated as new field data "
            "arrives. Initial risk estimates (priors) are combined with observed evidence to produce "
            "updated posterior risk estimates. This replaces static risk snapshots with living risk "
            "models that evolve with the project, reducing uncertainty progressively."
        ),
        "when_to_apply": (
            "Complex projects with multiple interdependent risks, or projects where field data "
            "progressively reduces uncertainty (construction surveys, manufacturing pilot runs, "
            "IT spike results, market research). Most valuable when initial uncertainty is high."
        ),
        "example": (
            "Soil risk example: initial survey gives P(poor soil) = 30%. After first boring test shows "
            "good results, update to P(poor soil) = 15%. After second boring confirms, P(poor soil) = 8%. "
            "Risk level adjusts in real-time rather than being fixed at project start."
        ),
        "academic_basis": "Straub, D. (2011). Reliability updating with equality information. Probabilistic Engineering Mechanics, 26(2), 254–258.",
        "best_for_industries": ["construction", "manufacturing"],
        "best_for_experience": ["senior"],
    },
    "lean_risk_buffers": {
        "name": "Lean Risk Buffers",
        "description": (
            "Adapted from the Toyota Lean Production System, Lean Risk Buffers apply 'just-in-time' "
            "philosophy to risk management: maintain minimal necessary buffers (time, cost, capacity) "
            "for the HIGHEST-impact risks, and deliberately eliminate buffers for low-impact risks. "
            "This contrasts with traditional 'buffer everything equally' approaches that waste resources "
            "and breed complacency."
        ),
        "when_to_apply": (
            "When time or budget pressure forces explicit trade-offs between risk mitigation investments. "
            "Forces the discipline of identifying exactly where buffers create the most value vs. "
            "where they are pure waste."
        ),
        "example": (
            "Manufacturing project: allocate a 20% time buffer for machine calibration validation "
            "(high-impact, hard to detect). Zero buffer for standard documentation review (low-impact, "
            "can be parallelised). Concentrate your limited risk capital precisely where it matters."
        ),
        "academic_basis": "Womack, J.P. & Jones, D.T. (2003). Lean Thinking: Banish Waste and Create Wealth in Your Corporation. Free Press.",
        "best_for_industries": ["manufacturing", "construction", "it"],
        "best_for_experience": ["mid", "senior"],
    },
    "pre_mortem_analysis": {
        "name": "Pre-Mortem Analysis",
        "description": (
            "Popularised by Gary Klein (1999) and validated by Kahneman (2011), Pre-Mortem Analysis "
            "asks the team to imagine the project has already failed spectacularly, then work backwards "
            "to identify why. This 'prospective hindsight' technique overcomes optimism bias and "
            "authority gradients — team members feel safe surfacing risks because failure is already "
            "'given' in the exercise."
        ),
        "when_to_apply": (
            "At the end of the planning phase — ideal as the capstone of your First 20% Risk Workshop. "
            "Especially powerful when teams have authority gradients (senior PM dominates and junior "
            "members are reluctant to voice concerns)."
        ),
        "example": (
            "Gather the team and say: 'It is 6 months from now. The project has failed badly. "
            "We are writing the post-mortem report. What happened? Write down your top 3 causes — "
            "anonymously.' Collect all answers, then discuss. Typically reveals 3–5 hidden risks "
            "not in the official risk register — the ones people knew but were afraid to say."
        ),
        "academic_basis": "Klein, G. (1999). Sources of Power: How People Make Decisions. MIT Press. Validated by Kahneman, D. (2011). Thinking, Fast and Slow.",
        "best_for_industries": ["construction", "manufacturing", "it"],
        "best_for_experience": ["junior", "mid", "senior"],
    },
    "scenario_planning_3x": {
        "name": "3-Scenario Risk Planning",
        "description": (
            "Rather than a single-point risk estimate, develop three explicit, named scenarios: "
            "Optimistic (best case, low confidence), Realistic (most likely, moderate confidence), "
            "and Pessimistic (stress case, explicit preparation required). "
            "Validated by Lempert et al. (2003) as 47% more accurate than single-point forecasts "
            "for complex, uncertain environments."
        ),
        "when_to_apply": (
            "For any risk with high uncertainty or where the consequences of the pessimistic scenario "
            "are substantially different from the realistic scenario. Particularly powerful for "
            "procurement, regulatory, and geotechnical risks."
        ),
        "example": (
            "Supply chain risk: Optimistic: 95% on-time delivery, no buffer needed. "
            "Realistic: 85% on-time, 10% safety stock required. "
            "Pessimistic: 60% on-time (geopolitical disruption), 30% buffer + activated alternative supplier needed. "
            "Decision: invest in 10% safety stock pre-emptively to protect against the realistic scenario "
            "and begin alternative supplier qualification now to protect against the pessimistic."
        ),
        "academic_basis": "Lempert, R., Popper, S., & Bankes, S. (2003). Shaping the Next One Hundred Years. RAND Corporation.",
        "best_for_industries": ["construction", "manufacturing", "it"],
        "best_for_experience": ["junior", "mid", "senior"],
    },
}


class FrameworkRecommender:
    """
    Dynamically recommends decision frameworks based on user context.

    Integrates both thesis frameworks (knowledge_base.py) and emerging
    methodologies, ordered by contextual relevance.
    """

    def recommend(self, ctx: "ProjectContext") -> list:
        """
        Return a context-specific, ordered list of framework recommendations.

        Each framework dict includes: name, description, when_to_apply, example,
        academic_basis, context_note, tier.
        """
        selected = []

        # ── Tier 1: Core frameworks (always applicable) ───────────────────────
        selected.append({
            "name": "Safety Premium",
            "tier": "Core",
            **DECISION_FRAMEWORKS["safety_premium"],
            "academic_basis": "PMI PMBOK 7th Edition (2021) + Thesis primary research (93% of experienced PMs endorse)",
            "context_note": (
                "Universally applicable — invest upfront to avoid catastrophic stoppages later. "
                "For your profile: the earlier you apply Safety Premium thinking, the larger the ROI."
            ),
        })

        selected.append({
            "name": "Two-Way Team Model",
            "tier": "Core",
            **DECISION_FRAMEWORKS["two_way_team_model"],
            "academic_basis": "IPMA ICB v4.0 (2015) + Thesis research (cross-experience perspective pairing)",
            "context_note": self._two_way_context_note(ctx),
        })

        # ── Tier 2: Context-specific thesis frameworks ────────────────────────
        if ctx.industry in ("construction", "manufacturing") or ctx.time_pressure == "high":
            selected.append({
                "name": "Somatic Verification",
                "tier": "Context-Specific",
                **DECISION_FRAMEWORKS["somatic_verification"],
                "academic_basis": "Thesis research findings + Weick & Sutcliffe (2007) — HRO preoccupation with failure",
                "context_note": (
                    "High time pressure makes this especially critical — digital reports lag physical reality by days."
                    if ctx.time_pressure == "high"
                    else f"Physical verification is irreplaceable in {ctx.industry} — digital models cannot capture all site conditions."
                ),
            })

        if ctx.experience_level == "senior" or ctx.decision_style == "formal_tools":
            selected.append({
                "name": "Bureaucratic Shield",
                "tier": "Context-Specific",
                **DECISION_FRAMEWORKS["bureaucratic_shield"],
                "academic_basis": "ISO 31000:2018 + Thesis findings (formal documentation as legal protection)",
                "context_note": (
                    "For senior PMs: your decisions carry liability. Formal documentation is both "
                    "your legal shield and your accountability mechanism."
                    if ctx.experience_level == "senior"
                    else "Formal-tool users: amplify the value of your tools by ensuring all outputs serve as auditable documentation."
                ),
            })

        if ctx.industry in ("manufacturing", "it"):
            selected.append({
                "name": "Truth-Link Technology",
                "tier": "Context-Specific",
                **DECISION_FRAMEWORKS["truth_link_technology"],
                "academic_basis": "McKinsey Industry 4.0 Report 2024 + Thesis research (IoT monitoring reduces downtime 40%)",
                "context_note": (
                    "IoT monitoring in manufacturing reduces quality defect detection time by 3×. "
                    "Real-time data replaces lagging status reports."
                    if ctx.industry == "manufacturing"
                    else "Automated monitoring is essential for IT projects — manual status reports are inherently unreliable."
                ),
            })

        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            selected.append({
                "name": "Reverse Training",
                "tier": "Cross-Cultural",
                **DECISION_FRAMEWORKS["reverse_training"],
                "academic_basis": "Hofstede et al. (2010) + GLOBE Study (2004) + Thesis cross-cultural primary research",
                "context_note": (
                    "Process Guardian: deliberately learn from Resource Navigator improvisation styles "
                    "to handle novel or tool-failure situations where formal frameworks cannot guide you."
                    if ctx.cultural_region == "process_guardian"
                    else "Resource Navigator: learn Process Guardian documentation discipline to build audit resilience and regulatory protection."
                ),
            })

        # ── Tier 3: Emerging / extended frameworks ────────────────────────────
        # Pre-Mortem: universally valuable, especially for mid/senior
        ef = EXTENDED_FRAMEWORKS["pre_mortem_analysis"]
        selected.append({
            "name": ef["name"],
            "tier": "Advanced",
            "description": ef["description"],
            "when_to_apply": ef["when_to_apply"],
            "example": ef["example"],
            "academic_basis": ef["academic_basis"],
            "context_note": (
                "Especially powerful at your experience level — overcomes the optimism bias "
                "that grows stronger with seniority."
                if ctx.experience_level in ("mid", "senior")
                else "Excellent for junior PMs: creates a safe space to voice risks without fear of appearing negative."
            ),
        })

        # 3-Scenario Planning: always valuable
        ef = EXTENDED_FRAMEWORKS["scenario_planning_3x"]
        selected.append({
            "name": ef["name"],
            "tier": "Analytical",
            "description": ef["description"],
            "when_to_apply": ef["when_to_apply"],
            "example": ef["example"],
            "academic_basis": ef["academic_basis"],
            "context_note": (
                f"Replace single-point risk estimates with 3-scenario models — "
                f"especially critical for {ctx.industry} where uncertainty is structurally high in the first 20%."
            ),
        })

        # Black Swan: for senior experience or high-pressure contexts
        if ctx.experience_level == "senior" or ctx.time_pressure == "high":
            ef = EXTENDED_FRAMEWORKS["black_swan_analysis"]
            selected.append({
                "name": ef["name"],
                "tier": "Strategic",
                "description": ef["description"],
                "when_to_apply": ef["when_to_apply"],
                "example": ef["example"],
                "academic_basis": ef["academic_basis"],
                "context_note": (
                    "Your experience level makes you capable of anticipating tail risks others miss. "
                    "Build anti-fragility — not just resilience."
                    if ctx.experience_level == "senior"
                    else "High time pressure is itself a risk amplifier for tail events. Build robustness before the pressure peaks."
                ),
            })

        # Bayesian: for senior PMs in construction/manufacturing
        if ctx.experience_level == "senior" and ctx.industry in ("construction", "manufacturing"):
            ef = EXTENDED_FRAMEWORKS["bayesian_risk_updating"]
            selected.append({
                "name": ef["name"],
                "tier": "Advanced",
                "description": ef["description"],
                "when_to_apply": ef["when_to_apply"],
                "example": ef["example"],
                "academic_basis": ef["academic_basis"],
                "context_note": (
                    "Advanced technique for experienced PMs: continuously update your risk model "
                    "as field data arrives — live risk quantification, not a one-shot assessment."
                ),
            })

        # Lean Risk Buffers: for high time pressure
        if ctx.time_pressure == "high":
            ef = EXTENDED_FRAMEWORKS["lean_risk_buffers"]
            selected.append({
                "name": ef["name"],
                "tier": "Efficiency",
                "description": ef["description"],
                "when_to_apply": ef["when_to_apply"],
                "example": ef["example"],
                "academic_basis": ef["academic_basis"],
                "context_note": (
                    "High time pressure demands lean allocation: concentrate your risk budget "
                    "precisely on highest-impact risks; eliminate buffers everywhere else."
                ),
            })

        return selected

    def _two_way_context_note(self, ctx: "ProjectContext") -> str:
        if ctx.experience_level == "junior":
            return (
                "As a junior PM: actively seek pairing with a senior for every major risk decision. "
                "Your micro-check capability is invaluable — use it to validate senior intuitions."
            )
        if ctx.experience_level == "senior":
            return (
                "As a senior PM: mandate junior Micro-Check reviews of your risk register before finalising. "
                "Their technical vigilance catches what experience-based pattern-matching misses."
            )
        return (
            "Bridge both perspectives: bring junior technical vigilance and senior strategic "
            "awareness to every risk decision. Neither alone is sufficient."
        )
