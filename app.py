"""
Flask web interface for the Project Risk Assessment Agent.

Run with:
    python app.py

Then open http://localhost:5000 in your browser.
"""
from __future__ import annotations

import io
import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from agent.knowledge_base import CULTURAL_ARCHETYPES
from agent.risk_agent import RiskAssessmentAgent

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "risk-assessment-dev-key-change-in-production")

# ── Helpers ───────────────────────────────────────────────────────────────────

_INDUSTRY_MAP = {
    "construction": "construction",
    "manufacturing": "manufacturing",
    "it": "it",
}

_LOCUS_MAP = {
    "internal": "internal",
    "external": "external",
    "mixed": "mixed",
}

_STYLE_MAP = {
    "intuition": "intuition",
    "balance": "balance",
    "formal_tools": "formal_tools",
}

_LEVEL_ICONS = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
}


def _build_report_from_session():
    """Rebuild the AssessmentReport from form data stored in the session."""
    form_data = session.get("form_data")
    if not form_data:
        return None, None

    agent = RiskAssessmentAgent()
    ctx = agent.build_context(
        industry=form_data["industry"],
        years_experience=form_data["years_experience"],
        projects_managed=form_data["projects_managed"],
        cultural_region=form_data["cultural_region"],
        top_risks=form_data["top_risks"],
        risk_locus=form_data["risk_locus"],
        decision_style=form_data["decision_style"],
        time_pressure=form_data["time_pressure"],
    )
    report = agent.generate_report(ctx, fetch_live_data=False)
    return ctx, report


# ── Routes ────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Home page with project introduction and Start Assessment button."""
    return render_template("index.html")


@app.route("/interview")
def interview():
    """Interview form page."""
    prefill = session.get("form_data", {})
    return render_template("interview.html", prefill=prefill)


@app.route("/generate-report", methods=["POST"])
def generate_report():
    """Process form submission and store validated data in session."""
    industry = _INDUSTRY_MAP.get(request.form.get("industry", ""), "construction")

    try:
        years_experience = int(request.form.get("years_experience", 0))
        years_experience = max(0, min(years_experience, 60))
    except (ValueError, TypeError):
        years_experience = 0

    try:
        projects_managed = int(request.form.get("projects_managed", 0))
        projects_managed = max(0, min(projects_managed, 500))
    except (ValueError, TypeError):
        projects_managed = 0

    cultural_region = request.form.get("cultural_region", "Germany").strip() or "Germany"

    top_risks: list[str] = []
    for i in range(1, 4):
        risk_text = request.form.get(f"risk{i}", "").strip()
        if risk_text:
            top_risks.append(risk_text)

    risk_locus = _LOCUS_MAP.get(request.form.get("risk_locus", ""), "mixed")
    decision_style = _STYLE_MAP.get(request.form.get("decision_style", ""), "balance")

    time_pressure = request.form.get("time_pressure", "medium").lower()
    if time_pressure not in ("low", "medium", "high"):
        time_pressure = "medium"

    session["form_data"] = {
        "industry": industry,
        "years_experience": years_experience,
        "projects_managed": projects_managed,
        "cultural_region": cultural_region,
        "top_risks": top_risks,
        "risk_locus": risk_locus,
        "decision_style": decision_style,
        "time_pressure": time_pressure,
    }

    return redirect(url_for("report"))


@app.route("/report")
def report():
    """Display the generated risk assessment report."""
    ctx, assessment = _build_report_from_session()
    if assessment is None:
        return redirect(url_for("index"))

    arch = CULTURAL_ARCHETYPES.get(ctx.cultural_region)

    critical_count = sum(1 for r in assessment.risk_register if r.level == "Critical")
    high_count = sum(1 for r in assessment.risk_register if r.level == "High")
    medium_count = sum(1 for r in assessment.risk_register if r.level == "Medium")
    low_count = sum(1 for r in assessment.risk_register if r.level == "Low")

    return render_template(
        "report.html",
        report=assessment,
        ctx=ctx,
        arch=arch,
        level_icons=_LEVEL_ICONS,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
    )


@app.route("/download-pdf")
def download_pdf():
    """Generate and download the report as a PDF using reportlab."""
    ctx, assessment = _build_report_from_session()
    if assessment is None:
        return redirect(url_for("index"))

    try:
        from reportlab.lib import colors  # type: ignore[import-untyped]
        from reportlab.lib.enums import TA_CENTER  # type: ignore[import-untyped]
        from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
        from reportlab.lib.units import mm  # type: ignore[import-untyped]
        from reportlab.platypus import (  # type: ignore[import-untyped]
            HRFlowable,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title="Project Risk Assessment Report",
            author="Risk Assessment Agent",
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=4,
            textColor=colors.HexColor("#2c3e50"),
        )
        heading1_style = ParagraphStyle(
            "ReportH1",
            parent=styles["Heading1"],
            fontSize=13,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor("#2c3e50"),
        )
        caption_style = ParagraphStyle(
            "Caption",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )

        story = []

        # Title block
        story.append(Paragraph("Project Risk Assessment Report", title_style))
        story.append(
            Paragraph(
                f"Industry: <b>{ctx.industry.title()}</b> &nbsp;|&nbsp; "
                f"Experience: <b>{ctx.experience_level.title()}</b> &nbsp;|&nbsp; "
                f"Time Pressure: <b>{ctx.time_pressure.title()}</b>",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 6 * mm))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#2c3e50")))
        story.append(Spacer(1, 4 * mm))

        # Executive summary
        story.append(Paragraph("Executive Summary", heading1_style))
        for line in assessment.summary.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), styles["Normal"]))
        story.append(Spacer(1, 4 * mm))

        # Risk Register
        story.append(Paragraph("Risk Register", heading1_style))
        header_row = ["#", "Description", "Category", "Level", "Score", "Recommended Action"]
        table_data = [header_row]

        level_bg = {
            "Critical": colors.HexColor("#e74c3c"),
            "High": colors.HexColor("#e67e22"),
            "Medium": colors.HexColor("#f1c40f"),
            "Low": colors.HexColor("#2ecc71"),
        }

        for i, risk in enumerate(assessment.risk_register, 1):
            desc = risk.description if len(risk.description) <= 70 else risk.description[:67] + "..."
            action = risk.action if len(risk.action) <= 60 else risk.action[:57] + "..."
            table_data.append([str(i), desc, risk.category, risk.level, str(risk.score), action])

        col_widths = [8 * mm, 58 * mm, 24 * mm, 18 * mm, 12 * mm, 46 * mm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        ts = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
        for i, risk in enumerate(assessment.risk_register, 1):
            bg = level_bg.get(risk.level, colors.white)
            ts.add("BACKGROUND", (3, i), (3, i), bg)
            if risk.level in ("Critical", "High"):
                ts.add("TEXTCOLOR", (3, i), (3, i), colors.white)
        table.setStyle(ts)
        story.append(table)
        story.append(Spacer(1, 4 * mm))

        # First 20% Action Checklist
        ind_data = assessment.industry_risks
        actions = ind_data.get("first_20_percent_actions", [])
        if actions:
            story.append(Paragraph(f"First 20% Action Checklist — {ctx.industry.title()}", heading1_style))
            for action in actions:
                story.append(Paragraph(f"☐  {action}", styles["Normal"]))
            story.append(Spacer(1, 4 * mm))

        # Footer
        story.append(HRFlowable(width="100%", color=colors.HexColor("#2c3e50")))
        story.append(Spacer(1, 2 * mm))
        story.append(
            Paragraph(
                "Generated by Project Risk Assessment Agent &nbsp;|&nbsp; "
                "Thesis: <i>Understanding Risk Awareness and Decision Making in "
                "Early-Stage Project Planning</i> — Devarshi Kansara, HDBW 2026",
                caption_style,
            )
        )

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="risk_assessment_report.pdf",
            mimetype="application/pdf",
        )

    except ImportError:
        # reportlab not installed — fall back to plain text
        lines = ["Project Risk Assessment Report", "=" * 40, "", assessment.summary, ""]
        lines += ["Risk Register", "-" * 40]
        for i, risk in enumerate(assessment.risk_register, 1):
            lines.append(f"{i}. [{risk.level}] {risk.description}")
            lines.append(f"   Score: {risk.score} | Category: {risk.category}")
            lines.append(f"   Action: {risk.action}")
            lines.append("")
        content = "\n".join(lines)
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            as_attachment=True,
            download_name="risk_assessment_report.txt",
            mimetype="text/plain",
        )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
