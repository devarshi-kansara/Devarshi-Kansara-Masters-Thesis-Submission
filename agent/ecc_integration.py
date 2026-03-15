"""
Optional integration layer for everything-claude-code (ECC) skills.

This module wraps ECC's ``deep-research`` and ``market-research`` skills to
provide supplementary data enrichment on top of the existing
:class:`~agent.internet_fetcher.InternetDataFetcher` pipeline.

Behaviour
---------
* **ECC available** — ``enrich_risk_academic()`` and
  ``validate_risk_market_data()`` call the ECC skill layer and return enriched
  data, which is then merged with the base internet-fetcher results.
* **ECC unavailable** — all methods return empty/``None`` results and log an
  ``INFO`` message.  The agent continues normally; no exception is raised.

The module never raises; it is designed to be called inside a bare
``try/except Exception`` block in :mod:`agent.risk_agent`.

Caching
-------
Results are cached via :class:`~agent.cache_manager.CacheManager` with the
same 24-hour TTL used by the internet fetcher, so repeated runs on the same
risk description incur no extra network calls.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── ECC availability flag ─────────────────────────────────────────────────────
# ECC exposes its skills as importable Python modules when the optional
# ``ecc-universal`` package (or individual ``@ecc/*`` packages) is installed.
# If the package is absent we set _ECC_AVAILABLE = False and all public methods
# return graceful empty results.

_ECC_AVAILABLE: bool = False
_ecc_deep_research: Any = None
_ecc_market_research: Any = None

try:
    import ecc.skills.deep_research as _ecc_deep_research  # type: ignore[import]
    import ecc.skills.market_research as _ecc_market_research  # type: ignore[import]
    _ECC_AVAILABLE = True
    logger.info("ECC skills loaded: deep_research, market_research")
except ImportError:
    logger.info(
        "ECC skills not installed — academic/market enrichment will be skipped. "
        "See docs/ECC_INTEGRATION.md for installation instructions."
    )


def is_ecc_available() -> bool:
    """Return ``True`` when the ECC skill modules are importable."""
    return _ECC_AVAILABLE


class EccResearchBridge:
    """
    Bridge between the Risk Assessment Agent and ECC's research skills.

    Parameters
    ----------
    cache_manager:
        An optional :class:`~agent.cache_manager.CacheManager` instance.  If
        omitted, a default one is created lazily on first use.
    """

    # Number of papers at which the paper-coverage sub-score reaches 1.0
    _MAX_PAPERS_FOR_FULL_CONFIDENCE: float = 3.0

    def __init__(self, cache_manager: Any = None) -> None:
        self._cache = cache_manager

    # ── Cache helper ──────────────────────────────────────────────────────────

    def _get_cache(self) -> Any:
        """Return the shared CacheManager, creating one if needed."""
        if self._cache is None:
            try:
                from agent.cache_manager import CacheManager  # lazy import
                self._cache = CacheManager()
            except ImportError:
                pass
        return self._cache

    @staticmethod
    def _cache_key(prefix: str, text: str) -> str:
        digest = hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()
        return f"ecc_{prefix}_{digest}"

    # ── Public API ────────────────────────────────────────────────────────────

    def enrich_risk_academic(
        self,
        risk_description: str,
        industry: str,
        max_papers: int = 3,
    ) -> List[Dict[str, str]]:
        """
        Use ECC's ``deep-research`` skill to find academic papers relevant to
        a given risk description.

        Parameters
        ----------
        risk_description:
            Free-text description of the risk (e.g. ``"permit delays"``).
        industry:
            Target industry (e.g. ``"construction"``).
        max_papers:
            Maximum number of paper dicts to return.

        Returns
        -------
        list of dict
            Each dict may contain keys ``title``, ``authors``, ``published``,
            ``url``, and ``summary``.  Returns an empty list when ECC is
            unavailable or the call fails.
        """
        if not _ECC_AVAILABLE:
            return []

        key = self._cache_key("academic", f"{risk_description}|{industry}")
        cache = self._get_cache()
        if cache is not None:
            cached = cache.get_cached(key)
            if cached is not None:
                return cached.get("papers", [])

        try:
            query = (
                f"Academic research on '{risk_description}' risks "
                f"in the {industry} industry. "
                f"Return peer-reviewed papers."
            )
            raw = _ecc_deep_research.run(query=query, max_results=max_papers)
            papers: List[Dict[str, str]] = raw.get("papers", [])
        except Exception as exc:  # noqa: BLE001
            logger.warning("ECC deep-research call failed: %s", exc)
            return []

        result = {"papers": papers[:max_papers]}
        if cache is not None:
            cache.set_cache(key, result)
        return result["papers"]

    def validate_risk_market_data(
        self,
        risk_description: str,
        industry: str,
    ) -> Dict[str, Any]:
        """
        Use ECC's ``market-research`` skill to find current market signals
        relevant to a given risk.

        Parameters
        ----------
        risk_description:
            Free-text description of the risk.
        industry:
            Target industry.

        Returns
        -------
        dict
            May contain keys ``market_trends``, ``price_signals``,
            ``regulatory_changes``, and ``confidence``.  Returns an empty dict
            when ECC is unavailable or the call fails.
        """
        if not _ECC_AVAILABLE:
            return {}

        key = self._cache_key("market", f"{risk_description}|{industry}")
        cache = self._get_cache()
        if cache is not None:
            cached = cache.get_cached(key)
            if cached is not None:
                return cached.get("validation", {})

        try:
            query = (
                f"Market research on '{risk_description}' in the {industry} industry. "
                f"Find current market trends, price signals, and regulatory changes."
            )
            raw = _ecc_market_research.run(query=query)
            validation: Dict[str, Any] = {
                "market_trends": raw.get("trends", []),
                "price_signals": raw.get("price_signals", []),
                "regulatory_changes": raw.get("regulatory_changes", []),
                "confidence": raw.get("confidence", "low"),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("ECC market-research call failed: %s", exc)
            return {}

        result = {"validation": validation}
        if cache is not None:
            cache.set_cache(key, result)
        return validation

    def compute_ecc_confidence_score(
        self,
        papers: List[Dict[str, str]],
        market_validation: Dict[str, Any],
    ) -> Optional[float]:
        """
        Compute a simple 0–1 confidence score based on how much ECC evidence
        was found for a risk.

        The score is the average of:
        * paper coverage  (min(len(papers) / _MAX_PAPERS_FOR_FULL_CONFIDENCE, 1.0))
        * market coverage (1.0 if market_validation is non-empty else 0.0)

        Returns ``None`` when both inputs are empty (i.e. ECC was not called).
        """
        if not papers and not market_validation:
            return None

        paper_score = min(len(papers) / self._MAX_PAPERS_FOR_FULL_CONFIDENCE, 1.0)
        market_score = 1.0 if market_validation else 0.0
        return round((paper_score + market_score) / 2.0, 2)
