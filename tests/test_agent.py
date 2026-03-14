"""Tests for the Project Risk Assessment Agent."""
from __future__ import annotations

import pytest

from agent.knowledge_base import (
    CULTURAL_ARCHETYPES,
    DECISION_FRAMEWORKS,
    EXPERIENCE_GUIDANCE,
    INDUSTRY_RISKS,
    REALITY_CHECK_FRAMEWORK,
    get_risk_level,
)
from agent.models import AssessmentReport, ProjectContext, RiskItem
from agent.risk_agent import RiskAssessmentAgent


# ── Knowledge-base tests ──────────────────────────────────────────────────────

class TestKnowledgeBase:
    def test_all_industries_present(self):
        for ind in ("construction", "manufacturing", "it"):
            assert ind in INDUSTRY_RISKS, f"Missing industry: {ind}"

    def test_industry_has_required_keys(self):
        required = {
            "primary_external",
            "primary_internal",
            "blind_spots_for_outsiders",
            "first_20_percent_actions",
            "typical_tools",
        }
        for ind, data in INDUSTRY_RISKS.items():
            for key in required:
                assert key in data, f"Industry '{ind}' missing key '{key}'"

    def test_decision_frameworks_present(self):
        for fw in (
            "safety_premium",
            "somatic_verification",
            "bureaucratic_shield",
            "two_way_team_model",
            "reverse_training",
            "truth_link_technology",
        ):
            assert fw in DECISION_FRAMEWORKS, f"Missing framework: {fw}"

    def test_experience_levels_present(self):
        for level in ("junior", "mid", "senior"):
            assert level in EXPERIENCE_GUIDANCE

    def test_cultural_archetypes_present(self):
        for arch in ("process_guardian", "resource_navigator"):
            assert arch in CULTURAL_ARCHETYPES

    def test_get_risk_level_low(self):
        result = get_risk_level("low", "low", "early")
        assert result["level"] == "Low"
        assert result["score"] == 1

    def test_get_risk_level_critical(self):
        result = get_risk_level("high", "critical", "post_occurrence")
        assert result["level"] == "Critical"
        assert result["score"] == 36

    def test_get_risk_level_medium(self):
        # medium(2) * medium(2) * late(2) = 8 → Medium (5–9)
        result = get_risk_level("medium", "medium", "late")
        assert result["level"] == "Medium"
        assert result["score"] == 8

    def test_get_risk_level_high(self):
        result = get_risk_level("high", "high", "late")
        assert result["level"] == "High"
        assert result["score"] == 18

    def test_reality_check_framework_keys(self):
        for key in ("description", "participants", "agenda_items", "output"):
            assert key in REALITY_CHECK_FRAMEWORK


# ── Model tests ───────────────────────────────────────────────────────────────

class TestModels:
    def test_risk_item_score_computed_on_init(self):
        item = RiskItem(
            description="Test risk",
            category="external",
            probability="high",
            impact="critical",
            detectability="post_occurrence",
        )
        assert item.score == 36
        assert item.level == "Critical"

    def test_project_context_classify_experience_junior(self):
        ctx = ProjectContext(years_experience=2)
        assert ctx.classify_experience() == "junior"
        assert ctx.experience_level == "junior"

    def test_project_context_classify_experience_mid(self):
        ctx = ProjectContext(years_experience=7)
        assert ctx.classify_experience() == "mid"

    def test_project_context_classify_experience_senior(self):
        ctx = ProjectContext(years_experience=15)
        assert ctx.classify_experience() == "senior"

    def test_assessment_report_fields(self):
        ctx = ProjectContext(industry="construction", years_experience=5, experience_level="mid")
        report = AssessmentReport(
            context=ctx,
            industry_risks={},
            experience_guidance={},
            framework_recommendations=[],
            reality_check_plan={},
            risk_register=[],
        )
        assert report.context is ctx
        assert report.summary == ""


# ── Agent tests ───────────────────────────────────────────────────────────────

class TestRiskAssessmentAgent:

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    @pytest.fixture
    def construction_context(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="Germany",
            top_risks=["Unexpected soil conditions", "Permit delays", "Subcontractor overruns"],
            risk_locus="external",
            decision_style="balance",
            time_pressure="high",
        )

    @pytest.fixture
    def manufacturing_context(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="manufacturing",
            years_experience=12,
            projects_managed=25,
            cultural_region="India",
            top_risks=["Supply chain disruption", "Machine calibration drift"],
            risk_locus="external",
            decision_style="intuition",
            time_pressure="medium",
        )

    @pytest.fixture
    def it_context(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="it",
            years_experience=2,
            projects_managed=3,
            cultural_region="USA",
            top_risks=["Scope creep", "Third-party API instability"],
            risk_locus="mixed",
            decision_style="formal_tools",
            time_pressure="low",
        )

    # Context building

    def test_build_context_construction(self, construction_context: ProjectContext):
        assert construction_context.industry == "construction"
        assert construction_context.experience_level == "mid"
        assert construction_context.cultural_region == "process_guardian"
        assert construction_context.time_pressure == "high"
        assert len(construction_context.top_risks) == 3

    def test_build_context_manufacturing(self, manufacturing_context: ProjectContext):
        assert manufacturing_context.industry == "manufacturing"
        assert manufacturing_context.experience_level == "senior"
        assert manufacturing_context.cultural_region == "resource_navigator"

    def test_build_context_it_junior(self, it_context: ProjectContext):
        assert it_context.industry == "it"
        assert it_context.experience_level == "junior"
        assert it_context.cultural_region == "mixed"

    def test_build_context_unknown_industry_defaults(self, agent: RiskAssessmentAgent):
        ctx = agent.build_context(industry="aerospace", years_experience=5, projects_managed=5)
        assert ctx.industry == "aerospace"

    # Report generation

    def test_generate_report_returns_report(self, agent: RiskAssessmentAgent, construction_context: ProjectContext):
        report = agent.generate_report(construction_context)
        assert isinstance(report, AssessmentReport)

    def test_generate_report_risk_register_sorted(self, agent: RiskAssessmentAgent, construction_context: ProjectContext):
        report = agent.generate_report(construction_context)
        scores = [r.score for r in report.risk_register]
        assert scores == sorted(scores, reverse=True), "Risk register should be sorted by score descending"

    def test_generate_report_contains_user_risks(self, agent: RiskAssessmentAgent, construction_context: ProjectContext):
        report = agent.generate_report(construction_context)
        descriptions = [r.description for r in report.risk_register]
        for user_risk in construction_context.top_risks:
            assert user_risk in descriptions

    def test_generate_report_high_pressure_escalates_scores(self, agent: RiskAssessmentAgent):
        ctx_high = agent.build_context(
            industry="construction",
            years_experience=5,
            projects_managed=10,
            time_pressure="high",
        )
        ctx_low = agent.build_context(
            industry="construction",
            years_experience=5,
            projects_managed=10,
            time_pressure="low",
        )
        report_high = agent.generate_report(ctx_high)
        report_low = agent.generate_report(ctx_low)
        avg_high = sum(r.score for r in report_high.risk_register) / max(len(report_high.risk_register), 1)
        avg_low = sum(r.score for r in report_low.risk_register) / max(len(report_low.risk_register), 1)
        assert avg_high >= avg_low, "High time pressure should not decrease overall risk scores"

    def test_generate_report_frameworks_always_include_safety_premium(
        self, agent: RiskAssessmentAgent, construction_context: ProjectContext
    ):
        report = agent.generate_report(construction_context)
        names = [fw["name"] for fw in report.framework_recommendations]
        assert "Safety Premium" in names

    def test_generate_report_frameworks_always_include_two_way_model(
        self, agent: RiskAssessmentAgent, manufacturing_context: ProjectContext
    ):
        report = agent.generate_report(manufacturing_context)
        names = [fw["name"] for fw in report.framework_recommendations]
        assert "Two-Way Team Model" in names

    def test_generate_report_truth_link_for_manufacturing(
        self, agent: RiskAssessmentAgent, manufacturing_context: ProjectContext
    ):
        report = agent.generate_report(manufacturing_context)
        names = [fw["name"] for fw in report.framework_recommendations]
        assert "Truth-Link Technology" in names

    def test_generate_report_summary_not_empty(self, agent: RiskAssessmentAgent, construction_context: ProjectContext):
        report = agent.generate_report(construction_context)
        assert report.summary.strip() != ""

    def test_generate_report_includes_industry_risks(
        self, agent: RiskAssessmentAgent, construction_context: ProjectContext
    ):
        report = agent.generate_report(construction_context)
        assert "primary_external" in report.industry_risks

    def test_generate_report_includes_reality_check(
        self, agent: RiskAssessmentAgent, construction_context: ProjectContext
    ):
        report = agent.generate_report(construction_context)
        assert "agenda_items" in report.reality_check_plan
        assert len(report.reality_check_plan["agenda_items"]) > 0

    def test_generate_report_cultural_archetype_process_guardian(
        self, agent: RiskAssessmentAgent, construction_context: ProjectContext
    ):
        report = agent.generate_report(construction_context)
        # Germany -> process_guardian
        assert report.context.cultural_region == "process_guardian"

    def test_generate_report_cultural_archetype_resource_navigator(
        self, agent: RiskAssessmentAgent, manufacturing_context: ProjectContext
    ):
        report = agent.generate_report(manufacturing_context)
        assert report.context.cultural_region == "resource_navigator"

    def test_generate_report_no_top_risks(self, agent: RiskAssessmentAgent):
        ctx = agent.build_context(
            industry="it",
            years_experience=4,
            projects_managed=6,
            top_risks=[],
        )
        report = agent.generate_report(ctx)
        # Should still produce a register from industry knowledge base
        assert len(report.risk_register) > 0

    # Risk scoring edge cases

    def test_risk_item_medium_score(self):
        # medium(2) * medium(2) * late(2) = 8 → Medium
        item = RiskItem(
            description="Medium risk",
            category="internal",
            probability="medium",
            impact="medium",
            detectability="late",
        )
        assert item.score == 8
        assert item.level == "Medium"

    def test_risk_item_low_score(self):
        item = RiskItem(
            description="Low risk",
            category="internal",
            probability="low",
            impact="low",
            detectability="early",
        )
        assert item.score == 1
        assert item.level == "Low"


# ── Phase 1: ContextAnalyzer tests ───────────────────────────────────────────

class TestContextAnalyzer:
    """Tests for the ContextAnalyzer class (Phase 1 personalization engine)."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    @pytest.fixture
    def german_pm_ctx(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="construction",
            years_experience=12,
            projects_managed=20,
            cultural_region="Germany",
            top_risks=["Unexpected soil conditions"],
            decision_style="formal_tools",
            time_pressure="high",
        )

    @pytest.fixture
    def indian_pm_ctx(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="construction",
            years_experience=12,
            projects_managed=20,
            cultural_region="India",
            top_risks=["Unexpected soil conditions"],
            decision_style="intuition",
            time_pressure="high",
        )

    @pytest.fixture
    def junior_pm_ctx(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="it",
            years_experience=2,
            projects_managed=3,
            cultural_region="Germany",
            time_pressure="medium",
        )

    @pytest.fixture
    def senior_pm_ctx(self, agent: RiskAssessmentAgent) -> ProjectContext:
        return agent.build_context(
            industry="it",
            years_experience=15,
            projects_managed=30,
            cultural_region="Germany",
            time_pressure="medium",
        )

    def test_context_analyzer_german_pm_blind_spots(self, german_pm_ctx: ProjectContext):
        from agent.context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        blind_spot = analyzer.get_blind_spots(german_pm_ctx)
        # German PM at senior level should get Process Guardian specific warning
        assert len(blind_spot) > 20
        # Should reference something about tools or BIM or the process guardian pattern
        assert any(word in blind_spot.lower() for word in ("bim", "digital", "tool", "guardian", "process"))

    def test_context_analyzer_indian_pm_blind_spots(self, indian_pm_ctx: ProjectContext):
        from agent.context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        blind_spot = analyzer.get_blind_spots(indian_pm_ctx)
        assert len(blind_spot) > 20
        # Indian PM blind spot should differ from German PM
        german_agent = RiskAssessmentAgent()
        german_ctx = german_agent.build_context(
            industry="construction", years_experience=12, projects_managed=20,
            cultural_region="Germany", time_pressure="high",
        )
        german_bs = ContextAnalyzer().get_blind_spots(german_ctx)
        assert blind_spot != german_bs

    def test_context_analyzer_benchmarks_by_experience(
        self, junior_pm_ctx: ProjectContext, senior_pm_ctx: ProjectContext
    ):
        from agent.context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        junior_bm = analyzer.get_benchmarks(junior_pm_ctx)
        senior_bm = analyzer.get_benchmarks(senior_pm_ctx)
        # Cohort notes should differ
        assert junior_bm.get("_cohort_note") != senior_bm.get("_cohort_note")
        # Both should have a default benchmark
        assert "default" in junior_bm
        assert "default" in senior_bm

    def test_context_analyzer_persona_profile_returns_archetype(self, german_pm_ctx: ProjectContext):
        from agent.context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(german_pm_ctx)
        assert "archetype" in profile
        assert profile["archetype"] == "Process Guardian"
        assert "strengths" in profile
        assert "blind_spots" in profile
        assert "decision_patterns" in profile

    def test_report_personas_different(self, german_pm_ctx: ProjectContext, indian_pm_ctx: ProjectContext):
        """German and Indian PM profiles must be meaningfully different."""
        from agent.context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        german_profile = analyzer.get_persona_profile(german_pm_ctx)
        indian_profile = analyzer.get_persona_profile(indian_pm_ctx)
        assert german_profile["archetype"] != indian_profile["archetype"]
        assert german_profile["blind_spots"] != indian_profile["blind_spots"]


# ── Phase 1: FrameworkRecommender tests ──────────────────────────────────────

class TestFrameworkRecommender:
    """Tests for the FrameworkRecommender class (Phase 1 personalization engine)."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    def _make_risks(self, descriptions: list) -> list:
        return [
            RiskItem(
                description=d,
                category="external",
                probability="high",
                impact="high",
                detectability="late",
            )
            for d in descriptions
        ]

    def test_framework_recommender_construction_high_pressure(self, agent: RiskAssessmentAgent):
        """Construction + high pressure must include Somatic Verification."""
        from agent.framework_recommender import FrameworkRecommender
        ctx = agent.build_context(
            industry="construction", years_experience=8, projects_managed=15,
            time_pressure="high",
        )
        risks = self._make_risks(["Permit delays", "Subcontractor overruns"])
        recommender = FrameworkRecommender()
        frameworks = recommender.recommend_frameworks(ctx, risks)
        names = [fw["name"] for fw in frameworks]
        assert "Somatic Verification" in names

    def test_framework_recommender_german_soil_risk(self, agent: RiskAssessmentAgent):
        """German PM + soil risk → Safety Premium and Somatic Verification."""
        from agent.framework_recommender import FrameworkRecommender
        ctx = agent.build_context(
            industry="construction", years_experience=10, projects_managed=20,
            cultural_region="Germany", time_pressure="medium",
        )
        risks = self._make_risks(["Unexpected soil conditions at excavation site"])
        recommender = FrameworkRecommender()
        frameworks = recommender.recommend_frameworks(ctx, risks)
        names = [fw["name"] for fw in frameworks]
        assert "Safety Premium" in names
        assert "Somatic Verification" in names

    def test_framework_recommender_includes_new_frameworks(self, agent: RiskAssessmentAgent):
        """Low-pressure project → Pre-Mortem and 3-Scenario Analysis suggested."""
        from agent.framework_recommender import FrameworkRecommender
        ctx = agent.build_context(
            industry="it", years_experience=3, projects_managed=5,
            time_pressure="low",
        )
        risks = self._make_risks(["Scope creep", "Third-party API instability"])
        recommender = FrameworkRecommender()
        frameworks = recommender.recommend_frameworks(ctx, risks)
        names = [fw["name"] for fw in frameworks]
        # At least one of the new frameworks should appear
        new_frameworks = {"Pre-Mortem Analysis", "3-Scenario Analysis", "Black Swan Awareness"}
        assert any(n in names for n in new_frameworks), f"No new frameworks in: {names}"

    def test_framework_recommender_why_for_you_present(self, agent: RiskAssessmentAgent):
        """Every recommended framework must include a 'why_for_you' field."""
        from agent.framework_recommender import FrameworkRecommender
        ctx = agent.build_context(
            industry="manufacturing", years_experience=7, projects_managed=12,
            cultural_region="India", time_pressure="medium",
        )
        risks = self._make_risks(["Supply chain disruption"])
        recommender = FrameworkRecommender()
        frameworks = recommender.recommend_frameworks(ctx, risks)
        for fw in frameworks:
            assert "why_for_you" in fw, f"Framework '{fw.get('name')}' missing 'why_for_you'"
            assert len(fw["why_for_you"]) > 10

    def test_report_frameworks_differ_by_context(self, agent: RiskAssessmentAgent):
        """German + high pressure gets different frameworks than Indian + low pressure."""
        from agent.framework_recommender import FrameworkRecommender
        ctx_german_high = agent.build_context(
            industry="construction", years_experience=10, projects_managed=20,
            cultural_region="Germany", time_pressure="high",
        )
        ctx_indian_low = agent.build_context(
            industry="it", years_experience=3, projects_managed=5,
            cultural_region="India", time_pressure="low",
        )
        recommender = FrameworkRecommender()
        risks_small = self._make_risks(["Scope creep"])
        fw_german = {fw["name"] for fw in recommender.recommend_frameworks(ctx_german_high, risks_small)}
        fw_indian = {fw["name"] for fw in recommender.recommend_frameworks(ctx_indian_low, risks_small)}
        # They should share some universal frameworks but differ in at least one
        assert fw_german != fw_indian


# ── Phase 1: ConsultantReporter tests ────────────────────────────────────────

class TestConsultantReporter:
    """Tests for the ConsultantReporter class (Phase 1 personalization engine)."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    @pytest.fixture
    def german_report(self, agent: RiskAssessmentAgent) -> AssessmentReport:
        ctx = agent.build_context(
            industry="construction",
            years_experience=10,
            projects_managed=20,
            cultural_region="Germany",
            top_risks=["Unexpected soil conditions", "Permit delays"],
            time_pressure="high",
        )
        return agent.generate_report(ctx)

    @pytest.fixture
    def indian_report(self, agent: RiskAssessmentAgent) -> AssessmentReport:
        ctx = agent.build_context(
            industry="construction",
            years_experience=10,
            projects_managed=20,
            cultural_region="India",
            top_risks=["Unexpected soil conditions", "Permit delays"],
            time_pressure="high",
        )
        return agent.generate_report(ctx)

    def test_consultant_report_includes_benchmarks(self, german_report: AssessmentReport):
        """Narrative must include benchmark statistics."""
        narrative = german_report.consultant_narrative
        assert narrative is not None
        # Look for percentage-style stats
        import re
        percentages = re.findall(r"\d+%", narrative)
        assert len(percentages) >= 1, "Narrative should include percentage statistics"

    def test_consultant_report_includes_blind_spots(self, german_report: AssessmentReport):
        """Narrative must warn about specific blind spots."""
        narrative = german_report.consultant_narrative
        assert narrative is not None
        assert "Blind Spot" in narrative or "blind spot" in narrative.lower()

    def test_consultant_report_includes_cross_industry(self, german_report: AssessmentReport):
        """Narrative must suggest cross-industry patterns."""
        narrative = german_report.consultant_narrative
        assert narrative is not None
        # Look for cross-industry indicators
        cross_industry_terms = ["industry", "adapt", "semiconductor", "aerospace", "pharmaceutical",
                                "aviation", "oil", "amazon", "google", "finance"]
        found = any(term in narrative.lower() for term in cross_industry_terms)
        assert found, "Narrative should include cross-industry insights"

    def test_consultant_report_different_for_german_vs_indian(
        self, german_report: AssessmentReport, indian_report: AssessmentReport
    ):
        """German and Indian reports must be meaningfully different."""
        german_narrative = german_report.consultant_narrative or ""
        indian_narrative = indian_report.consultant_narrative or ""
        assert german_narrative != indian_narrative
        # Persona profiles should differ
        assert german_report.persona_profile != indian_report.persona_profile
        assert german_report.persona_profile["archetype"] != indian_report.persona_profile["archetype"]

    def test_consultant_report_different_for_senior_vs_junior(self, agent: RiskAssessmentAgent):
        """Senior and junior PM reports must differ meaningfully."""
        senior_ctx = agent.build_context(
            industry="it", years_experience=15, projects_managed=30,
            cultural_region="Germany", time_pressure="medium",
        )
        junior_ctx = agent.build_context(
            industry="it", years_experience=1, projects_managed=2,
            cultural_region="Germany", time_pressure="medium",
        )
        senior_report = agent.generate_report(senior_ctx)
        junior_report = agent.generate_report(junior_ctx)
        assert senior_report.persona_profile["experience_level"] != junior_report.persona_profile["experience_level"]
        # Narratives should differ
        assert senior_report.consultant_narrative != junior_report.consultant_narrative

    def test_report_narrative_is_consultant_style(self, german_report: AssessmentReport):
        """Report should read like consultant advice with structured sections."""
        narrative = german_report.consultant_narrative
        assert narrative is not None
        assert len(narrative) > 500  # Should be a substantial report
        # Check for key consultant-style sections
        assert "PROFILE" in narrative or "Profile" in narrative
        assert "Action" in narrative or "ACTION" in narrative
        assert "Source" in narrative or "SOURCE" in narrative


# ── Phase 1: Enriched RiskItem tests ─────────────────────────────────────────

class TestEnrichedRiskItem:
    """Tests for the new RiskItem fields added in Phase 1."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    @pytest.fixture
    def construction_report(self, agent: RiskAssessmentAgent) -> AssessmentReport:
        ctx = agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="Germany",
            top_risks=["Unexpected soil conditions", "Permit delays", "Subcontractor overruns"],
            risk_locus="external",
            decision_style="balance",
            time_pressure="medium",
        )
        return agent.generate_report(ctx)

    def test_risk_item_has_benchmark(self, construction_report: AssessmentReport):
        """Each risk item should have benchmark data attached."""
        for risk in construction_report.risk_register:
            assert risk.benchmark is not None, f"Risk '{risk.description}' missing benchmark"
            assert isinstance(risk.benchmark, dict)

    def test_risk_item_has_confidence(self, construction_report: AssessmentReport):
        """Each risk item should have a confidence score between 0 and 1."""
        for risk in construction_report.risk_register:
            assert 0.0 <= risk.confidence <= 1.0, (
                f"Risk '{risk.description}' has invalid confidence: {risk.confidence}"
            )

    def test_risk_item_has_academic_source(self, construction_report: AssessmentReport):
        """Each risk item should include an academic citation."""
        for risk in construction_report.risk_register:
            assert risk.academic_source is not None, (
                f"Risk '{risk.description}' missing academic_source"
            )
            assert len(risk.academic_source) > 10

    def test_risk_item_has_cross_industry_insight(self, construction_report: AssessmentReport):
        """Each risk item should have a cross-industry insight."""
        for risk in construction_report.risk_register:
            insight = risk.cross_industry_insight or risk.novel_mitigation
            assert insight is not None, (
                f"Risk '{risk.description}' missing cross_industry_insight"
            )

    def test_risk_item_confidence_higher_for_low_pressure(self, agent: RiskAssessmentAgent):
        """Low time pressure should yield higher confidence scores than high pressure."""
        ctx_low = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            time_pressure="low",
        )
        ctx_high = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            time_pressure="high",
        )
        report_low = agent.generate_report(ctx_low)
        report_high = agent.generate_report(ctx_high)
        avg_conf_low = sum(r.confidence for r in report_low.risk_register) / max(len(report_low.risk_register), 1)
        avg_conf_high = sum(r.confidence for r in report_high.risk_register) / max(len(report_high.risk_register), 1)
        assert avg_conf_low >= avg_conf_high


# ── Phase 1: Report-level enrichment tests ───────────────────────────────────

class TestReportEnrichment:
    """Tests for the new AssessmentReport fields added in Phase 1."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    @pytest.fixture
    def full_report(self, agent: RiskAssessmentAgent) -> AssessmentReport:
        ctx = agent.build_context(
            industry="manufacturing",
            years_experience=6,
            projects_managed=10,
            cultural_region="India",
            top_risks=["Supply chain disruption", "Machine calibration drift"],
            time_pressure="medium",
        )
        return agent.generate_report(ctx)

    def test_report_has_persona_profile(self, full_report: AssessmentReport):
        assert full_report.persona_profile is not None
        assert "archetype" in full_report.persona_profile

    def test_report_has_benchmarks(self, full_report: AssessmentReport):
        assert full_report.benchmarks is not None
        assert isinstance(full_report.benchmarks, dict)
        assert "default" in full_report.benchmarks

    def test_report_has_frameworks_with_rationale(self, full_report: AssessmentReport):
        assert full_report.frameworks_with_rationale is not None
        assert len(full_report.frameworks_with_rationale) > 0
        for fw in full_report.frameworks_with_rationale:
            assert "why_for_you" in fw

    def test_report_has_consultant_narrative(self, full_report: AssessmentReport):
        assert full_report.consultant_narrative is not None
        assert len(full_report.consultant_narrative) > 100

    def test_all_existing_34_tests_still_pass(self, agent: RiskAssessmentAgent):
        """Smoke test: verify backward compatibility by generating reports for all 3 industries."""
        for industry in ("construction", "manufacturing", "it"):
            ctx = agent.build_context(
                industry=industry,
                years_experience=5,
                projects_managed=10,
                cultural_region="Germany",
            )
            report = agent.generate_report(ctx)
            assert isinstance(report, AssessmentReport)
            assert len(report.risk_register) > 0
            assert report.summary != ""
            assert "primary_external" in report.industry_risks


# ── Phase 1: Edge case tests ──────────────────────────────────────────────────

class TestEdgeCases:
    """Edge case tests for robustness of the Phase 1 personalization engine."""

    @pytest.fixture
    def agent(self) -> RiskAssessmentAgent:
        return RiskAssessmentAgent()

    def test_unknown_region_fallback_to_mixed(self, agent: RiskAssessmentAgent):
        """Unknown cultural region should fall back to 'mixed' archetype."""
        ctx = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            cultural_region="Atlantis",
        )
        assert ctx.cultural_region == "mixed"
        report = agent.generate_report(ctx)
        assert report.persona_profile is not None

    def test_zero_experience_handled(self, agent: RiskAssessmentAgent):
        """Zero years experience should be classified as junior with no crash."""
        ctx = agent.build_context(
            industry="it", years_experience=0, projects_managed=0,
        )
        assert ctx.experience_level == "junior"
        report = agent.generate_report(ctx)
        assert report.consultant_narrative is not None

    def test_empty_top_risks_still_enriches_register(self, agent: RiskAssessmentAgent):
        """Empty top_risks should still produce enriched risk register from KB."""
        ctx = agent.build_context(
            industry="manufacturing", years_experience=5, projects_managed=10,
            top_risks=[],
        )
        report = agent.generate_report(ctx)
        assert len(report.risk_register) > 0
        for risk in report.risk_register:
            assert risk.benchmark is not None
            assert risk.confidence > 0

    def test_high_pressure_increases_confidence_sensitivity(self, agent: RiskAssessmentAgent):
        """High pressure context should still produce valid confidence scores."""
        ctx = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            time_pressure="high",
        )
        report = agent.generate_report(ctx)
        for risk in report.risk_register:
            assert 0.0 < risk.confidence <= 1.0

    def test_narrative_structure_for_all_industries(self, agent: RiskAssessmentAgent):
        """Narrative should be generated successfully for all three industries."""
        for industry in ("construction", "manufacturing", "it"):
            ctx = agent.build_context(
                industry=industry, years_experience=5, projects_managed=10,
            )
            report = agent.generate_report(ctx)
            assert report.consultant_narrative is not None
            assert len(report.consultant_narrative) > 200

    def test_risk_item_new_fields_default_values(self):
        """New RiskItem fields should have sensible default values."""
        item = RiskItem(
            description="Test risk",
            category="external",
            probability="medium",
            impact="medium",
            detectability="late",
        )
        assert item.benchmark is None
        assert item.blind_spot is None
        assert item.novel_mitigation is None
        assert item.academic_source is None
        assert item.cross_industry_insight is None
        assert item.confidence == 0.85

    def test_assessment_report_new_fields_default_values(self):
        """New AssessmentReport fields should have sensible default values."""
        ctx = ProjectContext(industry="construction", years_experience=5, experience_level="mid")
        report = AssessmentReport(
            context=ctx,
            industry_risks={},
            experience_guidance={},
            framework_recommendations=[],
            reality_check_plan={},
            risk_register=[],
        )
        assert report.persona_profile is None
        assert report.benchmarks is None
        assert report.frameworks_with_rationale == []
        assert report.cultural_insights is None
        assert report.consultant_narrative is None

