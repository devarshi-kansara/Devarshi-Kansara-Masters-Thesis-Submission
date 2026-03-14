"""Tests for Phase 1 specialist modules."""
from __future__ import annotations

import pytest

from agent.context_analyzer import ContextAnalyzer
from agent.consultant_report import ConsultantReportGenerator
from agent.data_fetcher import DataFetcher
from agent.framework_recommender import FrameworkRecommender
from agent.models import ProjectContext, RiskItem
from agent.research_engine import ResearchEngine
from agent.risk_agent import RiskAssessmentAgent


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def agent() -> RiskAssessmentAgent:
    return RiskAssessmentAgent()


@pytest.fixture
def construction_ctx(agent: RiskAssessmentAgent) -> ProjectContext:
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
def manufacturing_ctx(agent: RiskAssessmentAgent) -> ProjectContext:
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
def it_ctx(agent: RiskAssessmentAgent) -> ProjectContext:
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


# ── ContextAnalyzer tests ─────────────────────────────────────────────────────

class TestContextAnalyzer:
    def test_persona_profile_process_guardian_mid(self, construction_ctx: ProjectContext):
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(construction_ctx)
        assert "archetype" in profile
        assert "Process Guardian" in profile["archetype"]
        assert isinstance(profile["strengths"], list)
        assert len(profile["strengths"]) > 0
        assert isinstance(profile["blind_spots"], list)
        assert len(profile["blind_spots"]) > 0

    def test_persona_profile_resource_navigator_senior(self, manufacturing_ctx: ProjectContext):
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(manufacturing_ctx)
        assert "Resource Navigator" in profile["archetype"]

    def test_persona_profile_time_pressure_note(self, construction_ctx: ProjectContext):
        """High time pressure context should include a time_pressure_note."""
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(construction_ctx)
        assert "time_pressure_note" in profile
        assert "High time pressure" in profile["time_pressure_note"]

    def test_persona_profile_no_time_pressure_note_for_low_pressure(
        self, manufacturing_ctx: ProjectContext
    ):
        """Medium time pressure context should NOT include a time_pressure_note."""
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(manufacturing_ctx)
        assert "time_pressure_note" not in profile

    def test_persona_profile_fallback_for_mixed_region(self, it_ctx: ProjectContext):
        """Unknown/mixed region should return the default Balanced Practitioner profile."""
        analyzer = ContextAnalyzer()
        profile = analyzer.get_persona_profile(it_ctx)
        assert "archetype" in profile

    def test_benchmarks_returns_construction_data(self, construction_ctx: ProjectContext):
        analyzer = ContextAnalyzer()
        benchmarks = analyzer.get_benchmarks(construction_ctx)
        assert isinstance(benchmarks, dict)
        assert len(benchmarks) > 0
        first_item = next(iter(benchmarks.values()))
        assert "frequency" in first_item
        assert "success_rate" in first_item

    def test_benchmarks_differ_by_industry(
        self, construction_ctx: ProjectContext, manufacturing_ctx: ProjectContext
    ):
        analyzer = ContextAnalyzer()
        c_benchmarks = analyzer.get_benchmarks(construction_ctx)
        m_benchmarks = analyzer.get_benchmarks(manufacturing_ctx)
        assert c_benchmarks != m_benchmarks

    def test_blind_spots_includes_profile_and_industry(
        self, construction_ctx: ProjectContext
    ):
        analyzer = ContextAnalyzer()
        blind_spots = analyzer.get_blind_spots(construction_ctx)
        assert isinstance(blind_spots, list)
        assert len(blind_spots) >= 2

    def test_blind_spots_differ_by_region(
        self, construction_ctx: ProjectContext, manufacturing_ctx: ProjectContext
    ):
        analyzer = ContextAnalyzer()
        # Different industries → different blind spots even if structure is similar
        c_spots = analyzer.get_blind_spots(construction_ctx)
        m_spots = analyzer.get_blind_spots(manufacturing_ctx)
        assert c_spots != m_spots


# ── ResearchEngine tests ──────────────────────────────────────────────────────

class TestResearchEngine:
    def test_citations_returns_list(self, construction_ctx: ProjectContext):
        engine = ResearchEngine()
        citations = engine.get_citations(construction_ctx)
        assert isinstance(citations, list)
        assert len(citations) > 0

    def test_citations_are_strings(self, construction_ctx: ProjectContext):
        engine = ResearchEngine()
        citations = engine.get_citations(construction_ctx)
        assert all(isinstance(c, str) for c in citations)

    def test_citations_include_general_references(self, it_ctx: ProjectContext):
        engine = ResearchEngine()
        citations = engine.get_citations(it_ctx)
        combined = " ".join(citations)
        assert "Kahneman" in combined or "Klein" in combined or "Taleb" in combined

    def test_citations_differ_by_industry(
        self, construction_ctx: ProjectContext, it_ctx: ProjectContext
    ):
        engine = ResearchEngine()
        c_cites = engine.get_citations(construction_ctx)
        i_cites = engine.get_citations(it_ctx)
        # Industry-specific citations should differ
        assert c_cites != i_cites

    def test_cross_industry_insights_returns_list(self, construction_ctx: ProjectContext):
        engine = ResearchEngine()
        insights = engine.get_cross_industry_insights(construction_ctx)
        assert isinstance(insights, list)
        assert len(insights) > 0

    def test_cross_industry_insights_differ_by_industry(
        self, construction_ctx: ProjectContext, manufacturing_ctx: ProjectContext
    ):
        engine = ResearchEngine()
        c_insights = engine.get_cross_industry_insights(construction_ctx)
        m_insights = engine.get_cross_industry_insights(manufacturing_ctx)
        assert c_insights != m_insights


# ── FrameworkRecommender tests ────────────────────────────────────────────────

class TestFrameworkRecommender:
    def test_recommender_returns_list(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        risks: list = []
        result = recommender.recommend_frameworks(construction_ctx, risks)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_safety_premium_always_included(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(construction_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Safety Premium" in names

    def test_two_way_team_model_always_included(self, manufacturing_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(manufacturing_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Two-Way Team Model" in names

    def test_somatic_verification_for_construction(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(construction_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Somatic Verification" in names

    def test_truth_link_for_manufacturing(self, manufacturing_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(manufacturing_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Truth-Link Technology" in names

    def test_truth_link_for_it(self, it_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(it_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Truth-Link Technology" in names

    def test_reverse_training_for_process_guardian(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(construction_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Reverse Training" in names

    def test_reverse_training_for_resource_navigator(self, manufacturing_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(manufacturing_ctx, [])
        names = [fw["name"] for fw in result]
        assert "Reverse Training" in names

    def test_rationale_present_on_all_frameworks(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(construction_ctx, [])
        for fw in result:
            assert "rationale" in fw, f"Missing 'rationale' in framework: {fw['name']}"
            assert fw["rationale"].strip() != ""

    def test_blind_spot_addressed_present(self, construction_ctx: ProjectContext):
        recommender = FrameworkRecommender()
        result = recommender.recommend_frameworks(construction_ctx, [])
        for fw in result:
            assert "blind_spot_addressed" in fw, (
                f"Missing 'blind_spot_addressed' in framework: {fw['name']}"
            )

    def test_frameworks_differ_by_industry(
        self, construction_ctx: ProjectContext, it_ctx: ProjectContext
    ):
        recommender = FrameworkRecommender()
        c_result = recommender.recommend_frameworks(construction_ctx, [])
        i_result = recommender.recommend_frameworks(it_ctx, [])
        c_names = {fw["name"] for fw in c_result}
        i_names = {fw["name"] for fw in i_result}
        # At least one difference (e.g. Somatic Verification vs Truth-Link)
        assert c_names != i_names


# ── DataFetcher tests ─────────────────────────────────────────────────────────

class TestDataFetcher:
    def test_regulatory_intel_returns_list(self, construction_ctx: ProjectContext):
        fetcher = DataFetcher()
        result = fetcher.get_regulatory_intel(construction_ctx)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_market_signals_returns_list(self, manufacturing_ctx: ProjectContext):
        fetcher = DataFetcher()
        result = fetcher.get_market_signals(manufacturing_ctx)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_black_swan_warnings_returns_list(self, it_ctx: ProjectContext):
        fetcher = DataFetcher()
        result = fetcher.get_black_swan_warnings(it_ctx)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_regulatory_intel_differs_by_industry(
        self, construction_ctx: ProjectContext, manufacturing_ctx: ProjectContext
    ):
        fetcher = DataFetcher()
        c_intel = fetcher.get_regulatory_intel(construction_ctx)
        m_intel = fetcher.get_regulatory_intel(manufacturing_ctx)
        assert c_intel != m_intel

    def test_black_swans_are_strings(self, construction_ctx: ProjectContext):
        fetcher = DataFetcher()
        warnings = fetcher.get_black_swan_warnings(construction_ctx)
        assert all(isinstance(w, str) for w in warnings)


# ── ConsultantReportGenerator tests ──────────────────────────────────────────

class TestConsultantReportGenerator:
    @pytest.fixture
    def construction_report(self, agent: RiskAssessmentAgent, construction_ctx: ProjectContext):
        return agent.generate_report(construction_ctx)

    @pytest.fixture
    def manufacturing_report(self, agent: RiskAssessmentAgent, manufacturing_ctx: ProjectContext):
        return agent.generate_report(manufacturing_ctx)

    @pytest.fixture
    def it_report(self, agent: RiskAssessmentAgent, it_ctx: ProjectContext):
        return agent.generate_report(it_ctx)

    def test_generate_returns_dict(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights, dict)

    def test_generate_has_all_expected_keys(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        expected_keys = {
            "persona_analysis",
            "industry_benchmarks",
            "blind_spots",
            "recommended_frameworks",
            "black_swan_warnings",
            "regulatory_intelligence",
            "market_signals",
            "research_citations",
            "cross_industry_insights",
        }
        assert expected_keys.issubset(insights.keys())

    def test_persona_analysis_is_dict(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["persona_analysis"], dict)
        assert "archetype" in insights["persona_analysis"]

    def test_industry_benchmarks_is_dict(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["industry_benchmarks"], dict)

    def test_blind_spots_is_non_empty_list(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["blind_spots"], list)
        assert len(insights["blind_spots"]) > 0

    def test_recommended_frameworks_is_non_empty_list(
        self, construction_ctx, construction_report
    ):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["recommended_frameworks"], list)
        assert len(insights["recommended_frameworks"]) > 0

    def test_research_citations_present(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["research_citations"], list)
        assert len(insights["research_citations"]) > 0

    def test_black_swan_warnings_present(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["black_swan_warnings"], list)
        assert len(insights["black_swan_warnings"]) > 0

    def test_insights_differ_by_industry(
        self,
        construction_ctx, construction_report,
        manufacturing_ctx, manufacturing_report,
    ):
        """Construction and Manufacturing should produce different consultant insights."""
        gen = ConsultantReportGenerator()
        c_insights = gen.generate(construction_ctx, construction_report)
        m_insights = gen.generate(manufacturing_ctx, manufacturing_report)
        assert (
            c_insights["persona_analysis"] != m_insights["persona_analysis"]
        ), "Persona analysis should differ by cultural region / experience level"
        assert (
            c_insights["industry_benchmarks"] != m_insights["industry_benchmarks"]
        ), "Industry benchmarks should differ by industry"
        assert (
            c_insights["regulatory_intelligence"] != m_insights["regulatory_intelligence"]
        ), "Regulatory intelligence should differ by industry"

    def test_insights_differ_for_german_vs_indian_pm(
        self, agent: RiskAssessmentAgent
    ):
        """German PM should get different persona analysis than Indian PM."""
        german_ctx = agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="Germany",
            time_pressure="medium",
        )
        indian_ctx = agent.build_context(
            industry="construction",
            years_experience=8,
            projects_managed=15,
            cultural_region="India",
            time_pressure="medium",
        )
        gen = ConsultantReportGenerator()
        german_report = agent.generate_report(german_ctx)
        indian_report = agent.generate_report(indian_ctx)
        german_insights = gen.generate(german_ctx, german_report)
        indian_insights = gen.generate(indian_ctx, indian_report)
        assert (
            german_insights["persona_analysis"]["archetype"]
            != indian_insights["persona_analysis"]["archetype"]
        )

    def test_cross_industry_insights_present(self, construction_ctx, construction_report):
        gen = ConsultantReportGenerator()
        insights = gen.generate(construction_ctx, construction_report)
        assert isinstance(insights["cross_industry_insights"], list)
        assert len(insights["cross_industry_insights"]) > 0
