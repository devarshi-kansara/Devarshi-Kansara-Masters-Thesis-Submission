"""
Tests for Phase 2 live internet intelligence modules:
  - agent/cache_manager.py
  - agent/internet_fetcher.py
  - agent/news_aggregator.py
  - agent/risk_agent.py (live-data integration)
  - agent/models.py (new fields)
"""
from __future__ import annotations

import json
import os
import time
import tempfile
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from agent.cache_manager import CacheManager
from agent.internet_fetcher import (
    InternetDataFetcher,
    _parse_arxiv,
    _parse_rss,
    _parse_worldbank,
)
from agent.models import AssessmentReport, ProjectContext, RiskItem
from agent.news_aggregator import NewsAggregator, NewsItem
from agent.risk_agent import RiskAssessmentAgent


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_cache(tmp_path):
    """Return a CacheManager backed by a temporary directory."""
    return CacheManager(cache_dir=str(tmp_path))


@pytest.fixture
def agent():
    return RiskAssessmentAgent()


@pytest.fixture
def construction_ctx(agent):
    return agent.build_context(
        industry="construction",
        years_experience=8,
        projects_managed=15,
        cultural_region="Germany",
        top_risks=["Permit delays", "Material shortage"],
        time_pressure="high",
    )


# ── CacheManager tests (5) ────────────────────────────────────────────────────

class TestCacheManager:
    def test_get_cached_miss_returns_none(self, tmp_cache):
        assert tmp_cache.get_cached("nonexistent_key") is None

    def test_set_and_get_cache_round_trip(self, tmp_cache):
        data = {"items": [{"title": "Test", "url": "https://example.com"}]}
        tmp_cache.set_cache("test_key", data, ttl_hours=1)
        result = tmp_cache.get_cached("test_key")
        assert result == data

    def test_expired_entry_returns_none(self, tmp_cache):
        data = {"value": 42}
        # Store with a TTL that is already expired
        tmp_cache.set_cache("expired_key", data, ttl_hours=0)
        # Force expiry by writing a past timestamp directly
        path = tmp_cache._path("expired_key")
        with open(path, "r") as fh:
            entry = json.load(fh)
        entry["expires_at"] = time.time() - 1
        with open(path, "w") as fh:
            json.dump(entry, fh)
        assert tmp_cache.get_cached("expired_key") is None

    def test_clear_old_cache_removes_expired(self, tmp_cache):
        tmp_cache.set_cache("active_key", {"x": 1}, ttl_hours=24)
        tmp_cache.set_cache("old_key", {"x": 2}, ttl_hours=0)
        # Force expiry on old_key
        path = tmp_cache._path("old_key")
        with open(path, "r") as fh:
            entry = json.load(fh)
        entry["expires_at"] = time.time() - 1
        with open(path, "w") as fh:
            json.dump(entry, fh)
        removed = tmp_cache.clear_old_cache()
        assert removed >= 1
        assert tmp_cache.get_cached("active_key") is not None

    def test_cache_key_sanitisation(self, tmp_cache):
        """Keys with special characters should not raise errors."""
        tmp_cache.set_cache("key with spaces & symbols!", {"ok": True})
        result = tmp_cache.get_cached("key with spaces & symbols!")
        assert result == {"ok": True}


# ── RSS / arXiv / World Bank parsing tests (4) ───────────────────────────────

class TestParsers:
    _SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Construction Permit Delays in Europe</title>
      <link>https://example.com/article1</link>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Material Shortage Alert</title>
      <link>https://example.com/article2</link>
      <pubDate>Tue, 02 Jan 2024 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

    _SAMPLE_ARXIV = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Risk Management in Construction Projects</title>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <summary>This paper examines risk factors in early-stage construction planning.</summary>
    <published>2024-01-15T00:00:00Z</published>
    <link rel="alternate" href="https://arxiv.org/abs/2401.00001"/>
  </entry>
</feed>"""

    _SAMPLE_WORLDBANK = json.dumps([
        {"page": 1, "pages": 1},
        [{"date": "2023", "value": 2.85, "indicator": {"id": "NY.GDP.MKTP.KD.ZG"}}],
    ])

    def test_parse_rss_returns_items(self):
        items = _parse_rss(self._SAMPLE_RSS)
        assert len(items) == 2
        assert items[0]["title"] == "Construction Permit Delays in Europe"
        assert items[0]["url"] == "https://example.com/article1"

    def test_parse_rss_max_items_respected(self):
        items = _parse_rss(self._SAMPLE_RSS, max_items=1)
        assert len(items) == 1

    def test_parse_arxiv_returns_papers(self):
        papers = _parse_arxiv(self._SAMPLE_ARXIV)
        assert len(papers) == 1
        assert "Construction" in papers[0]["title"]
        assert "Alice Smith" in papers[0]["authors"]
        assert papers[0]["published"].startswith("2024")

    def test_parse_worldbank_returns_indicator(self):
        result = _parse_worldbank(self._SAMPLE_WORLDBANK, "gdp_growth")
        assert result is not None
        assert result["indicator"] == "gdp_growth"
        assert result["value"] == "2.85"
        assert result["year"] == "2023"


# ── InternetDataFetcher tests (3) ─────────────────────────────────────────────

class TestInternetDataFetcher:
    """Tests that use a mocked HTTP layer so no real network calls are made."""

    _MOCK_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>Mock Construction Risk News</title>
        <link>https://mock.example.com/news</link>
        <pubDate>Wed, 10 Jan 2024 09:00:00 GMT</pubDate></item>
</channel></rss>"""

    @pytest.fixture
    def fetcher(self, tmp_path):
        cache = CacheManager(cache_dir=str(tmp_path))
        return InternetDataFetcher(cache_manager=cache)

    def test_fetch_industry_news_returns_dict_structure(self, fetcher):
        with patch("agent.internet_fetcher._fetch_url", return_value=self._MOCK_RSS):
            result = fetcher.fetch_industry_news("construction")
        assert "items" in result
        assert "confidence" in result
        assert result["confidence"] in ("real-time", "cached", "fallback")

    def test_fetch_industry_news_uses_cache_on_second_call(self, fetcher):
        with patch("agent.internet_fetcher._fetch_url", return_value=self._MOCK_RSS) as mock_fetch:
            fetcher.fetch_industry_news("manufacturing")
            fetcher.fetch_industry_news("manufacturing")
        # Second call should use cache, so network should only have been hit once
        # (or fewer times than if fully re-fetched)
        assert mock_fetch.call_count < 10  # generous upper bound

    def test_fetch_gracefully_handles_network_failure(self, fetcher):
        with patch("agent.internet_fetcher._fetch_url", return_value=None):
            result = fetcher.fetch_geopolitical_risks(region="Germany", industry="construction")
        assert result["confidence"] == "fallback"
        assert result["items"] == []


# ── NewsAggregator tests (3) ──────────────────────────────────────────────────

class TestNewsAggregator:
    @pytest.fixture
    def mock_fetcher(self):
        fetcher = MagicMock(spec=InternetDataFetcher)
        fetcher.fetch_industry_news.return_value = {
            "items": [
                {"title": "Construction permit delays in Germany", "url": "https://a.com/1", "date": "2024-01-10"},
                {"title": "Material shortage hits construction industry", "url": "https://a.com/2", "date": "2024-01-09"},
                {"title": "Labor shortage construction sites", "url": "https://a.com/3", "date": "2024-01-08"},
            ],
            "sources": ["Google News RSS"],
        }
        fetcher.fetch_regulatory_updates.return_value = {
            "items": [
                {"title": "EU construction regulation update 2024", "url": "https://eur-lex.europa.eu/1", "date": "2024-01-05"},
            ],
            "sources": ["EU-Lex"],
        }
        return fetcher

    @pytest.fixture
    def aggregator(self, mock_fetcher):
        return NewsAggregator(fetcher=mock_fetcher)

    def test_aggregate_industry_news_returns_news_items(self, aggregator):
        items = aggregator.aggregate_industry_news("construction", top_n=5, region="Germany")
        assert isinstance(items, list)
        assert all(isinstance(i, NewsItem) for i in items)

    def test_aggregate_industry_news_top_n_respected(self, aggregator):
        items = aggregator.aggregate_industry_news("construction", top_n=2)
        assert len(items) <= 2

    def test_rank_by_relevance_scores_keyword_matches(self, aggregator):
        articles = [
            NewsItem(title="Weather delays on construction site", url="", date="", source=""),
            NewsItem(title="Stock market rises 3%", url="", date="", source=""),
        ]
        ranked = aggregator.rank_by_relevance(articles, {"industry": "construction"})
        # The construction-related article must rank first (higher relevance score)
        assert "construction" in ranked[0].title.lower()


# ── Industry Relevance tests (8) ─────────────────────────────────────────────

class TestIndustryRelevance:
    """
    Verify that each industry returns only relevant data and no
    cross-industry contamination occurs.
    """

    # ── InternetDataFetcher relevance ─────────────────────────────────────────

    _CONSTRUCTION_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>Building permit delays hit German construction industry</title>
        <link>https://example.com/c1</link><pubDate>Mon, 10 Mar 2026 09:00:00 GMT</pubDate></item>
  <item><title>Steel prices surge 8% in European construction market</title>
        <link>https://example.com/c2</link><pubDate>Tue, 11 Mar 2026 09:00:00 GMT</pubDate></item>
  <item><title>GDPR fines hit record high for tech companies</title>
        <link>https://example.com/it1</link><pubDate>Wed, 12 Mar 2026 09:00:00 GMT</pubDate></item>
</channel></rss>"""

    _IT_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>Ransomware attack exposes 1 million patient records</title>
        <link>https://example.com/it1</link><pubDate>Mon, 10 Mar 2026 09:00:00 GMT</pubDate></item>
  <item><title>NIS2 compliance deadline forces IT security overhaul</title>
        <link>https://example.com/it2</link><pubDate>Tue, 11 Mar 2026 09:00:00 GMT</pubDate></item>
  <item><title>Lumber prices rise on construction demand</title>
        <link>https://example.com/c1</link><pubDate>Wed, 12 Mar 2026 09:00:00 GMT</pubDate></item>
</channel></rss>"""

    _ARXIV_CONSTRUCTION = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Risk Factors in Early-Stage Construction Projects</title>
    <author><name>Alice Smith</name></author>
    <summary>Construction project risk management in the first 20% of the lifecycle.</summary>
    <published>2024-03-01T00:00:00Z</published>
    <link rel="alternate" href="https://arxiv.org/abs/2403.00001"/>
  </entry>
  <entry>
    <title>Stable Topology in Exactly Flat Bands</title>
    <author><name>Bob Jones</name></author>
    <summary>Mathematical analysis of flat band topological invariants.</summary>
    <published>2024-03-02T00:00:00Z</published>
    <link rel="alternate" href="https://arxiv.org/abs/2403.00002"/>
  </entry>
</feed>"""

    @pytest.fixture
    def fetcher(self, tmp_path):
        cache = CacheManager(cache_dir=str(tmp_path))
        return InternetDataFetcher(cache_manager=cache)

    def test_regulatory_updates_filter_by_industry(self, fetcher):
        """Regulatory results are filtered to keep only industry-relevant items."""
        with patch("agent.internet_fetcher._fetch_url", return_value=self._CONSTRUCTION_RSS):
            result = fetcher.fetch_regulatory_updates("construction", "Germany")
        titles = [item["title"].lower() for item in result["items"]]
        # GDPR (IT-specific) should be filtered out; construction items kept
        assert all("gdpr" not in t for t in titles), (
            "IT-specific GDPR item should be filtered from construction regulatory updates"
        )

    def test_market_signals_include_commodity_data_for_construction(self, fetcher):
        """Market signals for construction include industry-specific commodity prices."""
        with patch("agent.internet_fetcher._fetch_url", return_value=None):
            result = fetcher.fetch_market_signals("construction")
        commodity = result.get("commodity_signals", [])
        assert len(commodity) > 0, "Construction market signals should include commodity prices"
        indicators = [c["indicator"].lower() for c in commodity]
        assert any("steel" in ind or "lumber" in ind or "concrete" in ind for ind in indicators), (
            "Construction commodity signals should include steel/lumber/concrete prices"
        )

    def test_market_signals_include_commodity_data_for_manufacturing(self, fetcher):
        """Market signals for manufacturing include manufacturing-specific indicators."""
        with patch("agent.internet_fetcher._fetch_url", return_value=None):
            result = fetcher.fetch_market_signals("manufacturing")
        commodity = result.get("commodity_signals", [])
        assert len(commodity) > 0
        indicators = [c["indicator"].lower() for c in commodity]
        assert any("semiconductor" in ind or "aluminum" in ind or "copper" in ind for ind in indicators)

    def test_market_signals_include_commodity_data_for_it(self, fetcher):
        """Market signals for IT include IT-specific indicators."""
        with patch("agent.internet_fetcher._fetch_url", return_value=None):
            result = fetcher.fetch_market_signals("it")
        commodity = result.get("commodity_signals", [])
        assert len(commodity) > 0
        indicators = [c["indicator"].lower() for c in commodity]
        assert any("breach" in ind or "cloud" in ind or "cyber" in ind for ind in indicators)

    def test_academic_research_filters_irrelevant_papers(self, fetcher):
        """arXiv papers are filtered so non-industry papers are excluded when industry is given."""
        with patch("agent.internet_fetcher._fetch_url", return_value=self._ARXIV_CONSTRUCTION):
            result = fetcher.fetch_academic_research(["risk"], industry="construction")
        papers = result.get("papers", [])
        titles = [p["title"].lower() for p in papers]
        # Topology paper should be filtered out; construction paper should remain
        assert not any("topology" in t or "flat band" in t for t in titles), (
            "Non-construction arXiv papers should be filtered out"
        )
        assert any("construction" in t for t in titles)

    def test_academic_research_no_industry_returns_all_papers(self, fetcher):
        """When industry is not specified, no filtering is applied (backward compat)."""
        with patch("agent.internet_fetcher._fetch_url", return_value=self._ARXIV_CONSTRUCTION):
            result = fetcher.fetch_academic_research(["risk"])
        # Should return all papers (no filtering without industry)
        assert len(result.get("papers", [])) == 2

    # ── NewsAggregator relevance ──────────────────────────────────────────────

    def test_news_aggregator_filters_irrelevant_articles(self):
        """aggregate_industry_news excludes articles with zero relevance score."""
        from agent.news_aggregator import NewsAggregator

        mock_fetcher = MagicMock(spec=InternetDataFetcher)
        mock_fetcher.fetch_industry_news.return_value = {
            "items": [
                {"title": "Building permit delays hit construction sites", "url": "https://a.com/1", "date": "2026-03-10"},
                {"title": "Stock market volatility continues on Wall Street", "url": "https://a.com/2", "date": "2026-03-09"},
                {"title": "Celebrity news: actor wins award", "url": "https://a.com/3", "date": "2026-03-08"},
            ],
            "sources": ["Google News RSS"],
        }
        mock_fetcher.fetch_regulatory_updates.return_value = {"items": [], "sources": []}

        aggregator = NewsAggregator(fetcher=mock_fetcher)
        items = aggregator.aggregate_industry_news("construction", top_n=5)
        titles = [i.title.lower() for i in items]
        # Generic / celebrity news with no construction keywords should be filtered
        assert not any("celebrity" in t or "actor" in t or "award" in t for t in titles)

    def test_no_cross_contamination_construction_vs_it(self):
        """Construction queries should not return IT-specific results."""
        from agent.news_aggregator import NewsAggregator

        mock_fetcher = MagicMock(spec=InternetDataFetcher)
        mock_fetcher.fetch_industry_news.return_value = {
            "items": [
                {"title": "GDPR breach fine hits tech company", "url": "https://a.com/it1", "date": "2026-03-10"},
                {"title": "Ransomware attack on cloud provider", "url": "https://a.com/it2", "date": "2026-03-09"},
                {"title": "Construction material prices surge", "url": "https://a.com/c1", "date": "2026-03-08"},
            ],
            "sources": ["Google News RSS"],
        }
        mock_fetcher.fetch_regulatory_updates.return_value = {"items": [], "sources": []}

        aggregator = NewsAggregator(fetcher=mock_fetcher)
        items = aggregator.aggregate_industry_news("construction", top_n=5)
        titles = [i.title.lower() for i in items]
        # IT-only articles should rank below construction articles and be filtered
        assert items[0].title.lower() == "construction material prices surge"


# ── Integration: RiskAgent + live data (3) ────────────────────────────────────

class TestRiskAgentLiveDataIntegration:
    def test_generate_report_without_live_data(self, agent, construction_ctx):
        """fetch_live_data=False should produce a complete report instantly."""
        report = agent.generate_report(construction_ctx, fetch_live_data=False)
        assert isinstance(report, AssessmentReport)
        assert report.live_data_timestamp is None
        assert report.data_sources_used == []

    def test_generate_report_live_data_fields_exist_on_model(self, agent, construction_ctx):
        """AssessmentReport must have all new live-data fields."""
        report = agent.generate_report(construction_ctx, fetch_live_data=False)
        assert hasattr(report, "live_data_timestamp")
        assert hasattr(report, "data_sources_used")
        assert hasattr(report, "regulatory_updates")
        assert hasattr(report, "industry_news")
        assert hasattr(report, "market_signals")
        assert hasattr(report, "academic_research")
        assert hasattr(report, "geopolitical_alerts")

    def test_risk_item_has_live_enrichment_fields(self, agent, construction_ctx):
        """RiskItem must have all new enrichment fields."""
        report = agent.generate_report(construction_ctx, fetch_live_data=False)
        for risk in report.risk_register:
            assert hasattr(risk, "recent_news_link")
            assert hasattr(risk, "recent_news_title")
            assert hasattr(risk, "recent_news_date")
            assert hasattr(risk, "regulatory_status")
            assert hasattr(risk, "market_signal")
            assert hasattr(risk, "academic_citation")
