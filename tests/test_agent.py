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

    # Input-sensitivity tests — different inputs must produce different outputs

    def test_time_pressure_produces_different_scores(self, agent: RiskAssessmentAgent):
        """Changing time pressure must visibly change risk scores."""
        results = {}
        for tp in ("low", "medium", "high"):
            ctx = agent.build_context(
                industry="construction", years_experience=5, projects_managed=10,
                top_risks=["Test risk"], time_pressure=tp,
            )
            report = agent.generate_report(ctx)
            results[tp] = sum(r.score for r in report.risk_register)
        assert results["low"] < results["medium"] < results["high"], (
            f"Scores must increase with pressure: low={results['low']}, "
            f"medium={results['medium']}, high={results['high']}"
        )

    def test_decision_style_produces_different_frameworks(self, agent: RiskAssessmentAgent):
        """Each decision style must select a different set of frameworks."""
        results = {}
        for ds in ("intuition", "balance", "formal_tools"):
            ctx = agent.build_context(
                industry="it", years_experience=5, projects_managed=10,
                cultural_region="USA", decision_style=ds, time_pressure="medium",
            )
            report = agent.generate_report(ctx)
            results[ds] = {fw["name"] for fw in report.framework_recommendations}
        assert results["intuition"] != results["balance"], "intuition and balance must differ"
        assert results["balance"] != results["formal_tools"], "balance and formal_tools must differ"

    def test_risk_locus_affects_user_risk_scores(self, agent: RiskAssessmentAgent):
        """Internal-locus risks should score differently from external-locus risks."""
        ctx_int = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            top_risks=["Same risk"], risk_locus="internal", time_pressure="medium",
        )
        ctx_ext = agent.build_context(
            industry="construction", years_experience=5, projects_managed=10,
            top_risks=["Same risk"], risk_locus="external", time_pressure="medium",
        )
        report_int = agent.generate_report(ctx_int)
        report_ext = agent.generate_report(ctx_ext)
        # Find the user-provided risk in each register
        user_int = next(r for r in report_int.risk_register if r.description == "Same risk")
        user_ext = next(r for r in report_ext.risk_register if r.description == "Same risk")
        assert user_int.score != user_ext.score, (
            f"Internal ({user_int.score}) and external ({user_ext.score}) should differ"
        )

    def test_same_inputs_produce_same_output(self, agent: RiskAssessmentAgent):
        """Identical inputs must always produce identical output (deterministic)."""
        kwargs = dict(
            industry="manufacturing", years_experience=12, projects_managed=25,
            cultural_region="India", top_risks=["Supply chain disruption"],
            risk_locus="external", decision_style="intuition", time_pressure="high",
        )
        report1 = agent.generate_report(agent.build_context(**kwargs))
        report2 = agent.generate_report(agent.build_context(**kwargs))
        scores1 = [r.score for r in report1.risk_register]
        scores2 = [r.score for r in report2.risk_register]
        fws1 = [fw["name"] for fw in report1.framework_recommendations]
        fws2 = [fw["name"] for fw in report2.framework_recommendations]
        assert scores1 == scores2, "Same inputs must produce identical scores"
        assert fws1 == fws2, "Same inputs must produce identical frameworks"
