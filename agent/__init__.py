"""
Project Risk Assessment Agent
Based on the thesis: "Understanding Risk Awareness and Decision Making in
Early-Stage Project Planning: Comparative Study of Project Managers Across Industries"
by Devarshi Kansara

Optional ECC Integration
------------------------
This package supports an optional integration with the everything-claude-code
(ECC) skill library (https://github.com/affaan-m/everything-claude-code).
When the ``ecc-universal`` package (or individual ``@ecc/deep-research`` and
``@ecc/market-research`` packages) is installed, the agent automatically
enriches each :class:`~agent.models.RiskItem` with:

* ``ecc_research_papers`` — peer-reviewed papers from ECC's deep-research skill
* ``ecc_market_validation`` — market trends and price signals from ECC's
  market-research skill
* ``ecc_confidence_score`` — a 0–1 confidence score derived from ECC evidence

If ECC is **not** installed the agent degrades gracefully: the existing
:class:`~agent.internet_fetcher.InternetDataFetcher` pipeline is unaffected and
the three ECC fields remain at their default empty values.

See ``docs/ECC_INTEGRATION.md`` for full installation and configuration details.
"""
