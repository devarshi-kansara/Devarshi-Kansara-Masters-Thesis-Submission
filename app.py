"""
Streamlit web interface for the Project Risk Assessment Agent.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

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

    # ── Consultant Profile & Confidence ──────────────────────────────────────
    ci = report.consultant_insights
    persona = ci.get("persona", {})
    confidence = ci.get("confidence", {})

    if persona or confidence:
        with st.container():
            st.header("🎭 Your Expert Consultant Profile")
            p_col, c_col = st.columns([2, 1])
            with p_col:
                if persona:
                    st.subheader(persona.get("persona", ""))
                    st.markdown(persona.get("description", ""))
                    blind_spots = persona.get("risk_blind_spots", [])
                    if blind_spots:
                        st.subheader("⚠️ Your Risk Blind Spots")
                        for bs in blind_spots:
                            st.warning(bs)
                    prescription = persona.get("prescription", "")
                    if prescription:
                        st.info(f"💊 **Prescription for you:** {prescription}")
            with c_col:
                if confidence:
                    score = confidence.get("score", 0)
                    label = confidence.get("label", "")
                    explanation = confidence.get("explanation", "")
                    st.metric("Confidence Level", f"{score}% ({label})")
                    st.caption(explanation)

    # ── Time Pressure Warning ─────────────────────────────────────────────────
    tp_insights = ci.get("time_pressure_insights", {})
    if tp_insights:
        st.header("⏱️ Time Pressure Intelligence")
        st.warning(tp_insights.get("risk_escalation_note", ""))
        st.info(tp_insights.get("behavioral_warning", ""))
        st.success(f"**Counter-strategy:** {tp_insights.get('counter_strategy', '')}")

    # ── Industry Benchmarks ───────────────────────────────────────────────────
    benchmarks = ci.get("benchmarks", {})
    if benchmarks:
        st.header("📈 Industry Benchmarks — Your Context")
        common_risks_pct = benchmarks.get("common_risks_pct", {})
        if common_risks_pct:
            st.subheader("How common are these risks in your industry + region?")
            for desc, pct in common_risks_pct.items():
                st.markdown(f"- **{pct}%** of PMs in your situation face: *{desc}*")
        failure_rate = benchmarks.get("failure_recovery_rate")
        if failure_rate:
            st.metric("Recovery Rate", f"{failure_rate}%", help="% of projects that recover from major risks")
        blind_spot = benchmarks.get("blind_spot", "")
        if blind_spot:
            st.subheader("🔍 Your Regional Blind Spot")
            st.warning(blind_spot)
        top_practices = benchmarks.get("top_performer_practices", [])
        if top_practices:
            st.subheader("🏆 What Top 10% of PMs Do Differently")
            for p in top_practices:
                st.markdown(f"✅ {p}")
        st.caption(f"Source: {benchmarks.get('source', 'Thesis research + industry reports')}")

    # ── Risk Register ─────────────────────────────────────────────────────────
    st.header("📋 Risk Register")
    level_colors = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
    enriched_risks = ci.get("enriched_risks", [])
    enriched_map = {er["risk"].description: er for er in enriched_risks}

    for i, risk in enumerate(report.risk_register, 1):
        icon = level_colors.get(risk.level, "⚪")
        with st.expander(f"{icon} #{i} [{risk.level}] — {risk.description}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Category:** {risk.category}")
            c2.markdown(f"**Probability:** {risk.probability}")
            c3.markdown(f"**Impact:** {risk.impact}")
            c4.markdown(f"**Risk Score:** {risk.score}")
            st.info(f"**Recommended Action:** {risk.action}")

            enriched = enriched_map.get(risk.description, {})
            context_note = enriched.get("context_note", "")
            if context_note:
                st.markdown(f"📍 **Context for you:** {context_note}")

            citations = enriched.get("citations", [])
            if citations:
                st.markdown("**📚 Research support:**")
                for cite in citations[:2]:
                    st.markdown(f"- *{cite['reference']}* — {cite['key_finding']}")

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
    frameworks_to_show = ci.get("frameworks") or report.framework_recommendations
    for fw in frameworks_to_show:
        tier = fw.get("tier", "")
        label = f"▸ {fw['name']}" + (f" [{tier}]" if tier else "")
        with st.expander(label):
            st.markdown(fw["description"])
            st.markdown(f"**When to apply:** {fw.get('when_to_apply', '')}")
            st.markdown(f"**Example:** *{fw.get('example', '')}*")
            if fw.get("academic_basis"):
                st.markdown(f"📚 **Academic basis:** {fw['academic_basis']}")
            if fw.get("context_note"):
                st.info(f"💡 **For you:** {fw['context_note']}")

    # ── Cross-Industry Innovations ────────────────────────────────────────────
    innovations = ci.get("innovations", [])
    if innovations:
        st.header("🔬 Novel Mitigations — Cross-Industry Pattern Recognition")
        for innov in innovations:
            with st.expander(f"💡 {innov['technique']} (from {innov['borrowed_from']})"):
                st.markdown(innov["description"])
                st.success(f"**ROI estimate:** {innov['roi_estimate']}")
                st.caption(f"Academic basis: {innov['academic_basis']}")

    # ── Black Swan Warning ────────────────────────────────────────────────────
    black_swan = ci.get("black_swan", {})
    if black_swan:
        st.header("🦢 Black Swan / Tail Risk Warning")
        with st.expander(f"⚠️ {black_swan.get('event', 'Unknown tail risk')}", expanded=False):
            st.markdown(f"**Example:** {black_swan.get('example', '')}")
            st.markdown(f"**Probability:** {black_swan.get('probability', '')}")
            st.markdown(f"**Impact:** {black_swan.get('impact', '')}")
            st.info(f"**How to prepare:** {black_swan.get('preparation', '')}")
            st.caption(f"Source: {black_swan.get('source', '')}")

    # ── Regulatory Intelligence ───────────────────────────────────────────────
    reg_data = ci.get("regulatory_data", {})
    if reg_data:
        st.header("⚖️ Regulatory Intelligence")
        data_freshness = ci.get("data_freshness", {})
        if data_freshness:
            st.caption(
                f"Data source: {data_freshness.get('data_source', '')} | "
                f"Last updated: {data_freshness.get('last_updated', '')} | "
                f"Next update: {data_freshness.get('next_update', '')}"
            )
        reg_risk_level_icons = {"Critical": "🔴", "High": "🟠", "Medium-High": "🟠", "Medium": "🟡", "Low": "🟢"}
        for reg in reg_data.get("active_regulations", []):
            risk_level = reg.get("risk_level", "")
            icon = next((v for k, v in reg_risk_level_icons.items() if k.lower() in risk_level.lower()), "⚪")
            with st.expander(f"{icon} {reg.get('name', '')} — {reg.get('status', '')}"):
                st.markdown(reg.get("summary", ""))
                st.caption(f"Source: {reg.get('source', '')}")
        market_signals = reg_data.get("market_signals", {})
        if market_signals:
            st.subheader("📈 Current Market Signals")
            for signal, value in market_signals.items():
                st.markdown(f"- **{signal.replace('_', ' ').title()}:** {value}")

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

    # ── Sources Used ─────────────────────────────────────────────────────────
    sources_used = ci.get("sources_used", [])
    if sources_used:
        st.header("📚 Sources Used in This Report")
        for src in sources_used:
            st.markdown(f"- {src}")

    st.divider()
    st.caption(
        "Report generated by the **Project Risk Assessment Agent** | "
        "Thesis: *Understanding Risk Awareness and Decision Making in Early-Stage Project Planning* "
        "— Devarshi Kansara, HDBW 2026"
    )
