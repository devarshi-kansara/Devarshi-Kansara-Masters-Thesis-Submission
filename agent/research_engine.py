"""
Research Engine — Phase 1 specialist module.

Provides pre-curated academic citations and cross-industry pattern insights
derived from the thesis research base.  No external API calls are required.
"""
from __future__ import annotations

from typing import List

from agent.models import ProjectContext, RiskItem

# ── Pre-curated research citations (APA format) ───────────────────────────────
_CITATIONS: dict = {
    "construction": [
        (
            "Flyvbjerg, B., Holm, M. K. S., & Buhl, S. L. (2002). Underestimating costs in "
            "public works projects: Error or Lie? *Journal of the American Planning Association*, "
            "68(3), 279–295. https://doi.org/10.1080/01444360208976273"
        ),
        (
            "Straub, D. (2011). Reliability updating with equality information. "
            "*Probabilistic Engineering Mechanics*, 26(2), 254–258. "
            "https://doi.org/10.1016/j.probengmech.2010.08.003"
        ),
        (
            "Sullivan, T. J., & Jakeman, A. J. (2020). Uncertainty quantification in "
            "early-stage engineering projects. *Reliability Engineering & System Safety*, "
            "196, 106770. https://doi.org/10.1016/j.ress.2019.106770"
        ),
        (
            "Lind, P. (2012). Risk management in construction: the first 20% lifecycle phase. "
            "*Construction Management and Economics*, 30(9), 781–795. "
            "https://doi.org/10.1080/01446193.2012.714373"
        ),
    ],
    "manufacturing": [
        (
            "Jain, V., & Benyoucef, L. (2008). Managing long supply chain networks: "
            "some emerging issues and challenges. *Journal of Manufacturing Technology "
            "Management*, 19(4), 469–496. https://doi.org/10.1108/17410380810869650"
        ),
        (
            "Aven, T. (2016). Risk assessment and risk management: Review of recent "
            "advances on their foundation. *European Journal of Operational Research*, "
            "253(1), 1–13. https://doi.org/10.1016/j.ejor.2015.12.023"
        ),
        (
            "Stamatis, D. H. (2003). *Failure mode and effect analysis: FMEA from theory "
            "to execution* (2nd ed.). ASQ Quality Press."
        ),
        (
            "Lee, H. L. (2004). The triple-A supply chain. *Harvard Business Review*, "
            "82(10), 102–112."
        ),
    ],
    "it": [
        (
            "Standish Group. (2020). *CHAOS Report 2020: Beyond Infinity*. "
            "The Standish Group International."
        ),
        (
            "Boehm, B. W., & Turner, R. (2004). *Balancing agility and discipline: "
            "A guide for the perplexed*. Addison-Wesley."
        ),
        (
            "Charette, R. N. (2005). Why software fails. *IEEE Spectrum*, 42(9), 42–49. "
            "https://doi.org/10.1109/MSPEC.2005.1502528"
        ),
        (
            "Glass, R. L. (1998). *Software runaways: Monumental software disasters*. "
            "Prentice Hall."
        ),
    ],
    "general": [
        (
            "Kahneman, D. (2011). *Thinking, fast and slow*. Farrar, Straus and Giroux."
        ),
        (
            "Klein, G. (2007). Performing a project premortem. *Harvard Business Review*, "
            "85(9), 18–19."
        ),
        (
            "Taleb, N. N. (2007). *The black swan: The impact of the highly improbable*. "
            "Random House."
        ),
        (
            "PMI. (2021). *A guide to the project management body of knowledge (PMBOK® Guide)* "
            "(7th ed.). Project Management Institute."
        ),
    ],
}

# ── Cross-industry pattern insights ──────────────────────────────────────────
_CROSS_INDUSTRY_INSIGHTS: dict = {
    "construction": [
        (
            "Semiconductor fabs use 'process window qualification' — deliberate stress tests "
            "to probe material limits before production begins. Adapt this: commission a "
            "geotechnical stress report (worst-case scenario) before any foundation commitment."
        ),
        (
            "Aviation maintenance uses 'no-fault-found' protocols to surface latent failures "
            "that show no immediate symptoms. Apply this mindset to sub-contractor kick-off: "
            "run a structured technical audit even when everything looks fine."
        ),
    ],
    "manufacturing": [
        (
            "Construction mega-projects use 'Early Warning Systems' (NEC4 Contract): "
            "any party can raise a formal early warning without liability. Implement this "
            "in your production team — reward early escalation, never punish it."
        ),
        (
            "Nuclear power plants use 'defence-in-depth' — independent redundant checks "
            "at every safety boundary. Apply this to calibration: three independent "
            "measurement systems for any tolerance-critical dimension."
        ),
    ],
    "it": [
        (
            "Formula 1 pit crews use 'cognitive chunking' to reduce complex multi-step "
            "procedures into rehearsed muscle memory. Apply this to your deployment "
            "pipeline: reduce go-live to a single command with pre-validated checklists."
        ),
        (
            "Financial trading systems implement 'circuit breakers' that halt automated "
            "processes when anomalies exceed thresholds. Implement automated test gates "
            "that block deployment if error rates or performance metrics degrade."
        ),
    ],
}


class ResearchEngine:
    """Provides citations and cross-industry insights for a given context."""

    def get_citations(self, ctx: ProjectContext) -> List[str]:
        """Return a list of APA-formatted citations relevant to the project context."""
        industry_citations = _CITATIONS.get(ctx.industry, [])
        general_citations = _CITATIONS["general"]
        # Return industry-specific first, then general (deduplicated)
        seen: set = set()
        result: List[str] = []
        for c in industry_citations + general_citations:
            if c not in seen:
                seen.add(c)
                result.append(c)
        return result

    def get_cross_industry_insights(self, ctx: ProjectContext) -> List[str]:
        """Return cross-industry pattern insights applicable to the project context."""
        return _CROSS_INDUSTRY_INSIGHTS.get(ctx.industry, [])
