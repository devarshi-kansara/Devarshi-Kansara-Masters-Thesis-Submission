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


def _demo_run() -> None:
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
    args = parser.parse_args()

    if args.demo:
        _demo_run()
    else:
        agent = RiskAssessmentAgent()
        try:
            agent.run_interactive_session()
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
