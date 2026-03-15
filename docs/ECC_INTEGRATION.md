# ECC Integration Guide

This document explains how the Risk Assessment Agent optionally integrates with
the [everything-claude-code (ECC)](https://github.com/affaan-m/everything-claude-code)
skill library to enhance live data enrichment.

---

## Overview

The base agent already enriches each risk with live data from free public APIs
(Google News, EU-Lex, FDA, arXiv, World Bank) via `agent/internet_fetcher.py`.

When ECC is installed, a second enrichment pass runs via `agent/ecc_integration.py`,
calling two ECC skills:

| ECC Skill | What it does | Risk field populated |
|---|---|---|
| `deep-research` | Finds peer-reviewed academic papers for each risk | `ecc_research_papers` |
| `market-research` | Finds current market trends and price signals | `ecc_market_validation` |

A derived `ecc_confidence_score` (0–1 float) is also computed from how much
evidence ECC found for the risk.

---

## Installation (Optional)

ECC enrichment is **entirely optional**.  The agent works identically without it.

### Option 1 — Full ECC package

```bash
npm install -D ecc-universal
```

### Option 2 — Individual skills only

```bash
npm install -D @ecc/deep-research @ecc/market-research
```

After installation the agent auto-detects ECC on the next run.  No code changes
or configuration flags are needed.

---

## How the Integration Works

### With ECC installed

```
generate_report()
  └─ _enrich_with_live_data()
       ├─ InternetDataFetcher          ← existing pipeline (unchanged)
       │    ├─ fetch_regulatory_updates()
       │    ├─ fetch_industry_news()
       │    ├─ fetch_market_signals()
       │    ├─ fetch_academic_research()
       │    └─ fetch_geopolitical_risks()
       │
       └─ EccResearchBridge            ← NEW (runs only when ECC available)
            ├─ enrich_risk_academic()   → risk.ecc_research_papers
            ├─ validate_risk_market_data() → risk.ecc_market_validation
            └─ compute_ecc_confidence_score() → risk.ecc_confidence_score
```

### Without ECC installed

```
generate_report()
  └─ _enrich_with_live_data()
       └─ InternetDataFetcher          ← runs as before
            (ECC bridge skipped — logged as INFO, not WARNING/ERROR)
```

---

## Fallback Behaviour

The integration is designed so that **no ECC failure can crash the agent**:

1. If `ecc-universal` is not installed → `is_ecc_available()` returns `False`
   and the bridge is never called.
2. If ECC *is* installed but a skill call raises an exception → the exception is
   caught inside `_enrich_with_live_data()` and logged at `INFO` level.
3. The three ECC fields on `RiskItem` default to empty list/dict/`None`, so
   existing serialisation and report rendering are unaffected.

---

## Accessing ECC Data in Reports

```python
from agent.risk_agent import RiskAssessmentAgent

agent = RiskAssessmentAgent()
ctx = agent.build_context(
    industry="construction",
    years_experience=8,
    projects_managed=15,
    cultural_region="Germany",
    top_risks=["Permit delays", "Material shortage"],
)
report = agent.generate_report(ctx)

for risk in report.risk_register:
    print(f"Risk: {risk.description}")
    print(f"  ECC papers:      {risk.ecc_research_papers}")
    print(f"  ECC market data: {risk.ecc_market_validation}")
    print(f"  ECC confidence:  {risk.ecc_confidence_score}")
```

When ECC is not installed all three fields will be `[]`, `{}`, and `None`
respectively.

---

## Checking ECC Availability at Runtime

```python
from agent.ecc_integration import is_ecc_available

if is_ecc_available():
    print("ECC skills are active — enrichment will include ECC data.")
else:
    print("ECC not installed — using internet fetcher only.")
```

---

## Caching Strategy

ECC results are cached with the same `CacheManager` used by the internet
fetcher.  Cache keys are prefixed with `ecc_academic_` and `ecc_market_` and
use an MD5 hash of `"{risk_description}|{industry}"`.

* **TTL:** 24 hours (inherited from `CacheManager` default)
* **Location:** same cache directory as internet fetcher results

This means repeated runs on the same risk in the same day incur **no extra ECC
API calls**.

---

## Performance Impact

| Scenario | Latency added |
|---|---|
| ECC not installed | 0 ms (skipped entirely) |
| ECC installed, cache hit | ~1 ms (dict lookup) |
| ECC installed, cache miss | Depends on ECC skill response time |

For production use it is recommended to run the agent once to warm the cache,
then rely on cached responses for subsequent report generations in the same day.

---

## No Breaking Changes

The following are guaranteed to be unaffected by this integration:

* `RiskItem.recent_news_link`, `recent_news_title`, `recent_news_date`,
  `regulatory_status`, `market_signal`, `academic_citation` — unchanged
* `InternetDataFetcher` public API — unchanged
* `RiskAssessmentAgent.generate_report()` signature — unchanged
* Old serialised `RiskItem` objects (e.g. from JSON/pickle) still deserialise
  correctly because the three new fields have default values
