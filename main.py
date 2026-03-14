#!/usr/bin/env python3
"""
CLI entry point for the Project Risk Assessment Agent.

Run with:
    python main.py               # interactive interview mode
    python main.py --demo        # run with built-in demo data (no user input)
"""
from __future__ import annotations

import argparse
import sys

from agent.risk_agent import RiskAssessmentAgent


def _demo_run(verbose: bool = False) -> None:
    """Run the agent with pre-filled demo data and print the report."""
    agent = RiskAssessmentAgent()
    ctx = agent.build_context(
        industry="construction",
        years_experience=8,
        projects_managed=15,
        cultural_region="Germany",
        top_risks=[
            "Unexpected soil conditions delaying foundation work",
            "Permit approval delays from local authority",
            "Key subcontractor going over budget",
        ],
        risk_locus="external",
        decision_style="balance",
        time_pressure="high",
    )
    report = agent.generate_report(ctx)
    RiskAssessmentAgent._print_banner()

    if verbose:
        # Show persona profile and benchmarks in verbose mode
        print("\n" + "═" * 60)
        print("  VERBOSE: DATA SOURCES USED IN THIS REPORT")
        print("═" * 60)
        if report.persona_profile:
            persona = report.persona_profile
            print(f"\nArchetype: {persona.get('archetype', 'Unknown')}")
            print(f"Experience Level: {persona.get('experience_level', 'Unknown')}")
            print("\nStrengths:")
            for s in persona.get("strengths", []):
                print(f"  ✅ {s}")
            print("\nBlind Spots:")
            for bs in persona.get("blind_spots", []):
                print(f"  ⚠  {bs}")
            exp_bs = persona.get("experience_blind_spot", "")
            if exp_bs:
                print(f"\nSpecific Blind Spot:\n  → {exp_bs}")
        if report.benchmarks:
            print("\n\nIndustry Benchmarks Used:")
            default_bm = report.benchmarks.get("default", {})
            print(f"  Default: {default_bm.get('frequency', '—')} frequency | "
                  f"{default_bm.get('success_rate', '—')} recovery rate")
            cohort = report.benchmarks.get("_cohort_note", "")
            if cohort:
                print(f"\nCohort Note:\n  {cohort}")
        print("\nData Sources:")
        print("  • Kansara, D. (2026). HDBW Master's Thesis")
        print("  • PMI Pulse of the Profession (2023)")
        print("  • Dodge Data & Analytics Construction Outlook (2024)")
        print("  • Gartner Manufacturing Technology Survey (2023)")
        print("  • McKinsey IT Project Research (2023)")
        print("═" * 60 + "\n")

    RiskAssessmentAgent._print_report(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project Risk Assessment Agent — thesis-derived tool for early-stage PM risk identification."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demo assessment with pre-filled data (no interactive input required).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show data sources, persona profile, and benchmarks used in report generation.",
    )
    args = parser.parse_args()

    if args.demo:
        _demo_run(verbose=args.verbose)
    else:
        agent = RiskAssessmentAgent()
        try:
            agent.run_interactive_session()
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
