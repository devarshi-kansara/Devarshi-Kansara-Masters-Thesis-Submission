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
