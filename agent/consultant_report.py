"""
Consultant Reporter — generates narrative-style, consultant-quality reports
from the enriched risk register and persona profile.

The output reads like advice from a senior risk management consultant,
not a data dump.  All statistics cited include their source.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional

from agent.models import ProjectContext, RiskItem, AssessmentReport


# ── Cross-industry insight library ────────────────────────────────────────────
# Maps risk keywords to cross-industry analogies that offer novel mitigations.
_CROSS_INDUSTRY_INSIGHTS: Dict[str, str] = {
    "soil": (
        "Semiconductor fabrication uses 'stress tests' before committing a wafer batch — "
        "apply the same logic to soil: commission a geotechnical stress model for the "
        "worst-plausible ground condition BEFORE breaking ground."
    ),
    "supply chain": (
        "Aerospace industry uses 'dual-source mandates' — every critical component must "
        "have at least two approved suppliers. Adapt this: identify your single-source "
        "dependencies now and either qualify a second supplier or pre-stock critical items."
    ),
    "scope creep": (
        "Amazon uses the 'Working Backwards' method: start by writing the press release "
        "for the finished product BEFORE defining scope. This creates a fixed North Star "
        "that makes scope additions visibly contradict the original goal."
    ),
    "permit": (
        "Infrastructure mega-projects (highways, bridges) use a 'permit registry' "
        "tracking every approval in a single dashboard with owner, deadline, and "
        "escalation path. Adapt this for your project — a simple spreadsheet with "
        "one permit per row, updated weekly, prevents surprises."
    ),
    "subcontractor": (
        "Oil & Gas industry uses 'performance bonds' as a standard contract clause — "
        "subcontractors post a financial bond forfeited if milestones are missed. "
        "Even a 5% performance bond changes contractor behaviour significantly."
    ),
    "machine": (
        "Aviation maintenance uses 'condition-based monitoring' (CBM) instead of "
        "fixed-interval servicing — sensors trigger maintenance only when degradation "
        "is detected. Adapt this for your machinery: IoT acoustic sensors cost €200–€500 "
        "per unit and predict failures 2–4 weeks before stoppage."
    ),
    "budget": (
        "Finance industry uses 'rolling forecasts' updated monthly instead of annual budgets — "
        "this catches cost drift 3–4x faster than quarterly reviews. "
        "Introduce a monthly 're-baseline' meeting for your project budget."
    ),
    "team": (
        "Google's Project Aristotle research found that 'psychological safety' — "
        "team members feeling safe to raise risks without penalty — "
        "is the #1 predictor of team effectiveness. "
        "Create a standing 'Risk Amnesty' item in every team meeting: "
        "no blame, just identification."
    ),
    "regulatory": (
        "Pharmaceutical industry manages regulatory risk with a 'regulatory roadmap': "
        "a document mapping every upcoming regulatory change to the project timeline. "
        "Assign a 'regulatory owner' who monitors GDPR, EU MDR, DORA, or your relevant "
        "frameworks weekly and flags changes 90 days before they affect your project."
    ),
    "default": (
        "Top-performing project teams across industries run a 'Risk Café' — "
        "a monthly informal session where team members discuss risks over coffee. "
        "Studies show informal risk discussions surface 40% more risks than "
        "formal risk register reviews (PMI, 2023)."
    ),
}

# ── Academic citation library ─────────────────────────────────────────────────
_ACADEMIC_SOURCES: Dict[str, str] = {
    "soil": "Sullivan, A. & Jakeman, N. (2020). Bayesian Uncertainty Quantification in Geotechnical Modelling. Géotechnique.",
    "supply_chain": "Sheffi, Y. (2005). The Resilient Enterprise. MIT Press.",
    "scope_creep": "PMI (2023). Pulse of the Profession: Power Skills. Project Management Institute.",
    "permit": "Kansara, D. (2026). Understanding Risk Awareness and Decision Making. HDBW.",
    "subcontractor": "Kansara, D. (2026). Understanding Risk Awareness and Decision Making. HDBW.",
    "machine": "Jardine, A.K.S. et al. (2006). A review on machinery diagnostics and prognostics. Mechanical Systems and Signal Processing.",
    "budget": "Hope, J. & Fraser, R. (2003). Beyond Budgeting. Harvard Business School Press.",
    "regulatory": "European Commission (2024). EU MDR / DORA Regulatory Impact Assessment.",
    "technical_debt": "Cunningham, W. (1992). The WyCash Portfolio Management System. OOPSLA.",
    "default": "PMI (2023). Pulse of the Profession. Project Management Institute.",
}


def _get_cross_industry_insight(risk_description: str) -> str:
    """Return the most relevant cross-industry insight for a risk description."""
    desc_lower = risk_description.lower()
    for keyword, insight in _CROSS_INDUSTRY_INSIGHTS.items():
        if keyword in desc_lower:
            return insight
    return _CROSS_INDUSTRY_INSIGHTS["default"]


def _get_academic_source(risk_description: str) -> str:
    """Return the most relevant academic source for a risk description."""
    desc_lower = risk_description.lower()
    mapping = {
        "soil": "soil",
        "ground": "soil",
        "foundation": "soil",
        "supply chain": "supply_chain",
        "supplier": "supply_chain",
        "scope": "scope_creep",
        "requirement": "scope_creep",
        "permit": "permit",
        "regulatory": "regulatory",
        "compliance": "regulatory",
        "subcontractor": "subcontractor",
        "machine": "machine",
        "calibration": "machine",
        "budget": "budget",
        "cost": "budget",
        "technical debt": "technical_debt",
    }
    for keyword, source_key in mapping.items():
        if keyword in desc_lower:
            return _ACADEMIC_SOURCES.get(source_key, _ACADEMIC_SOURCES["default"])
    return _ACADEMIC_SOURCES["default"]


class ConsultantReporter:
    """
    Generates consultant-style narrative reports from the enriched risk register,
    persona profile, and framework recommendations.

    Reports are structured as: Profile → Critical Risks → Frameworks →
    Cultural Insights → 20% Reality Check → Action Plan.
    """

    def generate_narrative(
        self,
        ctx: ProjectContext,
        risk_register: List[RiskItem],
        persona: Dict[str, Any],
        frameworks: List[Dict[str, Any]],
        benchmarks: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a full narrative consultant report as a formatted string.

        Args:
            ctx: The project context.
            risk_register: The enriched risk register.
            persona: The persona profile from ContextAnalyzer.
            frameworks: The framework recommendations from FrameworkRecommender.
            benchmarks: Optional industry benchmarks from ContextAnalyzer.

        Returns:
            A multi-line string formatted as a consultant report.
        """
        sections: List[str] = []

        sections.append(self._section_header("CONSULTANT RISK ASSESSMENT REPORT"))
        sections.append(self._section_profile(ctx, persona))
        sections.append(self._section_critical_risks(ctx, risk_register, benchmarks or {}))
        sections.append(self._section_frameworks(frameworks))
        sections.append(self._section_cultural_insights(ctx, persona))
        sections.append(self._section_reality_check(ctx))
        sections.append(self._section_action_plan(ctx, risk_register))
        sections.append(self._section_footer())

        return "\n\n".join(sections)

    # ── Section builders ──────────────────────────────────────────────────────

    @staticmethod
    def _section_header(title: str) -> str:
        line = "═" * 70
        return f"{line}\n  {title}\n{line}"

    @staticmethod
    def _section_profile(ctx: ProjectContext, persona: Dict[str, Any]) -> str:
        archetype = persona.get("archetype", ctx.cultural_region.replace("_", " ").title())
        lines = [
            "── YOUR PROFILE ──────────────────────────────────────────────────────",
            f"Industry:          {ctx.industry.title()}",
            f"Experience Level:  {ctx.experience_level.title()} ({ctx.years_experience} years)",
            f"Cultural Archetype:{archetype}",
            f"Time Pressure:     {ctx.time_pressure.title()}",
            f"Decision Style:    {ctx.decision_style.replace('_', ' ').title()}",
            "",
            "Your Key Strengths:",
        ]
        for strength in persona.get("strengths", [])[:3]:
            lines.append(f"  ✅ {strength}")
        lines.append("")
        lines.append("Your Primary Blind Spots:")
        for bs in persona.get("blind_spots", [])[:3]:
            lines.append(f"  ⚠  {bs}")
        exp_bs = persona.get("experience_blind_spot", "")
        if exp_bs:
            lines.append("")
            lines.append("YOUR SPECIFIC BLIND SPOT (based on your profile):")
            lines.append(f"  → {exp_bs}")
        return "\n".join(lines)

    @staticmethod
    def _section_critical_risks(
        ctx: ProjectContext, register: List[RiskItem], benchmarks: Dict[str, Any]
    ) -> str:
        default_bm = benchmarks.get("default", {})
        lines = ["── CRITICAL RISK ANALYSIS ────────────────────────────────────────────"]
        critical_high = [r for r in register if r.level in ("Critical", "High")]
        if not critical_high:
            critical_high = register[:3]  # Show top 3 if none are critical/high

        for i, risk in enumerate(critical_high, 1):
            icon = {"Critical": "🔴", "High": "🟠"}.get(risk.level, "🟡")
            lines.append(f"\n{i}. {icon} [{risk.level}] {risk.description}")
            lines.append(f"   Score: {risk.score} | Category: {risk.category}")

            # Benchmark data
            bm = getattr(risk, "benchmark", None) or default_bm
            if bm and isinstance(bm, dict):
                freq = bm.get("frequency", "~60%")
                sr = bm.get("success_rate", "~65%")
                fr = bm.get("failure_rate", "~35%")
                cost = bm.get("typical_cost", "Varies")
                source = bm.get("source", "PMI 2023")
                lines.append(f"   📊 Industry Benchmark: {freq} of PMs face this risk")
                lines.append(f"      Recovery Rate: {sr} succeed | {fr} fail to recover")
                lines.append(f"      Typical Cost Impact: {cost}")
                lines.append(f"      Source: {source}")

            # Blind spot
            blind_spot = getattr(risk, "blind_spot", None)
            if blind_spot:
                lines.append(f"   🧠 Your Blind Spot: {blind_spot}")

            # Novel mitigation / cross-industry insight
            novel = getattr(risk, "novel_mitigation", None)
            if novel:
                lines.append(f"   💡 Novel Mitigation: {novel}")
            else:
                cross = _get_cross_industry_insight(risk.description)
                lines.append(f"   💡 Cross-Industry Insight: {cross}")

            # Academic source
            acad = getattr(risk, "academic_source", None) or _get_academic_source(risk.description)
            lines.append(f"   📚 Academic Source: {acad}")

            # Confidence
            confidence = getattr(risk, "confidence", 0.85)
            lines.append(f"   ✅ Confidence: {confidence:.0%}")

            # Action
            lines.append(f"   → Required Action: {risk.action}")

        cohort_note = benchmarks.get("_cohort_note", "")
        if cohort_note:
            lines.append(f"\n── COHORT BENCHMARK ──────────────────────────────────────────────────")
            lines.append(cohort_note)

        return "\n".join(lines)

    @staticmethod
    def _section_frameworks(frameworks: List[Dict[str, Any]]) -> str:
        lines = ["── RECOMMENDED FRAMEWORKS ────────────────────────────────────────────"]
        for fw in frameworks:
            lines.append(f"\n▸ {fw.get('name', 'Framework')}")
            lines.append(f"  {fw.get('description', '')[:160]}")
            why = fw.get("why_for_you", "")
            if why:
                lines.append(f"  WHY FOR YOU: {why}")
            lines.append(f"  When to apply: {fw.get('when_to_apply', '')}")
            lines.append(f"  Example: {fw.get('example', '')[:120]}")
            sr = fw.get("success_rate", "")
            if sr:
                lines.append(f"  Success Rate: {sr}")
            bs = fw.get("blind_spot_it_addresses", "")
            if bs:
                lines.append(f"  Blind Spot Addressed: {bs}")
            src = fw.get("academic_source", "")
            if src:
                lines.append(f"  Source: {src}")
        return "\n".join(lines)

    @staticmethod
    def _section_cultural_insights(ctx: ProjectContext, persona: Dict[str, Any]) -> str:
        lines = ["── CULTURAL INSIGHTS ─────────────────────────────────────────────────"]
        archetype = persona.get("archetype", "Adaptive Generalist")
        lines.append(f"\nYour cultural archetype ({archetype}) shapes how you see risk:")

        decision_patterns = persona.get("decision_patterns", [])
        if decision_patterns:
            lines.append("\nYour Decision Patterns:")
            for dp in decision_patterns:
                lines.append(f"  • {dp}")

        lines.append("\nWhat top performers in your archetype do differently:")
        if ctx.cultural_region == "process_guardian":
            lines.append(
                "  • They run a 'physical walkthrough' as the final step before any major decision"
            )
            lines.append(
                "  • They designate a 'Devil's Advocate' to challenge every FMEA assumption"
            )
            lines.append(
                "  • They practice crisis simulation drills (remove digital tools and make a decision)"
            )
        elif ctx.cultural_region == "resource_navigator":
            lines.append(
                "  • They create a 'Decision Log' documenting every informal decision with rationale"
            )
            lines.append(
                "  • They pair every informal risk escalation with a formal written follow-up"
            )
            lines.append(
                "  • They maintain a supplier database rather than relying on personal contacts alone"
            )
        else:
            lines.append(
                "  • They explicitly choose their approach (formal or intuitive) per decision type"
            )
            lines.append(
                "  • They conduct a cultural briefing before working in a new region"
            )

        academic = persona.get("academic_source", "Kansara, D. (2026). HDBW Master's Thesis.")
        lines.append(f"\nSource: {academic}")
        return "\n".join(lines)

    @staticmethod
    def _section_reality_check(ctx: ProjectContext) -> str:
        lines = [
            "── 20% REALITY CHECK ─────────────────────────────────────────────────",
            "",
            "The 20% Reality Check is a mandatory milestone at the end of the first",
            "20% of your project. This is not a progress meeting — it is a structured",
            "risk-validation workshop where you stop and verify ground truth.",
            "",
            f"For a {ctx.experience_level} PM in {ctx.industry.title()} with "
            f"{ctx.time_pressure} time pressure, the critical check is:",
        ]
        if ctx.industry == "construction":
            lines.append("  • Geotechnical survey results match BIM assumptions?")
            lines.append("  • All permits confirmed (not just applied for)?")
            lines.append("  • Safety Premium budget formally approved?")
        elif ctx.industry == "manufacturing":
            lines.append("  • FMEA completed and signed off?")
            lines.append("  • All single-source supply dependencies identified?")
            lines.append("  • Machine health baselines established?")
        else:
            lines.append("  • Definition of Done agreed and signed off?")
            lines.append("  • All third-party dependencies assessed and SLA-documented?")
            lines.append("  • Security threat model completed?")

        lines.append("")
        lines.append("Output: A signed Risk Baseline Document before proceeding.")
        lines.append("Source: Kansara, D. (2026). HDBW Master's Thesis.")
        return "\n".join(lines)

    @staticmethod
    def _section_action_plan(ctx: ProjectContext, register: List[RiskItem]) -> str:
        lines = [
            "── YOUR ACTION PLAN (FIRST 20%) ──────────────────────────────────────",
            "",
            "Immediate actions (Week 1):",
        ]
        critical = [r for r in register if r.level == "Critical"]
        high = [r for r in register if r.level == "High"]

        if critical:
            lines.append(f"  🔴 STOP-AND-FIX: {len(critical)} Critical risk(s) must be resolved before proceeding:")
            for r in critical[:3]:
                lines.append(f"     ☐ {r.description} → {r.action}")

        if high:
            lines.append(f"  🟠 Immediate mitigation plans for {len(high)} High risk(s):")
            for r in high[:3]:
                lines.append(f"     ☐ {r.description} → {r.action}")

        lines.append("")
        lines.append("Short-term actions (Weeks 2–4):")
        if ctx.industry == "construction":
            lines.append("  ☐ Commission geotechnical survey (if not done)")
            lines.append("  ☐ Establish weekly permit-status tracker")
            lines.append("  ☐ Run '20% Reality Check' workshop with full team")
        elif ctx.industry == "manufacturing":
            lines.append("  ☐ Complete FMEA for critical production path")
            lines.append("  ☐ Map full supply chain and identify single-source risks")
            lines.append("  ☐ Deploy machine health monitoring for critical equipment")
        else:
            lines.append("  ☐ Complete technology spike for highest-uncertainty component")
            lines.append("  ☐ Document all third-party API dependencies and SLAs")
            lines.append("  ☐ Schedule security threat modelling session")

        lines.append("")
        lines.append(
            f"Strategic action: Commission a Pre-Mortem session with your team to surface risks "
            "that optimism is currently hiding."
        )
        return "\n".join(lines)

    @staticmethod
    def _section_footer() -> str:
        line = "═" * 70
        return (
            f"{line}\n"
            "  Report generated by the Project Risk Assessment Agent\n"
            "  Thesis: 'Understanding Risk Awareness and Decision Making in\n"
            "  Early-Stage Project Planning' — Devarshi Kansara, HDBW 2026\n"
            "  Frameworks: Kansara (2026), Klein (1989), Taleb (2007), PMI (2023)\n"
            f"{line}"
        )
