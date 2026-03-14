"""
Live internet data fetcher for the risk assessment agent.

Pulls from free, no-auth-required public APIs:
  - Google News RSS      (industry news)
  - EU-Lex RSS           (EU regulatory updates)
  - FDA OpenData RSS     (FDA safety alerts)
  - arXiv API            (academic research)
  - World Bank API       (macro / geopolitical indicators)

All responses are cached for 24 hours via :class:`~agent.cache_manager.CacheManager`
to stay within free-tier rate limits.  Every method gracefully degrades to an
empty list / dict if a network call fails, so the app never crashes.
"""
from __future__ import annotations

import logging
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from agent.cache_manager import CacheManager

logger = logging.getLogger(__name__)

# ── RSS / API endpoints ───────────────────────────────────────────────────────
_GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
_EULEX_RSS = (
    "https://eur-lex.europa.eu/RSSLINK.do?what=EM"
    "&type=general&language=EN&resetNewId=true"
)
_FDA_RSS = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml"
_ARXIV_API = "https://export.arxiv.org/api/query?search_query={query}&max_results={n}&sortBy=lastUpdatedDate&sortOrder=descending"
_WORLDBANK_API = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv=1"

# ── Industry → search queries ─────────────────────────────────────────────────
_INDUSTRY_NEWS_QUERIES: Dict[str, List[str]] = {
    "construction": [
        "construction industry risks",
        "building permits construction",
        "material shortage construction",
        "labor shortage construction",
    ],
    "manufacturing": [
        "supply chain disruption manufacturing",
        "manufacturing recall equipment failure",
        "factory automation risks",
    ],
    "it": [
        "cybersecurity breach data privacy",
        "API outage software failure",
        "IT regulatory compliance",
    ],
}

# ── Industry → academic search terms ─────────────────────────────────────────
_INDUSTRY_ARXIV_QUERIES: Dict[str, str] = {
    "construction": "construction project risk management",
    "manufacturing": "manufacturing supply chain risk",
    "it": "software project risk cybersecurity",
}

# ── World Bank indicators (GDP growth, unemployment) ─────────────────────────
_WB_INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
}

# ── Country → ISO2 code (best-effort) ────────────────────────────────────────
_COUNTRY_ISO2: Dict[str, str] = {
    "germany": "DE",
    "india": "IN",
    "usa": "US",
    "united states": "US",
    "uk": "GB",
    "united kingdom": "GB",
    "france": "FR",
    "china": "CN",
    "brazil": "BR",
    "australia": "AU",
    "canada": "CA",
    "japan": "JP",
}

_REQUEST_TIMEOUT = 8  # seconds


def _fetch_url(url: str) -> Optional[str]:
    """Fetch *url* and return the response body as text, or ``None`` on error."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "RiskAssessmentAgent/1.0 (academic research tool)"},
        )
        with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        logger.warning("HTTP fetch failed for %s: %s", url, exc)
        return None


def _parse_rss(xml_text: str, max_items: int = 5) -> List[Dict[str, str]]:
    """Parse an RSS feed and return a list of item dicts."""
    items: List[Dict[str, str]] = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        # Handle both RSS <item> and Atom <entry>
        entries = root.findall(".//item")
        if not entries:
            entries = root.findall(".//atom:entry", ns)
        for entry in entries[:max_items]:
            title_el = entry.find("title")
            if title_el is None:
                title_el = entry.find("atom:title", ns)
            link_el = entry.find("link")
            if link_el is None:
                link_el = entry.find("atom:link", ns)
            pub_el = entry.find("pubDate")
            if pub_el is None:
                pub_el = entry.find("updated")
            if pub_el is None:
                pub_el = entry.find("atom:updated", ns)
            title = title_el.text if title_el is not None else "No title"
            # <link> in Atom feeds can be an element with href attr
            if link_el is not None:
                link = link_el.get("href") or (link_el.text or "")
            else:
                link = ""
            pub = pub_el.text if pub_el is not None else ""
            # Strip HTML from title
            if title:
                title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
            items.append({"title": title, "url": link.strip(), "date": pub.strip()})
    except ET.ParseError as exc:
        logger.warning("RSS parse error: %s", exc)
    return items


class InternetDataFetcher:
    """
    Fetches live internet data from free public APIs for risk enrichment.

    All methods accept an optional *cache_manager* for testability; if not
    provided, a default :class:`~agent.cache_manager.CacheManager` is used.

    Confidence scores
    -----------------
    ``"real-time"``   – freshly fetched this session  
    ``"cached"``      – served from the on-disk 24-hour cache  
    ``"fallback"``    – API unavailable; returns empty result
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None) -> None:
        self._cache = cache_manager or CacheManager()

    # ── Public API ────────────────────────────────────────────────────────────

    def fetch_regulatory_updates(
        self, industry: str, region: str
    ) -> Dict[str, Any]:
        """
        Return regulatory news relevant to *industry* and *region*.

        Returns a dict with keys ``items`` (list of article dicts) and
        ``confidence`` (``"real-time"`` | ``"cached"`` | ``"fallback"``).
        """
        key = f"regulatory_{industry}_{region}".lower().replace(" ", "_")
        cached = self._cache.get_cached(key)
        if cached is not None:
            cached["confidence"] = "cached"
            return cached

        items: List[Dict[str, str]] = []
        sources_used: List[str] = []

        # EU-Lex (relevant for EU / Germany / Western Europe)
        if any(k in region.lower() for k in ("eu", "europe", "germany", "france", "uk")):
            xml = _fetch_url(_EULEX_RSS)
            if xml:
                items.extend(_parse_rss(xml, max_items=3))
                sources_used.append("EU-Lex")

        # FDA (relevant for USA / North America / pharma / medical / food)
        if any(k in region.lower() for k in ("usa", "us", "america", "united states")) or industry in ("manufacturing",):
            xml = _fetch_url(_FDA_RSS)
            if xml:
                items.extend(_parse_rss(xml, max_items=3))
                sources_used.append("FDA")

        # Google News for industry-specific regulations
        reg_query = urllib.parse.quote(f"{industry} regulations compliance {region}")
        xml = _fetch_url(_GNEWS_RSS.format(query=reg_query))
        if xml:
            items.extend(_parse_rss(xml, max_items=3))
            sources_used.append("Google News")

        result: Dict[str, Any] = {
            "items": items[:8],
            "sources": sources_used,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": "real-time" if items else "fallback",
        }
        if items:
            self._cache.set_cache(key, result)
        return result

    def fetch_industry_news(self, industry: str) -> Dict[str, Any]:
        """
        Return top 5 industry-relevant news items.

        Queries Google News RSS with industry-specific search terms.
        """
        key = f"industry_news_{industry}".lower()
        cached = self._cache.get_cached(key)
        if cached is not None:
            cached["confidence"] = "cached"
            return cached

        queries = _INDUSTRY_NEWS_QUERIES.get(industry.lower(), [f"{industry} project risk"])
        items: List[Dict[str, str]] = []

        for query in queries[:2]:  # Limit to 2 queries to be polite
            encoded = urllib.parse.quote(query)
            xml = _fetch_url(_GNEWS_RSS.format(query=encoded))
            if xml:
                items.extend(_parse_rss(xml, max_items=3))

        # Deduplicate by title
        seen: set = set()
        unique: List[Dict[str, str]] = []
        for item in items:
            if item["title"] not in seen:
                seen.add(item["title"])
                unique.append(item)

        result: Dict[str, Any] = {
            "items": unique[:5],
            "sources": ["Google News RSS"],
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": "real-time" if unique else "fallback",
        }
        if unique:
            self._cache.set_cache(key, result)
        return result

    def fetch_market_signals(self, industry: str) -> Dict[str, Any]:
        """
        Return basic market signals (commodity prices, labor trends) from
        Google News and World Bank macro indicators.
        """
        key = f"market_signals_{industry}".lower()
        cached = self._cache.get_cached(key)
        if cached is not None:
            cached["confidence"] = "cached"
            return cached

        market_queries: Dict[str, str] = {
            "construction": "construction material prices labor shortage 2024",
            "manufacturing": "commodity prices supply chain disruption factory",
            "it": "tech layoffs software labor market salary trends",
        }
        query = market_queries.get(industry.lower(), f"{industry} market trends")
        encoded = urllib.parse.quote(query)
        xml = _fetch_url(_GNEWS_RSS.format(query=encoded))
        items = _parse_rss(xml, max_items=5) if xml else []

        # World Bank macro indicator (global — "WLD" country code)
        wb_signals: List[Dict[str, str]] = []
        for indicator_name, indicator_code in _WB_INDICATORS.items():
            url = _WORLDBANK_API.format(country="WLD", indicator=indicator_code)
            raw = _fetch_url(url)
            if raw:
                signal = _parse_worldbank(raw, indicator_name)
                if signal:
                    wb_signals.append(signal)

        result: Dict[str, Any] = {
            "news_signals": items,
            "macro_indicators": wb_signals,
            "sources": ["Google News RSS"] + (["World Bank API"] if wb_signals else []),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": "real-time" if (items or wb_signals) else "fallback",
        }
        if items or wb_signals:
            self._cache.set_cache(key, result)
        return result

    def fetch_academic_research(
        self, risk_keywords: List[str], max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Return relevant academic papers from arXiv matching *risk_keywords*.
        """
        query_str = " ".join(risk_keywords[:4])
        key = f"arxiv_{'_'.join(risk_keywords[:3])}".lower().replace(" ", "_")
        cached = self._cache.get_cached(key)
        if cached is not None:
            cached["confidence"] = "cached"
            return cached

        encoded = urllib.parse.quote(f"all:{query_str} risk management project")
        url = _ARXIV_API.format(query=encoded, n=max_results)
        xml = _fetch_url(url)
        papers = _parse_arxiv(xml) if xml else []

        result: Dict[str, Any] = {
            "papers": papers[:max_results],
            "sources": ["arXiv API"],
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": "real-time" if papers else "fallback",
        }
        if papers:
            self._cache.set_cache(key, result)
        return result

    def fetch_geopolitical_risks(
        self, region: str = "", industry: str = ""
    ) -> Dict[str, Any]:
        """
        Return current geopolitical and macroeconomic risk signals via
        Google News and World Bank data for the given region / industry.
        """
        key = f"geopolitical_{region}_{industry}".lower().replace(" ", "_")
        cached = self._cache.get_cached(key)
        if cached is not None:
            cached["confidence"] = "cached"
            return cached

        queries = [
            "geopolitical risk trade war tariffs sanctions 2024",
            f"{region} political economic risk" if region else "global economic risk forecast",
        ]
        items: List[Dict[str, str]] = []
        for q in queries:
            encoded = urllib.parse.quote(q)
            xml = _fetch_url(_GNEWS_RSS.format(query=encoded))
            if xml:
                items.extend(_parse_rss(xml, max_items=3))

        # Deduplicate
        seen: set = set()
        unique: List[Dict[str, str]] = []
        for item in items:
            if item["title"] not in seen:
                seen.add(item["title"])
                unique.append(item)

        result: Dict[str, Any] = {
            "items": unique[:6],
            "sources": ["Google News RSS"],
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": "real-time" if unique else "fallback",
        }
        if unique:
            self._cache.set_cache(key, result)
        return result


# ── Parsing helpers ───────────────────────────────────────────────────────────

def _parse_arxiv(xml_text: str) -> List[Dict[str, str]]:
    """Parse an arXiv Atom feed and return a list of paper dicts."""
    papers: List[Dict[str, str]] = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            # Link with rel="alternate" is the abstract page
            link_el = entry.find("atom:link[@rel='alternate']", ns)
            if link_el is None:
                link_el = entry.find("atom:link", ns)
            authors = [
                a.find("atom:name", ns).text
                for a in entry.findall("atom:author", ns)
                if a.find("atom:name", ns) is not None
            ]
            title = (title_el.text or "").strip().replace("\n", " ")
            summary = (summary_el.text or "").strip().replace("\n", " ")[:300]
            url = (link_el.get("href") if link_el is not None else "") or ""
            pub = (published_el.text or "")[:10]
            papers.append(
                {
                    "title": title,
                    "authors": ", ".join(authors[:3]),
                    "summary": summary,
                    "url": url,
                    "published": pub,
                    "source": "arXiv",
                }
            )
    except ET.ParseError as exc:
        logger.warning("arXiv parse error: %s", exc)
    return papers


def _parse_worldbank(json_text: str, indicator_name: str) -> Optional[Dict[str, str]]:
    """Parse a World Bank JSON response and return a summary dict."""
    import json

    try:
        data = json.loads(json_text)
        # World Bank returns [metadata, [records]]
        if isinstance(data, list) and len(data) == 2:
            records = data[1]
            if records:
                rec = records[0]
                value = rec.get("value")
                year = rec.get("date", "")
                if value is not None:
                    return {
                        "indicator": indicator_name,
                        "value": f"{value:.2f}",
                        "year": year,
                        "source": "World Bank",
                    }
    except (json.JSONDecodeError, KeyError, TypeError, IndexError) as exc:
        logger.warning("World Bank parse error: %s", exc)
    return None
