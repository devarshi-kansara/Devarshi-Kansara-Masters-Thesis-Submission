"""
Data models for the risk assessment agent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
    # ── Personalisation fields (Phase 1) ─────────────────────────────────────
    benchmark: Optional[Dict] = None
    """Frequency / success / failure / cost benchmark data for this risk type."""
    blind_spot: Optional[str] = None
    """Specific blind-spot warning for the user's profile (region + experience)."""
    novel_mitigation: Optional[str] = None
    """Cross-industry or novel mitigation insight beyond the standard action."""
    academic_source: Optional[str] = None
    """Academic citation supporting the risk identification or mitigation."""
    cross_industry_insight: Optional[str] = None
    """Pattern or technique from another industry that applies to this risk."""
    confidence: float = 0.85
    """Confidence level (0–1) for this risk's scoring and recommendations."""

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
    # ── Personalisation fields (Phase 1) ─────────────────────────────────────
    persona_profile: Optional[Dict] = None
    """Deep persona analysis from ContextAnalyzer."""
    benchmarks: Optional[Dict] = None
    """Industry benchmarks by risk type from ContextAnalyzer."""
    frameworks_with_rationale: List[dict] = field(default_factory=list)
    """Frameworks enriched with WHY for this specific user."""
    cultural_insights: Optional[Dict] = None
    """Region-specific insights and cultural risk patterns."""
    consultant_narrative: Optional[str] = None
    """Formatted narrative consultant report."""
