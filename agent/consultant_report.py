"""
Consultant Report Generator — Phase 1 specialist module.

Orchestrates the Phase 1 specialist modules (ContextAnalyzer,
FrameworkRecommender, DataFetcher, ResearchEngine) and combines their
output into a single ``consultant_insights`` dict that :mod:`app` can
render as an industry-specific "Consultant Insights" section.
"""
from __future__ import annotations

from agent.context_analyzer import ContextAnalyzer
from agent.data_fetcher import DataFetcher
from agent.framework_recommender import FrameworkRecommender
from agent.models import AssessmentReport, ProjectContext
from agent.research_engine import ResearchEngine


class ConsultantReportGenerator:
    """
    Generates a consultant-style enrichment layer on top of the base
    :class:`~agent.models.AssessmentReport`.

    Usage::

        gen = ConsultantReportGenerator()
        insights = gen.generate(ctx, report)

    The returned dict contains the following keys:

    ``persona_analysis``
        Deep persona profile (archetype, strengths, blind spots, decision
        pattern, risk tolerance, optional time-pressure note).

    ``industry_benchmarks``
        Dictionary of benchmark data keyed by risk category label.

    ``blind_spots``
        Combined list of profile- and industry-specific blind spots.

    ``recommended_frameworks``
        List of framework dicts enriched with personalised ``rationale``
        and ``blind_spot_addressed`` keys.

    ``black_swan_warnings``
        Low-probability, high-impact warnings for the industry.

    ``regulatory_intelligence``
        Key regulatory obligations active for this industry.

    ``market_signals``
        Current market conditions relevant to the project.

    ``research_citations``
        APA-formatted citations supporting the assessment.

    ``cross_industry_insights``
        Patterns borrowed from adjacent industries that apply here.
    """

    def __init__(self) -> None:
        self._context_analyzer = ContextAnalyzer()
        self._framework_recommender = FrameworkRecommender()
        self._data_fetcher = DataFetcher()
        self._research_engine = ResearchEngine()

    def generate(self, ctx: ProjectContext, report: AssessmentReport) -> dict:
        """
        Produce the full consultant insights dict.

        :param ctx: The project context built by
            :meth:`~agent.risk_agent.RiskAssessmentAgent.build_context`.
        :param report: The base assessment report produced by
            :meth:`~agent.risk_agent.RiskAssessmentAgent.generate_report`.
        :returns: A dict with all consultant insight keys (see class docstring).
        """
        persona_analysis = self._context_analyzer.get_persona_profile(ctx)
        benchmarks = self._context_analyzer.get_benchmarks(ctx)
        blind_spots = self._context_analyzer.get_blind_spots(ctx)
        recommended_frameworks = self._framework_recommender.recommend_frameworks(
            ctx, report.risk_register
        )
        black_swan_warnings = self._data_fetcher.get_black_swan_warnings(ctx)
        regulatory_intelligence = self._data_fetcher.get_regulatory_intel(ctx)
        market_signals = self._data_fetcher.get_market_signals(ctx)
        research_citations = self._research_engine.get_citations(ctx)
        cross_industry_insights = self._research_engine.get_cross_industry_insights(ctx)

        return {
            "persona_analysis": persona_analysis,
            "industry_benchmarks": benchmarks,
            "blind_spots": blind_spots,
            "recommended_frameworks": recommended_frameworks,
            "black_swan_warnings": black_swan_warnings,
            "regulatory_intelligence": regulatory_intelligence,
            "market_signals": market_signals,
            "research_citations": research_citations,
            "cross_industry_insights": cross_industry_insights,
        }
