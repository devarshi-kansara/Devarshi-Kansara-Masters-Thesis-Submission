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
    st.divider()
    if st.button("🔄 Clear Data Cache", help="Force re-fetch of all live internet data on next report generation."):
        try:
            from agent.cache_manager import CacheManager
            removed = CacheManager().clear_old_cache()
            st.success(f"Cache cleared ({removed} stale entries removed). Next report will fetch fresh data.")
        except Exception:
            st.warning("Could not clear cache.")

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

    # ── Fetch live internet data with spinner feedback ────────────────────────
    with st.status("📡 Fetching live data...", expanded=True) as status:
        st.write("📡 Fetching live regulatory data...")
        st.write("📰 Scanning industry news...")
        st.write("💰 Collecting market signals...")
        st.write("📚 Searching academic research...")
        st.write("⚠️ Checking geopolitical alerts...")
        report = agent.generate_report(ctx, fetch_live_data=True)
        status.update(label="✅ Live data fetched!", state="complete", expanded=False)

    live_ok = bool(report.live_data_timestamp)

    st.success("✅ Assessment complete! Scroll down to review your personalised risk report.")
    if live_ok:
        ts = report.live_data_timestamp or ""
        sources = ", ".join(report.data_sources_used) if report.data_sources_used else "None"
        st.info(
            f"🌐 **Live data integrated** · Last updated: {ts} · "
            f"Sources: {sources}"
        )
    else:
        st.warning(
            "⚠️ Some live data unavailable — using cached/local data. "
            "The risk assessment is still complete based on the knowledge base."
        )
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

            # Live-data enrichment
            if risk.recent_news_title:
                news_link = f"[{risk.recent_news_title}]({risk.recent_news_link})" if risk.recent_news_link else risk.recent_news_title
                st.markdown(f"📰 **Recent News:** {news_link} _{risk.recent_news_date}_")
            if risk.regulatory_status:
                st.markdown(f"🏛️ **Regulatory Note:** {risk.regulatory_status}")
            if risk.market_signal:
                st.markdown(f"💰 **Market Signal:** {risk.market_signal}")
            if risk.academic_citation:
                st.markdown(f"📚 **Research:** {risk.academic_citation}")

    # ── Live Data Sections ────────────────────────────────────────────────────

    # 1. Regulatory Updates
    if report.regulatory_updates:
        st.header("🌍 Latest Regulatory Updates")
        for item in report.regulatory_updates:
            title = item.get("title", "")
            url = item.get("url", "")
            date = item.get("date", "")
            if url:
                st.markdown(f"- [{title}]({url}) _{date}_")
            else:
                st.markdown(f"- {title} _{date}_")
    else:
        if live_ok:
            st.header("🌍 Latest Regulatory Updates")
            st.caption("No regulatory updates found for this query.")

    # 2. Industry News
    if report.industry_news:
        st.header("📰 Industry News This Week")
        for item in report.industry_news:
            title = item.get("title", "")
            url = item.get("url", "")
            date = item.get("date", "")
            if url:
                st.markdown(f"- [{title}]({url}) _{date}_")
            else:
                st.markdown(f"- {title} _{date}_")
    else:
        if live_ok:
            st.header("📰 Industry News This Week")
            st.caption("No industry news found for this query.")

    # 3. Market Signals
    if report.market_signals:
        st.header("💰 Market Signals")
        news_signals = report.market_signals.get("news_signals", [])
        macro = report.market_signals.get("macro_indicators", [])
        commodity = report.market_signals.get("commodity_signals", [])
        if commodity:
            st.subheader("Industry Price Indicators")
            cols = st.columns(min(len(commodity), 4))
            for col, ind in zip(cols, commodity):
                label = ind.get("indicator", "")
                value = ind.get("value", "N/A")
                trend = ind.get("trend", "")
                col.metric(label, value, delta=trend if trend else None)
                col.caption(f"Source: {ind.get('source', 'Industry Index')}")
        if macro:
            st.subheader("Macro Indicators")
            cols = st.columns(len(macro))
            for col, ind in zip(cols, macro):
                label = ind.get("indicator", "").replace("_", " ").title()
                value = ind.get("value", "N/A")
                year = ind.get("year", "")
                col.metric(label, f"{value} ({year})", delta=None)
                col.caption(f"Source: {ind.get('source', 'World Bank')}")
        for item in news_signals[:3]:
            title = item.get("title", "")
            url = item.get("url", "")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.markdown(f"- {title}")

    # 4. Academic Research
    if report.academic_research:
        st.header("📚 Recent Research")
        for paper in report.academic_research:
            title = paper.get("title", "")
            authors = paper.get("authors", "")
            pub = paper.get("published", "")[:7]
            url = paper.get("url", "")
            summary = paper.get("summary", "")[:200]
            with st.expander(f"📄 {title}"):
                st.markdown(f"**Authors:** {authors}  |  **Published:** {pub}")
                if summary:
                    st.markdown(f"*{summary}...*")
                if url:
                    st.markdown(f"[View on arXiv]({url})")
                st.caption("Source: arXiv")

    # 5. Geopolitical Alerts
    if report.geopolitical_alerts:
        st.header("⚠️ Geopolitical Alerts")
        for item in report.geopolitical_alerts:
            title = item.get("title", "")
            url = item.get("url", "")
            date = item.get("date", "")
            if url:
                st.warning(f"[{title}]({url}) _{date}_")
            else:
                st.warning(f"{title} _{date}_")

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
