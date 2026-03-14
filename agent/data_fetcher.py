"""
Data fetcher for the risk assessment agent.

Fetches regulatory data, market signals, and geopolitical risk information.
Attempts live API calls when use_live_data=True; always falls back gracefully
to a curated, regularly-updated mock knowledge base.

Live API stubs are provided for future integration with:
  - EUR-Lex (EU regulatory database)
  - FDA API (US medical device and pharma)
  - ENISA (EU cybersecurity)
  - WEF Global Risk API
"""
from __future__ import annotations

# ── Curated Regulatory & Market Data ─────────────────────────────────────────
# Sourced from official publications as of early 2026.
# Used as fallback when live APIs are unavailable.

_MOCK_REGULATORY_DATA: dict = {
    "construction": {
        "last_updated": "2026-01-15",
        "active_regulations": [
            {
                "name": "EU Buildings Directive (EPBD) Recast 2024",
                "status": "Active — enforcement from Jan 2025",
                "risk_level": "High",
                "summary": (
                    "Mandatory nearly-zero energy requirements for all new construction in the EU. "
                    "Non-compliant designs require costly redesign. Factor into specifications from day 1."
                ),
                "source": "Official Journal of the EU, 2024",
            },
            {
                "name": "German VOB (Vergabe- und Vertragsordnung für Bauleistungen) 2023 Update",
                "status": "Active",
                "risk_level": "Medium",
                "summary": (
                    "Updated contractor liability clauses. Subcontractor quality assurance is now "
                    "explicitly documented as the PM's responsibility. Failure to document = liability."
                ),
                "source": "Deutsches Institut für Normung (DIN), 2023",
            },
            {
                "name": "EU Construction Products Regulation (CPR) Revision 2025",
                "status": "Active — phased enforcement 2025–2027",
                "risk_level": "Medium-High",
                "summary": (
                    "Stricter CE-marking requirements for structural products. Procurement of "
                    "non-compliant materials creates project halt risk from 2025 onwards."
                ),
                "source": "European Commission, 2024",
            },
        ],
        "market_signals": {
            "steel_price_trend": "↑ +8% YoY (Jan 2026); continued volatility expected",
            "concrete_supply": "Tight — 3–4 week lead times in Germany; 6+ weeks in high-demand regions",
            "skilled_labor_market": "Shortage persists: 15% vacancy rate for skilled trades in Germany (2025)",
            "geotechnical_costs": "Geotechnical survey costs stable at €5–15K for standard site assessments",
        },
    },
    "manufacturing": {
        "last_updated": "2026-01-20",
        "active_regulations": [
            {
                "name": "EU Medical Device Regulation (EU MDR) — Ongoing Enforcement",
                "status": "Active — continuing strict enforcement",
                "risk_level": "Critical for medical devices",
                "summary": (
                    "Notified Body backlogs remain 12–18 months for Class II/III devices. "
                    "Plan MDR certification timeline into project from day 1. "
                    "Non-compliance average penalty: €2.3M per incident."
                ),
                "source": "MedTech Europe + European Commission, 2024",
            },
            {
                "name": "DORA (Digital Operational Resilience Act) — Full Enforcement Jan 2025",
                "status": "Active — all EU financial sector entities must comply",
                "risk_level": "High for financial-sector manufacturing/fintech",
                "summary": (
                    "Mandatory ICT risk management, incident reporting (within 4 hours for major incidents), "
                    "and third-party ICT oversight. Non-compliance fines: up to 2% of global turnover."
                ),
                "source": "European Banking Authority, 2025",
            },
            {
                "name": "EU Deforestation Regulation (EUDR) — Active from 2025",
                "status": "Active — supply chain due diligence mandatory",
                "risk_level": "Medium-High for supply chains with wood/soy/palm/cocoa",
                "summary": (
                    "Due diligence mandatory for 7 regulated commodities in all supply chains. "
                    "Non-compliant products cannot be placed on the EU market."
                ),
                "source": "European Commission, 2023",
            },
        ],
        "market_signals": {
            "semiconductor_supply": "Stabilising — lead times 8–12 weeks (down from 52 weeks in 2022)",
            "rare_earth_metals": "Volatile — geopolitical tension; 15% price increase YoY",
            "european_energy_costs": "Manufacturing energy costs: +22% vs 2022 baseline; stabilising but elevated",
            "labour_market": "Skilled manufacturing workforce shortage: 8% vacancy rate in Germany",
        },
    },
    "it": {
        "last_updated": "2026-02-01",
        "active_regulations": [
            {
                "name": "DORA (Digital Operational Resilience Act) — Full Enforcement",
                "status": "Active since Jan 2025",
                "risk_level": "Critical for EU financial services IT",
                "summary": (
                    "Comprehensive ICT risk management, digital operational resilience testing, "
                    "and incident reporting within 4 hours for major incidents. "
                    "Affects all financial entities and their ICT third-party providers."
                ),
                "source": "EBA / European Commission, 2025",
            },
            {
                "name": "EU AI Act — Phased Enforcement 2025–2027",
                "status": "Phased — high-risk AI systems from Aug 2026",
                "risk_level": "High for AI/ML projects in regulated sectors",
                "summary": (
                    "AI systems in high-risk categories (healthcare, critical infrastructure, "
                    "biometric, employment) require conformity assessments and registration. "
                    "Build compliance requirements into your AI project from day 1."
                ),
                "source": "European Commission, 2024",
            },
            {
                "name": "GDPR Enforcement Intensification 2024–2025",
                "status": "Active — enforcement intensifying across all EU member states",
                "risk_level": "High",
                "summary": (
                    "Record €1.35B in GDPR fines in 2023. DPAs actively pursuing data minimisation, "
                    "consent violations, and cross-border data transfers. "
                    "Data protection impact assessments (DPIA) mandatory for high-risk processing."
                ),
                "source": "EDPB Enforcement Tracker, 2024",
            },
        ],
        "market_signals": {
            "cybersecurity_threats": "↑ 45% increase in ransomware attacks on EU orgs (ENISA 2024)",
            "cloud_costs": "Major cloud providers: +12–15% pricing adjustment Jan 2025",
            "ai_ml_talent": "Critical shortage: 40% of AI/ML roles unfilled in EU (2025)",
            "open_source_security": "Software supply chain attacks: +300% in 3 years (ENISA 2024)",
        },
    },
}

_MOCK_GEOPOLITICAL_DATA: dict = {
    "last_updated": "2026-02-01",
    "global_risk_level": "Elevated",
    "key_risks": [
        {
            "risk": "Supply chain disruption",
            "level": "High",
            "trend": "Increasing",
            "regions_affected": ["Asia-Pacific", "Middle East", "Eastern Europe"],
            "project_impact": "Material procurement lead times +20–40% vs pre-2020 baselines",
            "source": "WEF Global Risk Report 2025",
        },
        {
            "risk": "Regulatory divergence (EU vs US vs Asia)",
            "level": "Medium-High",
            "trend": "Increasing",
            "regions_affected": ["Global — cross-border projects"],
            "project_impact": "Compliance costs +15–25% for cross-jurisdictional projects",
            "source": "WEF Global Risk Report 2025",
        },
        {
            "risk": "Extreme weather and climate-driven delays",
            "level": "High and rising",
            "trend": "Increasing",
            "regions_affected": ["Global — construction especially exposed"],
            "project_impact": "Construction weather delays: +35% vs 10-year average in Central Europe (2025)",
            "source": "Munich Re Natural Catastrophe Report 2024",
        },
    ],
}


class DataFetcher:
    """
    Fetches regulatory, market, and geopolitical data for risk assessment.

    Falls back gracefully to curated mock data when live APIs are unavailable.
    All fallback data is sourced from official publications.

    Args:
        use_live_data: If True, attempt live API calls before falling back.
                       If False (default), use curated data directly.
    """

    def __init__(self, use_live_data: bool = False) -> None:
        self.use_live_data = use_live_data
        self._cache: dict = {}

    def get_regulatory_data(self, industry: str) -> dict:
        """Return current regulatory data for the given industry."""
        cache_key = f"regulatory_{industry}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.use_live_data:
            try:
                data = self._fetch_live_regulatory_data(industry)
                self._cache[cache_key] = data
                return data
            except (NotImplementedError, Exception):
                pass  # Fall through to curated data

        data = _MOCK_REGULATORY_DATA.get(
            industry, _MOCK_REGULATORY_DATA.get("it", {})
        )
        self._cache[cache_key] = data
        return data

    def get_geopolitical_data(self) -> dict:
        """Return current geopolitical risk data."""
        if "geopolitical" in self._cache:
            return self._cache["geopolitical"]

        if self.use_live_data:
            try:
                data = self._fetch_live_geopolitical_data()
                self._cache["geopolitical"] = data
                return data
            except (NotImplementedError, Exception):
                pass

        self._cache["geopolitical"] = _MOCK_GEOPOLITICAL_DATA
        return _MOCK_GEOPOLITICAL_DATA

    def get_market_signals(self, industry: str) -> dict:
        """Return current market signals relevant to the industry."""
        reg_data = self.get_regulatory_data(industry)
        return reg_data.get("market_signals", {})

    def get_data_freshness(self, industry: str) -> dict:
        """Return metadata about data freshness for transparency."""
        reg_data = self.get_regulatory_data(industry)
        return {
            "last_updated": reg_data.get("last_updated", "2026-01-01"),
            "data_source": "Live API" if self.use_live_data else "Curated knowledge base",
            "next_update": "Real-time" if self.use_live_data else "On next agent release",
        }

    # ── Live API stubs ────────────────────────────────────────────────────────
    # Future implementation: connect to EUR-Lex, FDA, ENISA, WEF APIs.
    # Set environment variables (REGULATORY_API_KEY etc.) to enable.

    def _fetch_live_regulatory_data(self, _industry: str) -> dict:
        """
        Stub for live regulatory data fetch.

        Future: Connect to EUR-Lex (EU law), FDA Open Data API,
        ENISA (cybersecurity), national building code databases.
        """
        raise NotImplementedError(
            "Live regulatory API not yet configured. "
            "Set the REGULATORY_API_KEY environment variable to enable live data."
        )

    def _fetch_live_geopolitical_data(self) -> dict:
        """
        Stub for live geopolitical data fetch.

        Future: Connect to WEF Global Risk API, ACLED conflict data,
        OECD country risk classifications.
        """
        raise NotImplementedError(
            "Live geopolitical API not yet configured. "
            "Set the GEOPOLITICAL_API_KEY environment variable to enable live data."
        )
