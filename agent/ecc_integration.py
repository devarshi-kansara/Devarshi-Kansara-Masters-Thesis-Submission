"""
ECC (everything-claude-code) integration layer for the Risk Assessment Agent.

This module provides an optional bridge to ECC's ``deep-research`` and
``market-research`` skills.  When the ECC package is **not** installed the
module degrades gracefully: all public methods return empty/neutral values and
the agent continues without ECC-sourced data.

Install ECC skills (optional):
    pip install everything-claude-code          # if published as a package
    # — OR —
    git clone https://github.com/affaan-m/everything-claude-code .ecc

Usage:
    from agent.ecc_integration import ECCIntegration
    ecc = ECCIntegration(cache_manager=my_cache)

    # Enrich a single risk with deep-research results
    papers = ecc.enrich_risk_academic(risk, industry="construction")

    # Validate a risk's market signal
    validation = ecc.validate_risk_market_data(risk, industry="construction")
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Try to import ECC skills ──────────────────────────────────────────────────
# ECC is an *optional* dependency.  We attempt to import the two skills we use
# and fall back to lightweight stub objects if the package is absent.

try:
    from ecc.skills.deep_research import DeepResearchSkill as _DeepResearchSkill  # type: ignore[import]

    _ECC_DEEP_RESEARCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ECC_DEEP_RESEARCH_AVAILABLE = False
    _DeepResearchSkill = None  # type: ignore[assignment,misc]

try:
    from ecc.skills.market_research import MarketResearchSkill as _MarketResearchSkill  # type: ignore[import]

    _ECC_MARKET_RESEARCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ECC_MARKET_RESEARCH_AVAILABLE = False
    _MarketResearchSkill = None  # type: ignore[assignment,misc]

_ECC_AVAILABLE = _ECC_DEEP_RESEARCH_AVAILABLE or _ECC_MARKET_RESEARCH_AVAILABLE


# ── Public helper ─────────────────────────────────────────────────────────────

def ecc_available() -> bool:
    """Return ``True`` when at least one ECC skill can be imported."""
    return _ECC_AVAILABLE


# ── Integration class ─────────────────────────────────────────────────────────

class ECCIntegration:
    """
    Bridge between the Risk Assessment Agent and ECC skills.

    Parameters
    ----------
    cache_manager:
        Optional :class:`~agent.cache_manager.CacheManager` instance.  When
        provided, ECC results are cached to avoid redundant network calls.
    ttl_hours:
        How long to cache ECC results (default: 24 hours, matching the
        existing internet fetcher cache strategy).
    """

    def __init__(
        self,
        cache_manager: Any = None,
        ttl_hours: float = 24.0,
    ) -> None:
        self._cache = cache_manager
        self._ttl = ttl_hours
        self._deep_research = (
            _DeepResearchSkill() if _ECC_DEEP_RESEARCH_AVAILABLE else None
        )
        self._market_research = (
            _MarketResearchSkill() if _ECC_MARKET_RESEARCH_AVAILABLE else None
        )

        if _ECC_AVAILABLE:
            logger.info("ECC integration enabled (deep_research=%s, market_research=%s)",
                        _ECC_DEEP_RESEARCH_AVAILABLE, _ECC_MARKET_RESEARCH_AVAILABLE)
        else:
            logger.info(
                "ECC skills not installed — enrichment will rely on internet_fetcher only. "
                "See docs/ECC_INTEGRATION.md for installation instructions."
            )

    # ── Public API ────────────────────────────────────────────────────────────

    def enrich_risk_academic(
        self,
        risk: Any,  # agent.models.RiskItem — kept as Any to avoid circular import
        industry: str,
        max_papers: int = 3,
    ) -> List[Dict[str, str]]:
        """
        Use ECC's ``deep-research`` skill to find academic papers related to
        *risk* and return them as a list of dicts.

        Each dict has the keys:
        ``title``, ``authors``, ``published``, ``url``, ``summary``, ``source``.

        Returns an empty list when ECC is unavailable or when the query fails.

        Parameters
        ----------
        risk:
            A :class:`~agent.models.RiskItem` instance.
        industry:
            Industry context string (e.g. ``"construction"``).
        max_papers:
            Maximum number of papers to return (default: 3).
        """
        if not _ECC_DEEP_RESEARCH_AVAILABLE or self._deep_research is None:
            return []

        query = f"{risk.description} risk {industry} project management"
        cache_key = f"ecc_academic_{query.replace(' ', '_')[:80]}"

        if self._cache is not None:
            cached = self._cache.get_cached(cache_key)
            if cached is not None:
                logger.debug("ECC academic cache hit for '%s'", query[:50])
                return cached  # type: ignore[return-value]

        try:
            results = self._deep_research.search(
                query=query,
                result_type="academic",
                max_results=max_papers,
            )
            papers = self._normalise_papers(results)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ECC deep-research failed for '%s': %s", query[:50], exc)
            return []

        if self._cache is not None:
            self._cache.set_cache(cache_key, papers, ttl_hours=self._ttl)

        return papers[:max_papers]

    def validate_risk_market_data(
        self,
        risk: Any,  # agent.models.RiskItem — kept as Any to avoid circular import
        industry: str,
    ) -> Dict[str, Any]:
        """
        Use ECC's ``market-research`` skill to validate the market signal
        associated with *risk*.

        Returns a dict with the keys:
        ``risk_description``, ``market_evidence`` (list of evidence items),
        ``confidence`` (``"high"`` | ``"medium"`` | ``"low"`` | ``"unavailable"``),
        ``source`` (``"ECC market-research"``).

        Returns a neutral dict when ECC is unavailable or when the query fails.

        Parameters
        ----------
        risk:
            A :class:`~agent.models.RiskItem` instance.
        industry:
            Industry context string (e.g. ``"construction"``).
        """
        if not _ECC_MARKET_RESEARCH_AVAILABLE or self._market_research is None:
            return {
                "risk_description": risk.description,
                "market_evidence": [],
                "confidence": "unavailable",
                "source": "ECC market-research",
            }

        query = f"{risk.description} market trends {industry}"
        cache_key = f"ecc_market_{query.replace(' ', '_')[:80]}"

        if self._cache is not None:
            cached = self._cache.get_cached(cache_key)
            if cached is not None:
                logger.debug("ECC market cache hit for '%s'", query[:50])
                return cached  # type: ignore[return-value]

        try:
            results = self._market_research.research(
                query=query,
                industry=industry,
            )
            validation = self._normalise_market(risk.description, results)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ECC market-research failed for '%s': %s", query[:50], exc)
            return {
                "risk_description": risk.description,
                "market_evidence": [],
                "confidence": "unavailable",
                "source": "ECC market-research",
            }

        if self._cache is not None:
            self._cache.set_cache(cache_key, validation, ttl_hours=self._ttl)

        return validation

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _normalise_papers(raw: Any) -> List[Dict[str, str]]:
        """Normalise ECC deep-research results to a consistent dict schema."""
        papers: List[Dict[str, str]] = []
        if not isinstance(raw, list):
            return papers
        for item in raw:
            if not isinstance(item, dict):
                continue
            papers.append(
                {
                    "title": str(item.get("title") or ""),
                    "authors": str(item.get("authors") or item.get("author") or ""),
                    "published": str(item.get("published") or item.get("date") or ""),
                    "url": str(item.get("url") or item.get("link") or ""),
                    "summary": str(item.get("summary") or item.get("abstract") or ""),
                    "source": "ECC deep-research",
                }
            )
        return papers

    @staticmethod
    def _normalise_market(risk_description: str, raw: Any) -> Dict[str, Any]:
        """Normalise ECC market-research results to a consistent dict schema."""
        evidence: List[Any] = []
        confidence = "low"

        if isinstance(raw, dict):
            evidence = raw.get("evidence", raw.get("results", []))
            confidence = raw.get("confidence", "low")
        elif isinstance(raw, list):
            evidence = raw
            confidence = "medium" if raw else "low"

        return {
            "risk_description": risk_description,
            "market_evidence": evidence,
            "confidence": confidence,
            "source": "ECC market-research",
        }
