# ECC Integration Guide

This document explains how the Risk Assessment Agent optionally integrates with
the [everything-claude-code (ECC)](https://github.com/affaan-m/everything-claude-code)
skill library to enhance live-data enrichment.

---

## Overview

The integration follows **Option A — Minimal Integration**: a lightweight bridge
module (`agent/ecc_integration.py`) wraps two ECC skills and merges their output
with the existing `InternetDataFetcher` results.  ECC is a _supplementary_ data
source; the agent works identically with or without it.

---

## ECC Skills Used

| Skill | Purpose in the Agent |
|-------|----------------------|
| `deep-research` | Finds peer-reviewed academic papers that support or contextualise each identified risk |
| `market-research` | Validates the market signal associated with each risk and provides a confidence rating |

---

## Installation (Optional)

ECC is an optional dependency.  To enable it, install the package using one of
the methods below and then run the agent as usual — no configuration changes are
required.

### Method 1 — PyPI (if published)

```bash
pip install everything-claude-code
```

### Method 2 — Clone the repository

```bash
git clone https://github.com/affaan-m/everything-claude-code .ecc
pip install -e .ecc
```

After installation, verify that the skills are accessible:

```python
from ecc.skills.deep_research import DeepResearchSkill
from ecc.skills.market_research import MarketResearchSkill
```

If either import succeeds, the corresponding skill will be used automatically.

---

## How the Integration Works

### Flow diagram

```
generate_report(ctx)
  └─ _enrich_with_live_data(report, ctx)
       ├─ InternetDataFetcher (existing)
       │    ├─ fetch_regulatory_updates()
       │    ├─ fetch_industry_news()
       │    ├─ fetch_market_signals()
       │    ├─ fetch_academic_research()
       │    └─ fetch_geopolitical_risks()
       │
       ├─ _enrich_risk_items()  ← applies internet data to each RiskItem
       │
       └─ _enrich_with_ecc()  ← NEW (no-op when ECC unavailable)
            └─ ECCIntegration
                 ├─ enrich_risk_academic()    → RiskItem.ecc_research_papers
                 └─ validate_risk_market_data() → RiskItem.ecc_market_validation
                                                  RiskItem.ecc_confidence_score
```

### New fields on `RiskItem`

| Field | Type | Description |
|-------|------|-------------|
| `ecc_research_papers` | `List[Dict[str, str]]` | Academic papers from ECC deep-research |
| `ecc_market_validation` | `Dict[str, Any]` | Market evidence and confidence from ECC market-research |
| `ecc_confidence_score` | `float` | Numeric confidence: `0.9` = high, `0.6` = medium, `0.0` = not assessed |

All three fields default to empty/zero and are only populated when ECC is
installed and its skills return results.

### Caching

ECC results are cached with the same `CacheManager` used by `InternetDataFetcher`
(default TTL: 24 hours, stored in `.cache/`).  This means:

- Repeated runs within 24 hours use the cached ECC result — no extra API calls.
- The cache is shared between the internet fetcher and ECC so the combined
  footprint is minimal.

---

## Fallback Behaviour (ECC Unavailable)

When ECC is not installed or fails to import:

1. `ECCIntegration.__init__` logs an `INFO` message (not an error).
2. `_enrich_with_ecc()` returns immediately without modifying the report.
3. All `RiskItem.ecc_*` fields remain at their default empty/zero values.
4. The report is identical to a pre-ECC report.

No exceptions propagate to the caller.  Every ECC call is wrapped in a
`try/except` block that logs a `WARNING` on failure and continues.

---

## Performance Impact

| Scenario | Impact |
|----------|--------|
| ECC not installed | None — method returns immediately |
| First run with ECC | One API call per risk item per skill (≈ 2× `len(risk_register)` calls) |
| Subsequent runs (cached) | Zero additional network calls for 24 hours |

For a typical risk register of 10 items this means up to 20 ECC API calls on
the first run.  All calls are synchronous and sequential.

---

## Programmatic Usage

```python
from agent.risk_agent import RiskAssessmentAgent

agent = RiskAssessmentAgent()
ctx = agent.build_context(
    industry="construction",
    years_experience=8,
    projects_managed=15,
    cultural_region="Germany",
    top_risks=["Weather delays", "Permit issues"],
    risk_locus="external",
    decision_style="balance",
    time_pressure="medium",
)
report = agent.generate_report(ctx)  # ECC enrichment happens here if available

for risk in report.risk_register:
    print(risk.description)
    print("  ECC papers:", len(risk.ecc_research_papers))
    print("  ECC market confidence:", risk.ecc_market_validation.get("confidence"))
    print("  ECC confidence score:", risk.ecc_confidence_score)
```

---

## Checking ECC Availability at Runtime

```python
from agent.ecc_integration import ecc_available

if ecc_available():
    print("ECC enrichment is active")
else:
    print("ECC not installed — using internet_fetcher only")
```

---

## No Breaking Changes

- `RiskItem.recent_news_link`, `recent_news_title`, etc. are unchanged.
- `InternetDataFetcher` API is unchanged.
- `RiskAssessmentAgent.generate_report()` signature is unchanged.
- All new ECC fields are optional with safe defaults (`[]`, `{}`, `0.0`).
- Old serialised `RiskItem` objects (e.g. from JSON) will deserialise correctly
  because the new fields have default values.
