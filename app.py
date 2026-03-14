"""
Streamlit web interface for the Project Risk Assessment Agent.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from agent.consultant_report import ConsultantReportGenerator
from agent.knowledge_base import CULTURAL_ARCHETYPES, DECISION_FRAMEWORKS, REALITY_CHECK_FRAMEWORK
from agent.risk_agent import RiskAssessmentAgent

st.set_page_config(
    page_title="Project Risk Assessment Agent",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏗 Risk Assessment Agent")
    st.caption(
        "Based on the thesis:\n"
        "*Understanding Risk Awareness and Decision Making in "
        "Early-Stage Project Planning*\n\n"
        "Devarshi Kansara — HDBW, 2026"
    )
    st.divider()
    st.info(
        "Fill in the form on the right to receive a personalised "
        "risk assessment for the **critical first 20%** of your project."
    )

# ── Page header ───────────────────────────────────────────────────────────────
st.title("📋 Early-Stage Project Risk Assessment")
st.subheader("First 20% Risk Identification Tool")
st.markdown(
    "Research shows that **~70% of project failures** are caused by decisions "
    "made in the first 20% of the project lifecycle. This tool helps you identify, "
    "prioritise, and address risks *before* they become physically irreversible."
)
st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("risk_form"):
    st.subheader("Section 1 — Your Background")
    col1, col2, col3 = st.columns(3)
    with col1:
        industry = st.selectbox(
            "Industry",
            ["Construction", "Manufacturing", "IT / Software"],
            help="Select the industry of your current project.",
        )
    with col2:
        years_experience = st.slider("Years of PM experience", 0, 40, 5)
    with col3:
        projects_managed = st.slider("Projects managed to completion", 0, 100, 10)

    cultural_region = st.text_input(
        "Primary work region / country",
        value="Germany",
        help="Used to identify your cultural risk archetype (e.g., Germany, India, USA).",
    )

    st.subheader("Section 2 — Early Risk Focus")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        risk1 = st.text_input("Top Risk #1", placeholder="e.g., unexpected soil conditions")
    with col_b:
        risk2 = st.text_input("Top Risk #2", placeholder="e.g., permit delays")
    with col_c:
        risk3 = st.text_input("Top Risk #3", placeholder="e.g., subcontractor overruns")

    risk_locus = st.radio(
        "These risks are mostly:",
        ["Inside the project (controllable)", "Outside the project (uncontrollable)", "A mix of both"],
        horizontal=True,
    )

    st.subheader("Section 3 — Intuition vs. Tools")
    decision_style = st.radio(
        "When deciding which risks to take seriously, you rely on:",
        ["Mostly experience and intuition", "A balance of intuition and tools", "Mostly formal tools and methods"],
        horizontal=True,
        index=1,
    )

    st.subheader("Section 4 — Time Pressure")
    time_pressure = st.select_slider(
        "Time pressure at project start",
        options=["Low", "Medium", "High"],
        value="Medium",
    )

    submitted = st.form_submit_button("🔍 Generate Risk Assessment", use_container_width=True)

# ── Process & display report ──────────────────────────────────────────────────
if submitted:
    # Map form values to agent keys
    industry_map = {"Construction": "construction", "Manufacturing": "manufacturing", "IT / Software": "it"}
    locus_map = {
        "Inside the project (controllable)": "internal",
        "Outside the project (uncontrollable)": "external",
        "A mix of both": "mixed",
    }
    style_map = {
        "Mostly experience and intuition": "intuition",
        "A balance of intuition and tools": "balance",
        "Mostly formal tools and methods": "formal_tools",
    }

    top_risks = [r for r in [risk1, risk2, risk3] if r.strip()]

    agent = RiskAssessmentAgent()
    ctx = agent.build_context(
        industry=industry_map[industry],
        years_experience=years_experience,
        projects_managed=projects_managed,
        cultural_region=cultural_region,
        top_risks=top_risks,
        risk_locus=locus_map[risk_locus],
        decision_style=style_map[decision_style],
        time_pressure=time_pressure.lower(),
    )
    report = agent.generate_report(ctx)
    consultant_gen = ConsultantReportGenerator()
    consultant_insights = consultant_gen.generate(ctx, report)

    st.success("✅ Assessment complete! Scroll down to review your personalised risk report.")
    st.divider()

    # ── Summary ──────────────────────────────────────────────────────────────
    st.header("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    critical_count = sum(1 for r in report.risk_register if r.level == "Critical")
    high_count = sum(1 for r in report.risk_register if r.level == "High")
    medium_count = sum(1 for r in report.risk_register if r.level == "Medium")
    low_count = sum(1 for r in report.risk_register if r.level == "Low")

    col1.metric("🔴 Critical", critical_count)
    col2.metric("🟠 High", high_count)
    col3.metric("🟡 Medium", medium_count)
    col4.metric("🟢 Low", low_count)

    if critical_count > 0:
        st.error(
            f"⚠️ **STOP-AND-FIX**: You have {critical_count} Critical risk(s). "
            "Do not proceed until these are resolved or formally accepted by your sponsor."
        )

    # ── Consultant Insights ───────────────────────────────────────────────────
    st.header("🧠 Consultant Insights")
    st.markdown(
        "Industry-specific analysis generated by the Phase 1 specialist modules. "
        "This section is personalised to your profile, industry, and project context."
    )

    # Persona analysis
    persona = consultant_insights["persona_analysis"]
    with st.expander("👤 Your Persona Profile & Blind Spots", expanded=True):
        st.markdown(f"**Archetype:** {persona.get('archetype', '')}")
        col_s, col_b = st.columns(2)
        with col_s:
            st.markdown("**Strengths ✅**")
            for s in persona.get("strengths", []):
                st.markdown(f"- {s}")
        with col_b:
            st.markdown("**Blind Spots ⚠️**")
            for bs in persona.get("blind_spots", []):
                st.warning(bs)
        st.markdown(f"**Decision Pattern:** {persona.get('decision_pattern', '')}")
        st.markdown(f"**Risk Tolerance:** {persona.get('risk_tolerance', '')}")
        if persona.get("time_pressure_note"):
            st.error(persona["time_pressure_note"])

    # Industry benchmarks
    benchmarks = consultant_insights["industry_benchmarks"]
    if benchmarks:
        with st.expander("📊 Industry Benchmarks — How You Compare"):
            for key, data in benchmarks.items():
                st.subheader(data.get("label", key))
                b1, b2 = st.columns(2)
                b1.markdown(f"**Frequency:** {data.get('frequency', '')}")
                b1.markdown(f"**Success rate:** {data.get('success_rate', '')}")
                b2.markdown(f"**Mitigation cost:** {data.get('typical_mitigation_cost', '')}")
                b2.markdown(f"**Failure cost:** {data.get('typical_failure_cost', '')}")
                st.divider()

    # Blind spots specific to this profile + industry
    all_blind_spots = consultant_insights["blind_spots"]
    if all_blind_spots:
        with st.expander("⚡ Blind Spots Specific to Your Profile & Industry"):
            for bs in all_blind_spots:
                st.warning(bs)

    # Recommended frameworks with rationale
    rec_frameworks = consultant_insights["recommended_frameworks"]
    if rec_frameworks:
        with st.expander("🧰 Recommended Frameworks — Personalised Rationale"):
            for fw in rec_frameworks:
                st.subheader(f"▸ {fw['name']}")
                st.markdown(fw.get("description", ""))
                st.markdown(f"**Why this matters for you:** {fw.get('rationale', '')}")
                st.markdown(f"**Blind spot addressed:** {fw.get('blind_spot_addressed', '')}")
                st.markdown(f"**When to apply:** {fw.get('when_to_apply', '')}")
                st.markdown(f"*Example: {fw.get('example', '')}*")
                st.divider()

    # Black swan warnings
    black_swans = consultant_insights["black_swan_warnings"]
    if black_swans:
        with st.expander("🦢 Black Swan Warnings — Low-Probability, High-Impact"):
            for warning in black_swans:
                st.error(warning)

    # Regulatory intelligence
    reg_intel = consultant_insights["regulatory_intelligence"]
    if reg_intel:
        with st.expander("⚖️ Regulatory Intelligence"):
            for item in reg_intel:
                st.info(item)

    # Market signals
    market_signals = consultant_insights["market_signals"]
    if market_signals:
        with st.expander("📈 Market Signals"):
            for signal in market_signals:
                st.markdown(f"- {signal}")

    # Cross-industry insights
    cross_insights = consultant_insights["cross_industry_insights"]
    if cross_insights:
        with st.expander("🔀 Cross-Industry Insights"):
            for insight in cross_insights:
                st.markdown(f"- {insight}")

    # Research citations (APA format)
    citations = consultant_insights["research_citations"]
    if citations:
        with st.expander("📚 Research Citations (APA Format)"):
            for cite in citations:
                st.markdown(f"> {cite}")

    st.divider()

    # ── Risk Register ─────────────────────────────────────────────────────────
    st.header("📋 Risk Register")
    level_colors = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
    for i, risk in enumerate(report.risk_register, 1):
        icon = level_colors.get(risk.level, "⚪")
        with st.expander(f"{icon} #{i} [{risk.level}] — {risk.description}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Category:** {risk.category}")
            c2.markdown(f"**Probability:** {risk.probability}")
            c3.markdown(f"**Impact:** {risk.impact}")
            c4.markdown(f"**Risk Score:** {risk.score}")
            st.info(f"**Recommended Action:** {risk.action}")

    # ── Industry Context ──────────────────────────────────────────────────────
    st.header(f"🏗 Industry Context — {industry}")
    ind_data = report.industry_risks
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("External Risks")
        for r in ind_data.get("primary_external", []):
            st.markdown(f"- {r}")
    with col_r:
        st.subheader("Internal Risks")
        for r in ind_data.get("primary_internal", []):
            st.markdown(f"- {r}")

    st.subheader("⚡ Blind Spots for Outsiders")
    for r in ind_data.get("blind_spots_for_outsiders", []):
        st.warning(r)

    # ── Experience-Level Guidance ─────────────────────────────────────────────
    exp = report.experience_guidance
    st.header(f"👤 Guidance for {ctx.experience_level.title()} Project Managers")
    col_s, col_d = st.columns(2)
    with col_s:
        st.subheader("Your Strengths ✅")
        for s in exp.get("strengths", []):
            st.markdown(f"- {s}")
    with col_d:
        st.subheader("Development Areas 📌")
        for d in exp.get("development_areas", []):
            st.markdown(f"- {d}")

    st.subheader("Recommended Actions for the First 20%")
    for a in exp.get("recommended_actions", []):
        st.markdown(f"→ {a}")

    # ── Decision Frameworks ───────────────────────────────────────────────────
    st.header("🧰 Decision Frameworks")
    for fw in report.framework_recommendations:
        with st.expander(f"▸ {fw['name']}"):
            st.markdown(fw["description"])
            st.markdown(f"**When to apply:** {fw['when_to_apply']}")
            st.markdown(f"**Example:** *{fw['example']}*")

    # ── 20% Reality Check ────────────────────────────────────────────────────
    st.header("📅 Your 20% Reality Check Milestone")
    rc = report.reality_check_plan
    st.info(rc["description"])
    st.subheader("Workshop Agenda")
    for item in rc.get("agenda_items", []):
        st.checkbox(item, key=item)
    st.success(f"**Expected output:** {rc.get('output', '')}")

    # ── First 20% Action Checklist ────────────────────────────────────────────
    st.header(f"🚀 First 20% Action Checklist — {industry}")
    for action in ind_data.get("first_20_percent_actions", []):
        st.checkbox(action, key=action)

    # ── Cultural Archetype ────────────────────────────────────────────────────
    arch = CULTURAL_ARCHETYPES.get(ctx.cultural_region)
    if arch:
        st.header(f"🌍 Cultural Archetype: {ctx.cultural_region.replace('_', ' ').title()}")
        st.subheader("Characteristics")
        for c in arch.get("characteristics", []):
            st.markdown(f"- {c}")
        st.subheader("Blind Spots")
        for bs in arch.get("blind_spots", []):
            st.warning(bs)
        st.subheader("Development Recommendation")
        st.info(arch.get("recommended_development", ""))

    st.divider()
    st.caption(
        "Report generated by the **Project Risk Assessment Agent** | "
        "Thesis: *Understanding Risk Awareness and Decision Making in Early-Stage Project Planning* "
        "— Devarshi Kansara, HDBW 2026"
    )
