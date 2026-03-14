"""
Core risk assessment agent logic.

The agent conducts a structured interview based on the thesis questionnaire,
analyses the responses using the thesis knowledge base, and produces a tailored
risk assessment report with prioritised recommendations.
"""
from __future__ import annotations

from typing import List

from agent.context_analyzer import ContextAnalyzer
from agent.consultant_report import ConsultantReporter, _get_academic_source, _get_cross_industry_insight
from agent.framework_recommender import FrameworkRecommender
from agent.knowledge_base import (
    CULTURAL_ARCHETYPES,
    DECISION_FRAMEWORKS,
    EXPERIENCE_GUIDANCE,
    INDUSTRY_RISKS,
    REALITY_CHECK_FRAMEWORK,
    get_risk_level,
)
from agent.models import AssessmentReport, ProjectContext, RiskItem

# ── Experience thresholds ─────────────────────────────────────────────────────
_JUNIOR_MAX_YEARS = 3
_MID_MAX_YEARS = 10

# ── Cultural region mapping by country keywords ───────────────────────────────
_PROCESS_GUARDIAN_KEYWORDS = {
    "germany", "german", "austria", "switzerland", "netherlands",
    "europe", "european", "western europe", "scandinavia",
}
_RESOURCE_NAVIGATOR_KEYWORDS = {
    "india", "indian", "asia", "southeast asia", "brazil",
    "middle east", "africa", "latin america",
}


def _map_cultural_archetype(region_text: str) -> str:
    text_lower = region_text.lower()
    if any(k in text_lower for k in _PROCESS_GUARDIAN_KEYWORDS):
        return "process_guardian"
    if any(k in text_lower for k in _RESOURCE_NAVIGATOR_KEYWORDS):
        return "resource_navigator"
    return "mixed"


def _classify_experience(years: int) -> str:
    if years <= _JUNIOR_MAX_YEARS:
        return "junior"
    if years <= _MID_MAX_YEARS:
        return "mid"
    return "senior"


class RiskAssessmentAgent:
    """
    Thesis-derived project risk assessment agent.

    Usage (non-interactive / programmatic):
        agent = RiskAssessmentAgent()
        ctx = agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="Germany",
            top_risks=["Weather delays", "Permit issues", "Subcontractor quality"],
            risk_locus="external",
            decision_style="balance",
            time_pressure="medium",
        )
        report = agent.generate_report(ctx)

    Usage (interactive CLI):
        agent = RiskAssessmentAgent()
        report = agent.run_interactive_session()
    """

    # ── Public API ────────────────────────────────────────────────────────────

    def build_context(
        self,
        industry: str,
        years_experience: int,
        projects_managed: int,
        cultural_region: str = "",
        top_risks: List[str] | None = None,
        risk_locus: str = "mixed",
        decision_style: str = "balance",
        time_pressure: str = "medium",
    ) -> ProjectContext:
        """Build a :class:`ProjectContext` from structured inputs."""
        ctx = ProjectContext(
            industry=industry.lower().strip(),
            years_experience=years_experience,
            projects_managed=projects_managed,
            experience_level=_classify_experience(years_experience),
            cultural_region=_map_cultural_archetype(cultural_region),
            top_risks=top_risks or [],
            risk_locus=risk_locus,
            decision_style=decision_style,
            time_pressure=time_pressure,
        )
        return ctx

    def generate_report(self, ctx: ProjectContext) -> AssessmentReport:
        """Produce a full :class:`AssessmentReport` for the given context."""
        industry_data = INDUSTRY_RISKS.get(
            ctx.industry, INDUSTRY_RISKS["construction"]
        )
        exp_data = EXPERIENCE_GUIDANCE.get(ctx.experience_level, EXPERIENCE_GUIDANCE["mid"])

        # ── Phase 1: Personalisation modules ─────────────────────────────────
        analyzer = ContextAnalyzer()
        persona = analyzer.get_persona_profile(ctx)
        benchmarks = analyzer.get_benchmarks(ctx)

        # Build risk register with enrichment
        risk_register = self._build_risk_register(ctx, industry_data, persona, benchmarks)

        # Use FrameworkRecommender for enriched framework selection
        recommender = FrameworkRecommender()
        frameworks_with_rationale = recommender.recommend_frameworks(ctx, risk_register)

        # Build legacy framework list for backward compatibility
        frameworks = self._select_frameworks(ctx)

        # Generate consultant narrative
        reporter = ConsultantReporter()
        narrative = reporter.generate_narrative(
            ctx, risk_register, persona, frameworks_with_rationale, benchmarks
        )

        summary = self._build_summary(ctx, risk_register, frameworks)

        return AssessmentReport(
            context=ctx,
            industry_risks=industry_data,
            experience_guidance=exp_data,
            framework_recommendations=frameworks,
            reality_check_plan=REALITY_CHECK_FRAMEWORK,
            risk_register=risk_register,
            summary=summary,
            persona_profile=persona,
            benchmarks=benchmarks,
            frameworks_with_rationale=frameworks_with_rationale,
            consultant_narrative=narrative,
        )

    def run_interactive_session(self) -> AssessmentReport:
        """Run a full conversational interview in the terminal and return the report."""
        self._print_banner()
        ctx = self._conduct_interview()
        report = self.generate_report(ctx)
        self._print_report(report)
        return report

    # ── Interview helpers ─────────────────────────────────────────────────────

    def _conduct_interview(self) -> ProjectContext:
        print("\n" + "─" * 60)
        print("SECTION 1 — Background")
        print("─" * 60)

        industry = self._ask_choice(
            "Which industry are you primarily working in?",
            ["Construction", "Manufacturing", "IT / Software", "Other"],
        )
        industry_key = {
            "Construction": "construction",
            "Manufacturing": "manufacturing",
            "IT / Software": "it",
            "Other": "construction",  # fallback to most common
        }[industry]

        years_raw = self._ask_int(
            "How many years have you worked as a project manager?", min_val=0, max_val=60
        )
        projects_raw = self._ask_int(
            "Roughly how many projects have you managed from start to finish?", min_val=0, max_val=500
        )
        region = self._ask_text(
            "What is your primary work region / country? (e.g., Germany, India, USA)"
        )

        print("\n" + "─" * 60)
        print("SECTION 2 — Early-Stage Risk Focus")
        print("─" * 60)

        print("\nWhen you start a new project, what are the first 3 risks that come to mind?")
        risks = []
        for i in range(1, 4):
            r = self._ask_text(f"  Risk {i}")
            if r:
                risks.append(r)

        locus = self._ask_choice(
            "Are these risks mostly:",
            [
                "Inside the project (directly controllable)",
                "Outside the project (uncontrollable: regulations, market, client)",
                "A mix of both",
            ],
        )
        locus_key = {
            "Inside the project (directly controllable)": "internal",
            "Outside the project (uncontrollable: regulations, market, client)": "external",
            "A mix of both": "mixed",
        }[locus]

        print("\n" + "─" * 60)
        print("SECTION 3 — Intuition vs. Tools")
        print("─" * 60)

        decision_style = self._ask_choice(
            "When deciding which risks to take seriously, you mainly rely on:",
            [
                "Mostly experience and intuition",
                "A balance of intuition and formal tools",
                "Mostly formal tools and methods",
            ],
        )
        style_key = {
            "Mostly experience and intuition": "intuition",
            "A balance of intuition and formal tools": "balance",
            "Mostly formal tools and methods": "formal_tools",
        }[decision_style]

        print("\n" + "─" * 60)
        print("SECTION 4 — Time and Management Pressure")
        print("─" * 60)

        pressure = self._ask_choice(
            "What is the current time pressure at the start of this project?",
            ["Low — plenty of planning time", "Medium — normal schedule", "High — management is pushing to start quickly"],
        )
        pressure_key = {
            "Low — plenty of planning time": "low",
            "Medium — normal schedule": "medium",
            "High — management is pushing to start quickly": "high",
        }[pressure]

        ctx = self.build_context(
            industry=industry_key,
            years_experience=years_raw,
            projects_managed=projects_raw,
            cultural_region=region,
            top_risks=risks,
            risk_locus=locus_key,
            decision_style=style_key,
            time_pressure=pressure_key,
        )
        return ctx

    # ── Report generation helpers ─────────────────────────────────────────────

    def _select_frameworks(self, ctx: ProjectContext) -> List[dict]:
        """Choose the most relevant decision frameworks for this context."""
        selected = []

        # Safety Premium is always relevant
        selected.append({"name": "Safety Premium", **DECISION_FRAMEWORKS["safety_premium"]})

        # Two-Way Team Model — always relevant
        selected.append({"name": "Two-Way Team Model", **DECISION_FRAMEWORKS["two_way_team_model"]})

        # Somatic Verification — for construction/manufacturing or high time pressure
        if ctx.industry in ("construction", "manufacturing") or ctx.time_pressure == "high":
            selected.append({"name": "Somatic Verification", **DECISION_FRAMEWORKS["somatic_verification"]})

        # Bureaucratic Shield — for senior PMs or formal-tool users
        if ctx.experience_level == "senior" or ctx.decision_style == "formal_tools":
            selected.append({"name": "Bureaucratic Shield", **DECISION_FRAMEWORKS["bureaucratic_shield"]})

        # Truth-Link Technology — for manufacturing or IT
        if ctx.industry in ("manufacturing", "it"):
            selected.append({"name": "Truth-Link Technology", **DECISION_FRAMEWORKS["truth_link_technology"]})

        # Reverse Training — for cross-cultural teams or identified cultural archetype
        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            selected.append({"name": "Reverse Training", **DECISION_FRAMEWORKS["reverse_training"]})

        return selected

    def _build_risk_register(
        self, ctx: ProjectContext, industry_data: dict,
        persona: dict | None = None, benchmarks: dict | None = None
    ) -> List[RiskItem]:
        """Create an initial risk register combining user-provided and knowledge-base risks."""
        register: List[RiskItem] = []
        persona = persona or {}
        benchmarks = benchmarks or {}

        # Determine persona blind spots list for enrichment
        persona_blind_spots: List[str] = persona.get("blind_spots", [])
        exp_blind_spot: str = persona.get("experience_blind_spot", "")

        def _enrich(item: RiskItem, index: int) -> RiskItem:
            """Enrich a RiskItem with benchmark, blind_spot, cross-industry, and academic source."""
            # Benchmark: try to match by keyword
            default_bm = benchmarks.get("default", {})
            desc_lower = item.description.lower()
            matched_bm = default_bm
            for key, bm in benchmarks.items():
                if key.startswith("_"):
                    continue
                if key.replace("_", " ") in desc_lower or any(
                    part in desc_lower for part in key.split("_")
                ):
                    matched_bm = bm
                    break
            item.benchmark = matched_bm

            # Blind spot: rotate through persona blind spots for variety
            all_blind_spots = list(persona_blind_spots)
            if exp_blind_spot:
                all_blind_spots = [exp_blind_spot] + all_blind_spots
            if all_blind_spots:
                item.blind_spot = all_blind_spots[index % len(all_blind_spots)]

            # Cross-industry insight
            item.cross_industry_insight = _get_cross_industry_insight(item.description)
            item.novel_mitigation = item.cross_industry_insight

            # Academic source
            item.academic_source = _get_academic_source(item.description)

            # Confidence: high-pressure reduces confidence slightly (more uncertainty)
            base_conf = 0.90 if ctx.time_pressure == "low" else (0.85 if ctx.time_pressure == "medium" else 0.80)
            # Adjust by experience: senior PMs have higher confidence in assessments
            if ctx.experience_level == "senior":
                base_conf = min(1.0, base_conf + 0.05)
            elif ctx.experience_level == "junior":
                base_conf = max(0.60, base_conf - 0.05)
            item.confidence = round(base_conf, 2)

            return item

        item_index = 0

        # Add user-provided top risks
        for risk_desc in ctx.top_risks:
            # Heuristic: classify as external if locus says so
            category = ctx.risk_locus if ctx.risk_locus != "mixed" else "external"
            # Default probability/impact — moderate since we don't have details
            item = RiskItem(
                description=risk_desc,
                category=category,
                probability="medium",
                impact="high",
                detectability="late",
            )
            _enrich(item, item_index)
            register.append(item)
            item_index += 1

        # Add top 3 industry-specific external risks
        for risk_desc in industry_data.get("primary_external", [])[:3]:
            item = RiskItem(
                description=risk_desc,
                category="external",
                probability="medium",
                impact="high",
                detectability="late",
            )
            _enrich(item, item_index)
            register.append(item)
            item_index += 1

        # Add top 2 industry-specific internal risks
        for risk_desc in industry_data.get("primary_internal", [])[:2]:
            item = RiskItem(
                description=risk_desc,
                category="internal",
                probability="medium",
                impact="medium",
                detectability="early",
            )
            _enrich(item, item_index)
            register.append(item)
            item_index += 1

        # Escalate probability/impact under high time pressure
        if ctx.time_pressure == "high":
            for item in register:
                if item.probability == "low":
                    item.probability = "medium"
                if item.impact == "low":
                    item.impact = "medium"
                # Recalculate score
                result = get_risk_level(item.probability, item.impact, item.detectability)
                item.score = result["score"]
                item.level = result["level"]
                item.action = result["action"]

        # Sort by score descending
        register.sort(key=lambda r: r.score, reverse=True)
        return register

    def _build_summary(
        self, ctx: ProjectContext, risk_register: List[RiskItem], frameworks: List[dict]
    ) -> str:
        critical = [r for r in risk_register if r.level == "Critical"]
        high = [r for r in risk_register if r.level == "High"]
        lines = [
            f"Industry: {ctx.industry.title()}  |  "
            f"Experience: {ctx.experience_level.title()} ({ctx.years_experience} yrs)  |  "
            f"Time Pressure: {ctx.time_pressure.title()}",
            "",
            f"Risk register contains {len(risk_register)} items: "
            f"{len(critical)} Critical, {len(high)} High, "
            f"{len(risk_register) - len(critical) - len(high)} Medium/Low.",
            "",
        ]
        if critical:
            lines.append("⚠  STOP-AND-FIX items before proceeding:")
            for r in critical:
                lines.append(f"   • {r.description}")
            lines.append("")
        arch = CULTURAL_ARCHETYPES.get(ctx.cultural_region)
        if arch:
            lines.append(f"Cultural archetype: {ctx.cultural_region.replace('_', ' ').title()}")
            lines.append(f"Blind spots to address: {'; '.join(arch['blind_spots'])}")
            lines.append("")
        lines.append(
            f"Top recommended framework: {frameworks[0]['name']} — {frameworks[0]['description'][:120]}..."
        )
        return "\n".join(lines)

    # ── Printing helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _print_banner() -> None:
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║       PROJECT RISK ASSESSMENT AGENT                              ║
║       Based on thesis: "Understanding Risk Awareness and         ║
║       Decision Making in Early-Stage Project Planning"           ║
║       by Devarshi Kansara — HDBW, 2026                          ║
╚══════════════════════════════════════════════════════════════════╝

This agent will guide you through a structured risk assessment for
the critical first 20% of your project lifecycle.
Estimated time: 3–5 minutes.
"""
        print(banner)

    @staticmethod
    def _print_report(report: AssessmentReport) -> None:
        ctx = report.context
        print("\n\n" + "═" * 68)
        print("  RISK ASSESSMENT REPORT")
        print("═" * 68)

        print("\n📋 SUMMARY")
        print("─" * 40)
        print(report.summary)

        print("\n🏗  INDUSTRY CONTEXT  —", ctx.industry.upper())
        print("─" * 40)
        industry_data = report.industry_risks
        print("Primary external risks to monitor in first 20%:")
        for r in industry_data.get("primary_external", []):
            print(f"  • {r}")
        print("\nPrimary internal risks to monitor in first 20%:")
        for r in industry_data.get("primary_internal", []):
            print(f"  • {r}")
        print("\nBlind spots for professionals from OTHER industries entering yours:")
        for r in industry_data.get("blind_spots_for_outsiders", []):
            print(f"  ⚡ {r}")

        print("\n👤 EXPERIENCE-LEVEL GUIDANCE  —", ctx.experience_level.upper())
        print("─" * 40)
        exp = report.experience_guidance
        print("Your strengths:")
        for s in exp.get("strengths", []):
            print(f"  ✅ {s}")
        print("\nDevelopment areas:")
        for d in exp.get("development_areas", []):
            print(f"  📌 {d}")
        print("\nRecommended actions for the first 20%:")
        for a in exp.get("recommended_actions", []):
            print(f"  → {a}")

        print("\n📊 RISK REGISTER  (sorted by severity)")
        print("─" * 40)
        for i, risk in enumerate(report.risk_register, 1):
            icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(risk.level, "⚪")
            print(f"  {i:2}. [{risk.level:8s}] {icon} Score={risk.score:3d}  {risk.description}")
            print(f"      Category: {risk.category}  |  P={risk.probability}, I={risk.impact}, D={risk.detectability}")
            print(f"      Action: {risk.action}")

        print("\n🧰 RECOMMENDED DECISION FRAMEWORKS")
        print("─" * 40)
        for fw in report.framework_recommendations:
            print(f"\n  ▸ {fw['name']}")
            print(f"    {fw['description'][:160]}")
            print(f"    When: {fw['when_to_apply']}")
            print(f"    Example: {fw['example']}")

        print("\n📅 20% REALITY CHECK MILESTONE")
        print("─" * 40)
        rc = report.reality_check_plan
        print(rc["description"])
        print("\nAgenda items for your Reality Check workshop:")
        for item in rc.get("agenda_items", []):
            print(f"  ☐ {item}")
        print("\nExpected output:", rc.get("output", ""))

        industry_data2 = report.industry_risks
        print("\n🚀 FIRST 20% ACTION CHECKLIST  —", ctx.industry.upper())
        print("─" * 40)
        for action in industry_data2.get("first_20_percent_actions", []):
            print(f"  ☐ {action}")

        arch = CULTURAL_ARCHETYPES.get(ctx.cultural_region)
        if arch:
            print(f"\n🌍 CULTURAL ARCHETYPE: {ctx.cultural_region.replace('_', ' ').upper()}")
            print("─" * 40)
            print("Key characteristics:")
            for c in arch.get("characteristics", []):
                print(f"  • {c}")
            print("\nDevelopment recommendation:")
            print(f"  → {arch.get('recommended_development', '')}")

        print("\n" + "═" * 68)
        print("  Report generated by the Project Risk Assessment Agent")
        print("  Thesis: 'Understanding Risk Awareness and Decision Making in")
        print("  Early-Stage Project Planning' — Devarshi Kansara, HDBW 2026")
        print("═" * 68 + "\n")

    # ── Input helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _ask_text(prompt: str) -> str:
        return input(f"\n{prompt}: ").strip()

    @staticmethod
    def _ask_int(prompt: str, min_val: int = 0, max_val: int = 100) -> int:
        while True:
            raw = input(f"\n{prompt} [{min_val}–{max_val}]: ").strip()
            try:
                val = int(raw)
                if min_val <= val <= max_val:
                    return val
                print(f"  Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("  Please enter a valid integer.")

    @staticmethod
    def _ask_choice(prompt: str, choices: List[str]) -> str:
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        while True:
            raw = input("Enter number: ").strip()
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                print(f"  Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("  Please enter a valid number.")
