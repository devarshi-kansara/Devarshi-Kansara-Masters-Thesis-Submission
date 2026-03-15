"""
Data models for the risk assessment agent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RiskItem:
    """Represents a single identified risk."""

    description: str
    category: str  # "external" | "internal" | "cross-cultural"
    probability: str  # "low" | "medium" | "high"
    impact: str  # "low" | "medium" | "high" | "critical"
    detectability: str  # "early" | "late" | "post_occurrence"
    owner: Optional[str] = None
    mitigation: Optional[str] = None
    score: int = 0
    level: str = ""
    action: str = ""
    # Live-data enrichment fields (populated by InternetDataFetcher)
    recent_news_link: Optional[str] = None   # URL of a related recent news article
    recent_news_title: Optional[str] = None  # Article headline
    recent_news_date: Optional[str] = None   # Publication date
    regulatory_status: Optional[str] = None  # Current compliance note
    market_signal: Optional[str] = None      # Price / labour trend snippet
    academic_citation: Optional[str] = None  # APA-style citation with URL
    # ECC-sourced enrichment fields (populated by EccResearchBridge when available)
    ecc_research_papers: List[Dict[str, str]] = field(default_factory=list)
    ecc_market_validation: Dict[str, Any] = field(default_factory=dict)
    ecc_confidence_score: Optional[float] = None

    def __post_init__(self) -> None:
        from agent.knowledge_base import get_risk_level

        result = get_risk_level(self.probability, self.impact, self.detectability)
        self.score = result["score"]
        self.level = result["level"]
        self.action = result["action"]


@dataclass
class ProjectContext:
    """Captures the context gathered during the agent interview."""

    industry: str = ""  # "construction" | "manufacturing" | "it"
    years_experience: int = 0
    projects_managed: int = 0
    experience_level: str = ""  # "junior" | "mid" | "senior"
    cultural_region: str = ""  # "process_guardian" | "resource_navigator" | "mixed"
    top_risks: List[str] = field(default_factory=list)
    risk_locus: str = ""  # "internal" | "external" | "mixed"
    decision_style: str = ""  # "intuition" | "balance" | "formal_tools"
    time_pressure: str = ""  # "low" | "medium" | "high"
    identified_risks: List[RiskItem] = field(default_factory=list)

    def classify_experience(self) -> str:
        if self.years_experience <= 3:
            level = "junior"
        elif self.years_experience <= 10:
            level = "mid"
        else:
            level = "senior"
        self.experience_level = level
        return level


@dataclass
class AssessmentReport:
    """Full output of the agent's assessment."""

    context: ProjectContext
    industry_risks: dict
    experience_guidance: dict
    framework_recommendations: List[dict]
    reality_check_plan: dict
    risk_register: List[RiskItem]
    summary: str = ""
    # Live-data enrichment (populated when InternetDataFetcher is available)
    live_data_timestamp: Optional[str] = None   # ISO-8601 UTC timestamp
    data_sources_used: List[str] = field(default_factory=list)
    regulatory_updates: List[dict] = field(default_factory=list)
    industry_news: List[dict] = field(default_factory=list)
    market_signals: dict = field(default_factory=dict)
    academic_research: List[dict] = field(default_factory=list)
    geopolitical_alerts: List[dict] = field(default_factory=list)
