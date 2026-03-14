"""
Core risk assessment agent logic.

The agent conducts a structured interview based on the thesis questionnaire,
analyses the responses using the thesis knowledge base, and produces a tailored
risk assessment report with prioritised recommendations.

The report is enriched by the ConsultantReportGenerator which adds:
  - Context-driven persona analysis and benchmarks
  - Academic citations and industry research references
  - Cross-industry innovation patterns
  - Black swan / tail-risk warnings
  - Regulatory intelligence data
  - Source attribution and confidence metrics
"""
from __future__ import annotations

from typing import List

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
        frameworks = self._select_frameworks(ctx)
        risk_register = self._build_risk_register(ctx, industry_data)
        summary = self._build_summary(ctx, risk_register, frameworks)

        report = AssessmentReport(
            context=ctx,
            industry_risks=industry_data,
            experience_guidance=exp_data,
            framework_recommendations=frameworks,
            reality_check_plan=REALITY_CHECK_FRAMEWORK,
            risk_register=risk_register,
            summary=summary,
        )

        # Enrich with consultant insights (context analysis, benchmarks, citations, etc.)
        report.consultant_insights = self._generate_consultant_insights(report)

        return report

    def _generate_consultant_insights(self, report: AssessmentReport) -> dict:
        """Generate the consultant insights layer using the new specialist modules."""
        try:
            from agent.consultant_report import ConsultantReportGenerator
            generator = ConsultantReportGenerator(use_live_data=False)
            return generator.generate(report)
        except Exception:
            return {}

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
        self, ctx: ProjectContext, industry_data: dict
    ) -> List[RiskItem]:
        """Create an initial risk register combining user-provided and knowledge-base risks.

        Risk scores are now context-sensitive:
        - Senior PMs see elevated strategic/political risks; junior see elevated operational risks
        - High time pressure escalates all external risks
        - Process Guardian region: elevated regulatory and documentation risks
        - Resource Navigator region: elevated supply/labor and informal-agreement risks
        - IT industry: elevated security risks; Construction: elevated geotechnical risks
        """
        register: List[RiskItem] = []

        # Derive context modifiers
        is_senior = ctx.experience_level == "senior"
        is_junior = ctx.experience_level == "junior"
        is_process_guardian = ctx.cultural_region == "process_guardian"
        is_resource_navigator = ctx.cultural_region == "resource_navigator"
        high_pressure = ctx.time_pressure == "high"
        low_pressure = ctx.time_pressure == "low"

        def _external_detectability() -> str:
            """External risks are harder to detect early under high pressure."""
            if high_pressure:
                return "post_occurrence"
            if low_pressure:
                return "early"
            return "late"

        def _impact_for_external() -> str:
            """Senior PMs face higher political/strategic external risk."""
            if is_senior:
                return "high"
            if high_pressure:
                return "high"
            return "medium"

        def _probability_for_external() -> str:
            """External risk probability increases under pressure and in complex regions."""
            if high_pressure and (is_process_guardian or is_resource_navigator):
                return "high"
            if high_pressure:
                return "medium"
            return "medium"

        def _internal_probability() -> str:
            """Junior PMs face higher internal operational risk due to inexperience."""
            if is_junior:
                return "high"
            if is_senior:
                return "low"
            return "medium"

        def _internal_detectability() -> str:
            """Senior PMs detect internal issues earlier via experience."""
            if is_senior:
                return "early"
            return "late"

        # Add user-provided top risks
        for risk_desc in ctx.top_risks:
            category = ctx.risk_locus if ctx.risk_locus != "mixed" else "external"
            if category == "external":
                prob = _probability_for_external()
                impact = _impact_for_external()
                detectability = _external_detectability()
            else:
                prob = _internal_probability()
                impact = "medium"
                detectability = _internal_detectability()
            item = RiskItem(
                description=risk_desc,
                category=category,
                probability=prob,
                impact=impact,
                detectability=detectability,
            )
            register.append(item)

        # Add industry-specific external risks (context-sensitive P/I/D)
        for risk_desc in industry_data.get("primary_external", [])[:3]:
            risk_lower = risk_desc.lower()
            # Industry-specific severity adjustments
            prob = _probability_for_external()
            impact = _impact_for_external()
            detectability = _external_detectability()

            # Construction: geotechnical and regulatory risks are higher for process guardians
            if ctx.industry == "construction" and is_process_guardian:
                if any(k in risk_lower for k in ("soil", "permit", "regulat", "legal")):
                    impact = "high"
                    detectability = "late"

            # Manufacturing: compliance gaps are critical for formal-tool environments
            if ctx.industry == "manufacturing" and is_process_guardian:
                if any(k in risk_lower for k in ("compliance", "mdr", "fda", "gdpr", "dora", "regulat")):
                    impact = "high"
                    detectability = "late"

            # IT: security risks escalate with time pressure
            if ctx.industry == "it" and high_pressure:
                if any(k in risk_lower for k in ("security", "cyber", "gdpr", "dora", "compliance")):
                    prob = "high"
                    impact = "high"

            # Resource Navigator: supply chain risks are more severe
            if is_resource_navigator:
                if any(k in risk_lower for k in ("supply", "material", "labor", "vendor", "resource")):
                    prob = "high"
                    detectability = "late"

            item = RiskItem(
                description=risk_desc,
                category="external",
                probability=prob,
                impact=impact,
                detectability=detectability,
            )
            register.append(item)

        # Add industry-specific internal risks (context-sensitive P/I/D)
        for risk_desc in industry_data.get("primary_internal", [])[:2]:
            risk_lower = risk_desc.lower()
            prob = _internal_probability()
            detectability = _internal_detectability()
            # Default impact is medium for internal; escalate for critical internal risks
            impact = "medium"

            # Manufacturing: tolerance and calibration errors are critical
            if ctx.industry == "manufacturing":
                if any(k in risk_lower for k in ("calibrat", "tolerance", "defect", "quality", "error")):
                    impact = "high"
                    if is_process_guardian:
                        detectability = "late"  # Over-documentation masks physical reality

            # IT: technical debt cascades under pressure
            if ctx.industry == "it" and high_pressure:
                if any(k in risk_lower for k in ("debt", "error", "bug", "complet", "complexit")):
                    impact = "high"
                    prob = "high"
                    detectability = "post_occurrence"

            # Senior normalises internal issues (their blind spot)
            if is_senior:
                if any(k in risk_lower for k in ("minor", "small", "drift", "calibrat", "error")):
                    prob = "medium"  # Seniors miss these via normalisation bias

            item = RiskItem(
                description=risk_desc,
                category="internal",
                probability=prob,
                impact=impact,
                detectability=detectability,
            )
            register.append(item)

        # Escalate probability/impact under high time pressure (post-individual-scoring)
        if high_pressure:
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
            f"Cultural Region: {ctx.cultural_region.replace('_', ' ').title()}  |  "
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
        ci = report.consultant_insights  # may be empty dict if generation failed

        print("\n\n" + "═" * 68)
        print("  RISK ASSESSMENT REPORT")
        print("═" * 68)

        print("\n📋 SUMMARY")
        print("─" * 40)
        print(report.summary)

        # ── Consultant Persona & Benchmark ────────────────────────────────────
        persona = ci.get("persona", {})
        if persona:
            print(f"\n🎭 YOUR CONSULTANT PROFILE: {persona.get('persona', '')}")
            print("─" * 40)
            print(f"  {persona.get('description', '')}")
            blind_spots = persona.get("risk_blind_spots", [])
            if blind_spots:
                print("\n  ⚠  Your risk blind spots:")
                for bs in blind_spots:
                    print(f"     • {bs}")
            prescription = persona.get("prescription", "")
            if prescription:
                print(f"\n  💊 Prescription: {prescription}")

        # ── Time Pressure Warning ─────────────────────────────────────────────
        tp_insights = ci.get("time_pressure_insights", {})
        if tp_insights:
            print(f"\n⏱  TIME PRESSURE NOTE")
            print("─" * 40)
            print(f"  {tp_insights.get('risk_escalation_note', '')}")
            print(f"  {tp_insights.get('behavioral_warning', '')}")
            print(f"  → {tp_insights.get('counter_strategy', '')}")

        # ── Industry Context ──────────────────────────────────────────────────
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

        # ── Benchmarks ────────────────────────────────────────────────────────
        benchmarks = ci.get("benchmarks", {})
        if benchmarks:
            print("\n📊 INDUSTRY BENCHMARKS (for your industry + region)")
            print("─" * 40)
            for desc, pct in benchmarks.get("common_risks_pct", {}).items():
                print(f"  • {pct}% of PMs in your situation face: {desc}")
            failure_rate = benchmarks.get("failure_recovery_rate")
            if failure_rate:
                print(f"\n  Recovery rate: {failure_rate}% of projects recover successfully from major risks")
            blind_spot = benchmarks.get("blind_spot", "")
            if blind_spot:
                print(f"\n  🔍 Regional Blind Spot: {blind_spot}")
            print(f"\n  Source: {benchmarks.get('source', 'Thesis research + industry reports')}")

        # ── Experience-Level Guidance ─────────────────────────────────────────
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

        # ── Risk Register ─────────────────────────────────────────────────────
        print("\n📊 RISK REGISTER  (sorted by severity)")
        print("─" * 40)
        enriched_risks = ci.get("enriched_risks", [])
        enriched_map = {er["risk"].description: er for er in enriched_risks}
        for i, risk in enumerate(report.risk_register, 1):
            icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(risk.level, "⚪")
            print(f"  {i:2}. [{risk.level:8s}] {icon} Score={risk.score:3d}  {risk.description}")
            print(f"      Category: {risk.category}  |  P={risk.probability}, I={risk.impact}, D={risk.detectability}")
            print(f"      Action: {risk.action}")
            # Show context note if available
            enriched = enriched_map.get(risk.description, {})
            if enriched.get("context_note"):
                print(f"      Context: {enriched['context_note']}")
            # Show top citation
            citations = enriched.get("citations", [])
            if citations:
                print(f"      Research: {citations[0]['reference']}")
                print(f"               Key finding: {citations[0]['key_finding']}")

        # ── Decision Frameworks ───────────────────────────────────────────────
        print("\n🧰 RECOMMENDED DECISION FRAMEWORKS")
        print("─" * 40)
        # Use enriched frameworks from consultant if available, else fall back to report
        frameworks_to_print = ci.get("frameworks") or report.framework_recommendations
        for fw in frameworks_to_print:
            tier = fw.get("tier", "")
            tier_label = f" [{tier}]" if tier else ""
            print(f"\n  ▸ {fw['name']}{tier_label}")
            print(f"    {fw['description'][:160]}")
            print(f"    When: {fw.get('when_to_apply', '')}")
            print(f"    Example: {fw.get('example', '')}")
            if fw.get("academic_basis"):
                print(f"    📚 Academic basis: {fw['academic_basis']}")
            if fw.get("context_note"):
                print(f"    💡 For you: {fw['context_note']}")

        # ── Cross-Industry Innovations ────────────────────────────────────────
        innovations = ci.get("innovations", [])
        if innovations:
            print("\n🔬 NOVEL MITIGATIONS (Cross-Industry Pattern Recognition)")
            print("─" * 40)
            for innov in innovations[:2]:
                print(f"\n  💡 {innov['technique']}")
                print(f"     Borrowed from: {innov['borrowed_from']}")
                print(f"     {innov['description'][:200]}")
                print(f"     ROI: {innov['roi_estimate']}")
                print(f"     Academic basis: {innov['academic_basis']}")

        # ── Black Swan Warning ────────────────────────────────────────────────
        black_swan = ci.get("black_swan", {})
        if black_swan:
            print("\n🦢 BLACK SWAN / TAIL RISK WARNING")
            print("─" * 40)
            print(f"  Scenario: {black_swan.get('event', '')}")
            print(f"  Example: {black_swan.get('example', '')}")
            print(f"  Probability: {black_swan.get('probability', '')}")
            print(f"  Preparation: {black_swan.get('preparation', '')}")

        # ── Regulatory Intelligence ───────────────────────────────────────────
        reg_data = ci.get("regulatory_data", {})
        if reg_data:
            print("\n⚖️  REGULATORY INTELLIGENCE (current)")
            print("─" * 40)
            for reg in reg_data.get("active_regulations", [])[:2]:
                print(f"  • [{reg.get('risk_level', '')}] {reg.get('name', '')}")
                print(f"    Status: {reg.get('status', '')}")
                print(f"    {reg.get('summary', '')}")
            market_signals = reg_data.get("market_signals", {})
            if market_signals:
                print("\n  📈 Market signals:")
                for signal, value in list(market_signals.items())[:3]:
                    print(f"     {signal.replace('_', ' ').title()}: {value}")

        # ── 20% Reality Check ────────────────────────────────────────────────
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

        # ── Sources & Confidence ──────────────────────────────────────────────
        confidence = ci.get("confidence", {})
        sources_used = ci.get("sources_used", [])
        if confidence or sources_used:
            print("\n📚 SOURCES & CONFIDENCE")
            print("─" * 40)
            if confidence:
                print(f"  Confidence: {confidence.get('score', 0)}% ({confidence.get('label', '')}) — {confidence.get('explanation', '')}")
            if sources_used:
                print("\n  Data sources used:")
                for src in sources_used:
                    print(f"    • {src}")

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
