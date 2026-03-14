"""
Data Fetcher — Phase 1 specialist module.

Provides mock regulatory intelligence, market signals, and black swan
warnings tailored to the project context.  Implemented as static
knowledge-base lookups (no external API calls) ready for live API
integration in Phase 2.
"""
from __future__ import annotations

from typing import List

from agent.models import ProjectContext

# ── Regulatory intelligence by industry ──────────────────────────────────────
_REGULATORY_INTEL: dict = {
    "construction": [
        "EU Construction Products Regulation (CPR 305/2011): CE marking required for "
        "structural components — non-compliance blocks project delivery.",
        "VOB/B (Germany): Part B governs construction service contracts; clause 13 "
        "imposes a 4-year defect liability period — document all deviations in writing.",
        "EU Workplace Safety Directive 89/391/EEC: risk assessment documentation "
        "must be available to labour inspectors on site from day 1.",
        "DGUV Regulation 38 (Germany): mandatory safety coordinator appointment for "
        "projects involving more than one contractor on site simultaneously.",
    ],
    "manufacturing": [
        "EU Machinery Directive 2006/42/EC: CE marking required for all new machinery "
        "before market placement — engage a Notified Body in the first 20%.",
        "EU MDR 2017/745: medical device projects must submit a Clinical Evaluation "
        "Plan within the first project phase — delays here cascade into launch risk.",
        "ISO 9001:2015 Clause 6.1: organisations must address risks and opportunities "
        "as part of quality planning — ensure risk register is linked to QMS.",
        "REACH Regulation (EC 1907/2006): chemical substance registration can take "
        "6–18 months; initiate in the first 20% to avoid production hold.",
    ],
    "it": [
        "GDPR (EU 2016/679): data protection impact assessments (DPIA) are mandatory "
        "for high-risk processing activities — initiate in sprint 1.",
        "DORA (EU 2022/2554): financial sector digital resilience obligations include "
        "ICT risk management frameworks — engage compliance from day 1.",
        "NIS2 Directive (EU 2022/2555): expanded cybersecurity obligations for critical "
        "infrastructure operators — threat modelling required before architecture lock-in.",
        "eIDAS Regulation: if your system handles electronic signatures or identity, "
        "qualified trust service providers must be engaged early.",
    ],
}

# ── Market signals by industry ────────────────────────────────────────────────
_MARKET_SIGNALS: dict = {
    "construction": [
        "European construction cost indices rose 12–18% in 2022–2024; re-baseline "
        "material budgets against current spot prices, not contract award estimates.",
        "Skilled trades shortage: electricians and steel fixers are 8–14 weeks lead "
        "time in Germany and Western Europe — book in the first 20%.",
        "BIM mandate: German public-sector clients require BIM Level 2 on all new "
        "federal infrastructure contracts — confirm client BIM specification upfront.",
    ],
    "manufacturing": [
        "Semiconductor lead times remain elevated (16–52 weeks for some components); "
        "identify all electronics dependencies and place orders immediately.",
        "Energy cost volatility: European industrial electricity prices remain 2–3× "
        "pre-2021 levels — re-evaluate energy-intensive production assumptions.",
        "Reshoring trend: EU Critical Raw Materials Act (2024) creates incentives for "
        "domestic sourcing — assess if reshoring changes your supply risk profile.",
    ],
    "it": [
        "Cloud hyperscaler pricing changes: AWS, Azure, and GCP each revised pricing "
        "structures in 2023–2024 — validate cloud cost models against current rates.",
        "AI model API pricing volatility: LLM API costs have shifted significantly; "
        "if your product depends on third-party AI, lock in pricing agreements early.",
        "Cybersecurity insurance: premiums rose 50–100% post-2021; factor cyber "
        "insurance costs into project budget from the first 20%.",
    ],
}

# ── Black swan warnings by industry ──────────────────────────────────────────
_BLACK_SWAN_WARNINGS: dict = {
    "construction": [
        "Sudden ground-collapse or undiscovered archaeological site: halts work "
        "immediately and triggers legal obligations — no contingency fully covers this; "
        "ensure project insurance covers force-majeure ground events.",
        "Key subcontractor insolvency mid-project: occurs in 4–8% of major projects "
        "annually — verify financial health of top-3 subcontractors before award.",
        "Extreme weather event (flooding, heat dome): European frequency doubled "
        "since 2010 — include weather-force-majeure clauses in all contracts.",
    ],
    "manufacturing": [
        "Single-source critical component discontinuation: supplier EOL notices can "
        "arrive with 90 days' notice — audit all single-source parts in the BOM now.",
        "Pandemic or geopolitical supply shock: COVID-19 and Ukraine conflict both "
        "triggered 6–18 month supply chain disruptions with minimal warning.",
        "Regulatory recall cascade: a defect in one component can trigger a full "
        "product recall costing 10–100× the original product value.",
    ],
    "it": [
        "Zero-day vulnerability in a core dependency: Log4Shell-type events can "
        "require immediate, unplanned rework across the entire codebase.",
        "Cloud provider major outage: AWS, Azure, and GCP have each experienced "
        "multi-hour regional outages — design for graceful degradation from day 1.",
        "Key engineer departure mid-project: knowledge-silo risk is highest in the "
        "first 20% — mandate documentation sprints from sprint 1.",
    ],
}


class DataFetcher:
    """Provides regulatory intelligence, market signals, and black swan warnings."""

    def get_regulatory_intel(self, ctx: ProjectContext) -> List[str]:
        """Return regulatory intelligence relevant to the project context."""
        return _REGULATORY_INTEL.get(ctx.industry, [])

    def get_market_signals(self, ctx: ProjectContext) -> List[str]:
        """Return current market signals relevant to the project context."""
        return _MARKET_SIGNALS.get(ctx.industry, [])

    def get_black_swan_warnings(self, ctx: ProjectContext) -> List[str]:
        """Return low-probability, high-impact black swan warnings for the context."""
        return _BLACK_SWAN_WARNINGS.get(ctx.industry, [])
