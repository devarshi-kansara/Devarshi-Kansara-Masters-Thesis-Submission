"""
Consultant-style report generator for the risk assessment agent.

Orchestrates the ContextAnalyzer, ResearchEngine, FrameworkRecommender,
and DataFetcher to produce narrative-driven, benchmark-enriched,
academically-referenced risk assessment insights.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from agent.context_analyzer import ContextAnalyzer
from agent.data_fetcher import DataFetcher
from agent.framework_recommender import FrameworkRecommender
from agent.research_engine import ResearchEngine

if TYPE_CHECKING:
    from agent.models import AssessmentReport, ProjectContext


class ConsultantReportGenerator:
    """
    Generates consultant-style, benchmark-driven, academically-referenced
    insight layers that enrich the core AssessmentReport.
    """

    def __init__(self, use_live_data: bool = False) -> None:
        self._context_analyzer = ContextAnalyzer()
        self._research_engine = ResearchEngine()
        self._framework_recommender = FrameworkRecommender()
        self._data_fetcher = DataFetcher(use_live_data=use_live_data)

    def generate(self, report: "AssessmentReport") -> dict:
        """
        Generate the full consultant insights layer for an AssessmentReport.

        Returns a dict with keys:
            context_analysis, frameworks, enriched_risks, industry_reports,
            innovations, black_swan, regulatory_data, market_signals,
            sources_used, data_freshness
        """
        ctx = report.context

        context_analysis = self._context_analyzer.analyze(ctx)
        frameworks = self._framework_recommender.recommend(ctx)
        industry_reports = self._research_engine.get_industry_reports(ctx.industry)
        innovations = self._research_engine.get_cross_industry_innovations(ctx.industry)
        black_swan = self._research_engine.get_black_swan_warning(ctx.industry, ctx.time_pressure)
        regulatory_data = self._data_fetcher.get_regulatory_data(ctx.industry)
        market_signals = self._data_fetcher.get_market_signals(ctx.industry)
        data_freshness = self._data_fetcher.get_data_freshness(ctx.industry)

        enriched_risks = self._enrich_risk_register(report, ctx, context_analysis)

        sources_used = self._compile_sources(ctx, industry_reports, data_freshness)

        return {
            "context_analysis": context_analysis,
            "frameworks": frameworks,
            "enriched_risks": enriched_risks,
            "industry_reports": industry_reports,
            "innovations": innovations,
            "black_swan": black_swan,
            "regulatory_data": regulatory_data,
            "market_signals": market_signals,
            "sources_used": sources_used,
            "data_freshness": data_freshness,
            "persona": context_analysis.get("persona", {}),
            "benchmarks": context_analysis.get("benchmarks", {}),
            "time_pressure_insights": context_analysis.get("time_pressure_insights", {}),
            "decision_style_insights": context_analysis.get("decision_style_insights", {}),
            "confidence": context_analysis.get("confidence_level", {}),
        }

    def _enrich_risk_register(
        self,
        report: "AssessmentReport",
        ctx: "ProjectContext",
        context_analysis: dict,
    ) -> list:
        """Enrich each risk in the register with citations and context notes."""
        enriched = []
        benchmarks = context_analysis.get("benchmarks", {})
        persona = context_analysis.get("persona", {})

        for risk in report.risk_register:
            citations = self._research_engine.get_citations_for_risk(
                risk.description, ctx.industry, ctx.experience_level
            )
            context_note = self._build_risk_context_note(risk, ctx, benchmarks, persona)
            enriched.append({
                "risk": risk,
                "citations": citations,
                "context_note": context_note,
            })
        return enriched

    def _build_risk_context_note(
        self, risk, ctx: "ProjectContext", benchmarks: dict, persona: dict
    ) -> str:
        """Build a personalised context note for a single risk item."""
        notes = []

        # Benchmark match
        common_risks_pct = benchmarks.get("common_risks_pct", {})
        risk_lower = risk.description.lower()
        for bench_desc, pct in common_risks_pct.items():
            # Match on any of the first 3 significant words
            words = [w for w in bench_desc.lower().split() if len(w) > 3][:3]
            if words and any(w in risk_lower for w in words):
                notes.append(f"{pct}% of PMs in your industry+region face this risk.")
                break

        # Persona blind spot match
        blind_spots = persona.get("risk_blind_spots", [])
        for bs in blind_spots:
            bs_words = [w for w in bs.lower().split() if len(w) > 4][:4]
            if bs_words and any(w in risk_lower for w in bs_words):
                notes.append(f"Profile blind spot: {bs}")
                break

        return " | ".join(notes) if notes else ""

    def _compile_sources(
        self, ctx: "ProjectContext", industry_reports: list, data_freshness: dict
    ) -> list:
        """Compile the complete list of sources used in this report."""
        sources = [
            "Thesis knowledge base (Kansara, HDBW 2026) — core industry risk frameworks",
            "PMI PMBOK 7th Edition (2021) — risk management processes",
            "ISO 31000:2018 — risk management guidelines",
        ]

        for rep in industry_reports[:2]:
            sources.append(f"{rep['title']} — {rep['publisher']}")

        if ctx.cultural_region in ("process_guardian", "resource_navigator"):
            sources.append("Hofstede et al. (2010) — Cultural Dimensions in Risk Perception")
            sources.append("GLOBE Study (2004) — Cross-Cultural Risk Communication Styles")

        sources.append(
            f"Regulatory intelligence: {data_freshness.get('data_source', 'Curated knowledge base')} "
            f"(updated {data_freshness.get('last_updated', '2026-01')})"
        )

        return sources
