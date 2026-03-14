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


# ── New module tests ──────────────────────────────────────────────────────────


class TestContextAnalyzer:
    """Tests for the context analyzer module."""

    @pytest.fixture
    def analyzer(self):
        from agent.context_analyzer import ContextAnalyzer
        return ContextAnalyzer()

    def test_analyze_returns_required_keys(self, analyzer):
        ctx = ProjectContext(
            industry="construction",
            years_experience=8,
            experience_level="mid",
            cultural_region="process_guardian",
            time_pressure="high",
            decision_style="balance",
        )
        result = analyzer.analyze(ctx)
        for key in ("persona", "benchmarks", "time_pressure_insights", "decision_style_insights", "confidence_level"):
            assert key in result, f"Missing key: {key}"

    def test_persona_differs_junior_vs_senior_process_guardian(self, analyzer):
        ctx_junior = ProjectContext(
            industry="construction", years_experience=2, experience_level="junior",
            cultural_region="process_guardian", time_pressure="medium", decision_style="balance",
        )
        ctx_senior = ProjectContext(
            industry="construction", years_experience=15, experience_level="senior",
            cultural_region="process_guardian", time_pressure="medium", decision_style="balance",
        )
        result_junior = analyzer.analyze(ctx_junior)
        result_senior = analyzer.analyze(ctx_senior)
        # Different personas for different experience levels
        assert result_junior["persona"]["persona"] != result_senior["persona"]["persona"]

    def test_benchmarks_differ_by_region(self, analyzer):
        ctx_pg = ProjectContext(
            industry="construction", years_experience=5, experience_level="mid",
            cultural_region="process_guardian", time_pressure="medium", decision_style="balance",
        )
        ctx_rn = ProjectContext(
            industry="construction", years_experience=5, experience_level="mid",
            cultural_region="resource_navigator", time_pressure="medium", decision_style="balance",
        )
        result_pg = analyzer.analyze(ctx_pg)
        result_rn = analyzer.analyze(ctx_rn)
        # Benchmark blind spots differ by region
        assert result_pg["benchmarks"].get("blind_spot") != result_rn["benchmarks"].get("blind_spot")

    def test_time_pressure_high_includes_escalation_note(self, analyzer):
        ctx = ProjectContext(
            industry="it", years_experience=5, experience_level="mid",
            cultural_region="mixed", time_pressure="high", decision_style="balance",
        )
        result = analyzer.analyze(ctx)
        note = result["time_pressure_insights"].get("risk_escalation_note", "")
        assert "HIGH TIME PRESSURE" in note

    def test_time_pressure_low_includes_complacency_warning(self, analyzer):
        ctx = ProjectContext(
            industry="it", years_experience=5, experience_level="mid",
            cultural_region="mixed", time_pressure="low", decision_style="balance",
        )
        result = analyzer.analyze(ctx)
        note = result["time_pressure_insights"].get("behavioral_warning", "")
        assert len(note) > 10

    def test_confidence_score_is_within_bounds(self, analyzer):
        ctx = ProjectContext(
            industry="manufacturing", years_experience=12, experience_level="senior",
            cultural_region="process_guardian", time_pressure="medium", decision_style="formal_tools",
            top_risks=["Supply chain", "Calibration", "Compliance"],
            projects_managed=20,
        )
        result = analyzer.analyze(ctx)
        score = result["confidence_level"]["score"]
        assert 50 <= score <= 97

    def test_decision_style_formal_tools_warns_about_analysis_paralysis(self, analyzer):
        ctx = ProjectContext(
            industry="construction", years_experience=5, experience_level="mid",
            cultural_region="mixed", time_pressure="medium", decision_style="formal_tools",
        )
        result = analyzer.analyze(ctx)
        blind_spot = result["decision_style_insights"].get("blind_spot", "")
        assert "paralysis" in blind_spot.lower() or "tool" in blind_spot.lower()


class TestResearchEngine:
    """Tests for the research engine module."""

    @pytest.fixture
    def engine(self):
        from agent.research_engine import ResearchEngine
        return ResearchEngine()

    def test_get_citations_returns_list(self, engine):
        citations = engine.get_citations_for_risk("soil conditions", "construction", "senior")
        assert isinstance(citations, list)
        assert len(citations) > 0

    def test_get_citations_deduplicated(self, engine):
        citations = engine.get_citations_for_risk("compliance mdr regulatory", "manufacturing", "mid")
        refs = [c["reference"] for c in citations]
        assert len(refs) == len(set(refs)), "Citations should be deduplicated"

    def test_get_citations_max_four(self, engine):
        citations = engine.get_citations_for_risk("security cyber gdpr dora compliance breach", "it", "junior")
        assert len(citations) <= 4

    def test_get_citations_includes_pmi_for_all(self, engine):
        citations = engine.get_citations_for_risk("any generic risk", "construction", "mid")
        refs = [c["reference"] for c in citations]
        assert any("PMI" in ref for ref in refs), "PMI citation should always be included"

    def test_get_industry_reports_construction(self, engine):
        reports = engine.get_industry_reports("construction")
        assert isinstance(reports, list)
        assert len(reports) > 0
        for rep in reports:
            assert "title" in rep and "publisher" in rep and "key_insight" in rep

    def test_get_industry_reports_manufacturing(self, engine):
        reports = engine.get_industry_reports("manufacturing")
        assert len(reports) > 0

    def test_get_industry_reports_it(self, engine):
        reports = engine.get_industry_reports("it")
        assert len(reports) > 0

    def test_get_cross_industry_innovations_returns_list(self, engine):
        innovations = engine.get_cross_industry_innovations("construction")
        assert isinstance(innovations, list)
        assert len(innovations) > 0
        for innov in innovations:
            assert "technique" in innov
            assert "borrowed_from" in innov
            assert "roi_estimate" in innov

    def test_get_black_swan_warning_returns_valid_dict(self, engine):
        bs = engine.get_black_swan_warning("manufacturing")
        assert "event" in bs
        assert "preparation" in bs
        assert "source" in bs


class TestFrameworkRecommender:
    """Tests for the framework recommender module."""

    @pytest.fixture
    def recommender(self):
        from agent.framework_recommender import FrameworkRecommender
        return FrameworkRecommender()

    def test_recommend_returns_list(self, recommender):
        ctx = ProjectContext(
            industry="construction", years_experience=8, experience_level="mid",
            cultural_region="process_guardian", time_pressure="high", decision_style="balance",
        )
        frameworks = recommender.recommend(ctx)
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0

    def test_recommend_includes_safety_premium(self, recommender):
        ctx = ProjectContext(
            industry="construction", years_experience=5, experience_level="mid",
            cultural_region="mixed", time_pressure="medium", decision_style="balance",
        )
        frameworks = recommender.recommend(ctx)
        names = [fw["name"] for fw in frameworks]
        assert "Safety Premium" in names

    def test_recommend_includes_pre_mortem(self, recommender):
        ctx = ProjectContext(
            industry="it", years_experience=7, experience_level="mid",
            cultural_region="mixed", time_pressure="medium", decision_style="balance",
        )
        frameworks = recommender.recommend(ctx)
        names = [fw["name"] for fw in frameworks]
        assert "Pre-Mortem Analysis" in names

    def test_recommend_includes_black_swan_for_senior(self, recommender):
        ctx = ProjectContext(
            industry="construction", years_experience=15, experience_level="senior",
            cultural_region="process_guardian", time_pressure="medium", decision_style="balance",
        )
        frameworks = recommender.recommend(ctx)
        names = [fw["name"] for fw in frameworks]
        assert "Black Swan Analysis" in names

    def test_recommend_includes_lean_buffers_for_high_pressure(self, recommender):
        ctx = ProjectContext(
            industry="manufacturing", years_experience=5, experience_level="mid",
            cultural_region="mixed", time_pressure="high", decision_style="balance",
        )
        frameworks = recommender.recommend(ctx)
        names = [fw["name"] for fw in frameworks]
        assert "Lean Risk Buffers" in names

    def test_recommend_all_frameworks_have_academic_basis(self, recommender):
        ctx = ProjectContext(
            industry="it", years_experience=12, experience_level="senior",
            cultural_region="process_guardian", time_pressure="high", decision_style="formal_tools",
        )
        frameworks = recommender.recommend(ctx)
        for fw in frameworks:
            assert fw.get("academic_basis"), f"Framework '{fw.get('name')}' missing academic_basis"


class TestDataFetcher:
    """Tests for the data fetcher module."""

    @pytest.fixture
    def fetcher(self):
        from agent.data_fetcher import DataFetcher
        return DataFetcher(use_live_data=False)

    def test_get_regulatory_data_construction(self, fetcher):
        data = fetcher.get_regulatory_data("construction")
        assert "active_regulations" in data
        assert len(data["active_regulations"]) > 0

    def test_get_regulatory_data_manufacturing(self, fetcher):
        data = fetcher.get_regulatory_data("manufacturing")
        assert "active_regulations" in data

    def test_get_regulatory_data_it(self, fetcher):
        data = fetcher.get_regulatory_data("it")
        assert "active_regulations" in data
        # DORA should be present for IT
        names = [r["name"] for r in data["active_regulations"]]
        assert any("DORA" in n for n in names)

    def test_get_market_signals_returns_dict(self, fetcher):
        signals = fetcher.get_market_signals("construction")
        assert isinstance(signals, dict)
        assert len(signals) > 0

    def test_get_data_freshness_returns_valid_metadata(self, fetcher):
        freshness = fetcher.get_data_freshness("it")
        assert "last_updated" in freshness
        assert "data_source" in freshness

    def test_get_geopolitical_data_returns_risks(self, fetcher):
        geo = fetcher.get_geopolitical_data()
        assert "key_risks" in geo
        assert len(geo["key_risks"]) > 0

    def test_caching_works(self, fetcher):
        # Call twice — both calls should return the same data content
        data1 = fetcher.get_regulatory_data("manufacturing")
        data2 = fetcher.get_regulatory_data("manufacturing")
        assert data1 == data2


class TestConsultantReportIntegration:
    """Integration tests for consultant report generation."""

    @pytest.fixture
    def agent(self):
        return RiskAssessmentAgent()

    def test_consultant_insights_populated_on_generate_report(self, agent):
        ctx = agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="Germany",
            top_risks=["Soil conditions", "Permit delays"],
            time_pressure="high",
        )
        report = agent.generate_report(ctx)
        assert isinstance(report.consultant_insights, dict)
        assert len(report.consultant_insights) > 0

    def test_reports_differ_junior_vs_senior_germany(self, agent):
        ctx_junior = agent.build_context(
            industry="construction", years_experience=2, projects_managed=3,
            cultural_region="Germany", time_pressure="medium",
        )
        ctx_senior = agent.build_context(
            industry="construction", years_experience=15, projects_managed=40,
            cultural_region="Germany", time_pressure="medium",
        )
        report_j = agent.generate_report(ctx_junior)
        report_s = agent.generate_report(ctx_senior)
        # Personas should be different
        persona_j = report_j.consultant_insights.get("persona", {}).get("persona", "")
        persona_s = report_s.consultant_insights.get("persona", {}).get("persona", "")
        assert persona_j != persona_s, "Junior and senior should have different consultant personas"

    def test_reports_differ_germany_vs_india(self, agent):
        ctx_de = agent.build_context(
            industry="construction", years_experience=8, projects_managed=15,
            cultural_region="Germany", time_pressure="medium",
        )
        ctx_in = agent.build_context(
            industry="construction", years_experience=8, projects_managed=15,
            cultural_region="India", time_pressure="medium",
        )
        report_de = agent.generate_report(ctx_de)
        report_in = agent.generate_report(ctx_in)
        # Regional blind spots differ
        bs_de = report_de.consultant_insights.get("benchmarks", {}).get("blind_spot", "")
        bs_in = report_in.consultant_insights.get("benchmarks", {}).get("blind_spot", "")
        assert bs_de != bs_in, "German and Indian PMs should have different regional blind spots"

    def test_reports_differ_high_vs_low_pressure(self, agent):
        ctx_high = agent.build_context(
            industry="it", years_experience=5, projects_managed=8,
            cultural_region="USA", time_pressure="high",
        )
        ctx_low = agent.build_context(
            industry="it", years_experience=5, projects_managed=8,
            cultural_region="USA", time_pressure="low",
        )
        report_high = agent.generate_report(ctx_high)
        report_low = agent.generate_report(ctx_low)
        note_high = report_high.consultant_insights.get("time_pressure_insights", {}).get("risk_escalation_note", "")
        note_low = report_low.consultant_insights.get("time_pressure_insights", {}).get("risk_escalation_note", "")
        assert note_high != note_low, "High and low time pressure should produce different escalation notes"

    def test_report_has_source_attribution(self, agent):
        ctx = agent.build_context(
            industry="manufacturing", years_experience=10, projects_managed=20,
            cultural_region="India", time_pressure="medium",
        )
        report = agent.generate_report(ctx)
        sources = report.consultant_insights.get("sources_used", [])
        assert len(sources) > 0, "Report should include source attribution"

    def test_report_has_black_swan_warning(self, agent):
        ctx = agent.build_context(
            industry="construction", years_experience=8, projects_managed=15,
            cultural_region="Germany", time_pressure="high",
        )
        report = agent.generate_report(ctx)
        black_swan = report.consultant_insights.get("black_swan", {})
        assert "event" in black_swan, "Report should include black swan warning"

    def test_report_has_regulatory_intelligence(self, agent):
        ctx = agent.build_context(
            industry="it", years_experience=6, projects_managed=10,
            cultural_region="Germany", time_pressure="medium",
        )
        report = agent.generate_report(ctx)
        reg_data = report.consultant_insights.get("regulatory_data", {})
        assert "active_regulations" in reg_data, "IT report should include regulatory intelligence"

    def test_report_has_cross_industry_innovations(self, agent):
        ctx = agent.build_context(
            industry="construction", years_experience=8, projects_managed=15,
            cultural_region="Germany", time_pressure="high",
        )
        report = agent.generate_report(ctx)
        innovations = report.consultant_insights.get("innovations", [])
        assert len(innovations) > 0, "Report should include cross-industry innovations"

    def test_context_sensitive_scores_differ_junior_vs_senior(self, agent):
        """Junior PMs have higher internal risk scores (operational blind spots)."""
        ctx_j = agent.build_context(
            industry="manufacturing", years_experience=2, projects_managed=2,
            cultural_region="Germany", time_pressure="medium",
        )
        ctx_s = agent.build_context(
            industry="manufacturing", years_experience=15, projects_managed=30,
            cultural_region="Germany", time_pressure="medium",
        )
        report_j = agent.generate_report(ctx_j)
        report_s = agent.generate_report(ctx_s)
        # Scores should differ — not identical for all profiles
        scores_j = sorted([r.score for r in report_j.risk_register], reverse=True)
        scores_s = sorted([r.score for r in report_s.risk_register], reverse=True)
        assert scores_j != scores_s, "Risk scores should differ between junior and senior profiles"
