"""
Project Risk Assessment Agent
Based on the thesis: "Understanding Risk Awareness and Decision Making in
Early-Stage Project Planning: Comparative Study of Project Managers Across Industries"
by Devarshi Kansara

Optional ECC Integration
------------------------
This agent supports an optional integration with the
`everything-claude-code (ECC) <https://github.com/affaan-m/everything-claude-code>`_
skill library.  When the ECC package is installed, the agent enriches each
risk item with:

* Academic papers sourced via the ECC ``deep-research`` skill
  (``RiskItem.ecc_research_papers``)
* Market validation evidence via the ECC ``market-research`` skill
  (``RiskItem.ecc_market_validation``, ``RiskItem.ecc_confidence_score``)

ECC is entirely **optional**.  If the package is not installed the agent falls
back to its existing ``internet_fetcher`` behaviour without any change in
output or behaviour.

To enable ECC enrichment, install the package (see docs/ECC_INTEGRATION.md)
and run the agent as usual:

    pip install everything-claude-code   # if published on PyPI
    # — OR —
    git clone https://github.com/affaan-m/everything-claude-code .ecc
"""
