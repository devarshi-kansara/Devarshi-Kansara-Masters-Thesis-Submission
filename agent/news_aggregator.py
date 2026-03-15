"""
News aggregator for the risk assessment agent.

Combines news from :class:`~agent.internet_fetcher.InternetDataFetcher` with
simple keyword-based relevance ranking — no third-party NLP libraries required.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agent.internet_fetcher import InternetDataFetcher


@dataclass
class NewsItem:
    """A single aggregated news item with relevance metadata."""

    title: str
    url: str
    date: str
    source: str
    relevance_score: float = 0.0
    extracted_risks: List[str] = field(default_factory=list)


# ── Industry / risk keyword sets ─────────────────────────────────────────────
_RISK_KEYWORDS: Dict[str, List[str]] = {
    "construction": [
        "permit", "soil", "weather", "safety", "delay", "labour", "labor",
        "material", "shortage", "subcontractor", "structural", "foundation",
        "regulation", "inspection", "budget", "cost overrun",
    ],
    "manufacturing": [
        "supply chain", "recall", "equipment", "calibration", "automation",
        "factory", "production", "quality", "defect", "tariff", "import",
        "export", "raw material", "logistics", "shortage",
    ],
    "it": [
        "cybersecurity", "breach", "data", "privacy", "outage", "api",
        "software", "vulnerability", "compliance", "gdpr", "cloud", "ransomware",
        "phishing", "incident", "downtime",
    ],
}

_GENERIC_RISK_KEYWORDS = [
    "risk", "failure", "disruption", "crisis", "incident", "warning",
    "alert", "deadline", "regulation", "compliance", "fine", "penalty",
]


class NewsAggregator:
    """
    Aggregates industry news from multiple live sources and ranks by relevance.

    Parameters
    ----------
    fetcher:
        Optional :class:`~agent.internet_fetcher.InternetDataFetcher` instance.
        If not provided, a default one is created.
    """

    def __init__(self, fetcher: Optional[InternetDataFetcher] = None) -> None:
        self._fetcher = fetcher or InternetDataFetcher()

    # ── Public API ────────────────────────────────────────────────────────────

    def aggregate_industry_news(
        self,
        industry: str,
        top_n: int = 5,
        region: str = "",
    ) -> List[NewsItem]:
        """
        Return up to *top_n* news items relevant to *industry* (and optionally
        *region*), combining live-fetched news and regulatory updates.
        """
        raw_items: List[Dict[str, Any]] = []

        news_data = self._fetcher.fetch_industry_news(industry)
        for item in news_data.get("items", []):
            item["source"] = "Google News"
            raw_items.append(item)

        if region:
            reg_data = self._fetcher.fetch_regulatory_updates(industry, region)
            for item in reg_data.get("items", []):
                if "source" not in item:
                    item["source"] = reg_data.get("sources", ["Regulatory Feed"])[0]
                raw_items.append(item)

        news_items = [
            NewsItem(
                title=i.get("title", ""),
                url=i.get("url", ""),
                date=i.get("date", ""),
                source=i.get("source", "Unknown"),
            )
            for i in raw_items
            if i.get("title")
        ]

        # Rank and deduplicate
        ranked = self.rank_by_relevance(news_items, {"industry": industry, "region": region})

        # Remove articles with zero relevance score to avoid cross-contamination
        relevant = [item for item in ranked if item.relevance_score > 0]
        # Fall back to all ranked items if none matched (e.g. unknown industry)
        if not relevant:
            relevant = ranked

        # Deduplicate by title (case-insensitive)
        seen: set = set()
        unique: List[NewsItem] = []
        for item in relevant:
            key = item.title.lower()
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return unique[:top_n]

    def extract_risk_keywords(self, news_articles: List[NewsItem]) -> List[str]:
        """
        Extract risk-relevant keywords from a list of :class:`NewsItem` titles.

        This is an NLP-free implementation that uses a predefined keyword list
        and simple substring matching.
        """
        found: set = set()
        all_keywords = _GENERIC_RISK_KEYWORDS + [
            kw for kws in _RISK_KEYWORDS.values() for kw in kws
        ]
        for article in news_articles:
            text = article.title.lower()
            for kw in all_keywords:
                if kw in text:
                    found.add(kw)
        return sorted(found)

    def rank_by_relevance(
        self,
        articles: List[NewsItem],
        context: Dict[str, str],
    ) -> List[NewsItem]:
        """
        Rank *articles* by relevance to the given *context* dict.

        Scoring heuristic (higher = more relevant):
        - +2 per industry-specific keyword found in title
        - +1 per generic risk keyword found in title
        - Tie-break: more recent articles first (lexicographic date sort)
        """
        industry = context.get("industry", "").lower()
        industry_kws = _RISK_KEYWORDS.get(industry, [])

        for article in articles:
            text = article.title.lower()
            score = 0.0
            risks: List[str] = []
            for kw in industry_kws:
                if kw in text:
                    score += 2.0
                    risks.append(kw)
            for kw in _GENERIC_RISK_KEYWORDS:
                if kw in text:
                    score += 1.0
                    risks.append(kw)
            article.relevance_score = score
            article.extracted_risks = list(set(risks))

        return sorted(articles, key=lambda a: -a.relevance_score)
