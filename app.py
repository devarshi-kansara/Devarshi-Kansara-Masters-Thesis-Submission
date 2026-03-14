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
    page_title="Risk Assessment Agent — Devarshi Kansara",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: #F1F5F9; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0F172A !important;
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    section[data-testid="stSidebar"] .stMarkdown a { color: #60A5FA !important; }
    section[data-testid="stSidebar"] hr { border-color: #334155 !important; }
    section[data-testid="stSidebar"] .stInfo {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* ── Hero header ── */
    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border-radius: 16px;
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3B82F6, #06B6D4, #8B5CF6);
    }
    .hero h1 {
        color: #F8FAFC !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.4rem 0 !important;
        line-height: 1.2 !important;
    }
    .hero p {
        color: #94A3B8 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        max-width: 680px;
        line-height: 1.6;
    }
    .hero .pill {
        display: inline-block;
        background: rgba(59,130,246,0.2);
        border: 1px solid rgba(59,130,246,0.4);
        color: #93C5FD !important;
        border-radius: 999px;
        padding: 0.2rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    /* ── Section card ── */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 4px rgba(15,23,42,0.06);
    }
    .section-card h2, .section-card h3 {
        color: #0F172A !important;
        margin-top: 0 !important;
    }

    /* ── Section heading with accent bar ── */
    .section-heading {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 2rem 0 1rem 0;
    }
    .section-heading .bar {
        width: 4px;
        height: 1.5rem;
        border-radius: 2px;
        background: linear-gradient(180deg, #3B82F6, #06B6D4);
        flex-shrink: 0;
    }
    .section-heading .text {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    /* ── Metric card ── */
    .metric-row { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
    .metric-card {
        flex: 1;
        min-width: 120px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(15,23,42,0.05);
    }
    .metric-card .m-value {
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    .metric-card .m-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
    }
    .mc-critical { border-top: 3px solid #DC2626; }
    .mc-critical .m-value { color: #DC2626; }
    .mc-high { border-top: 3px solid #EA580C; }
    .mc-high .m-value { color: #EA580C; }
    .mc-medium { border-top: 3px solid #CA8A04; }
    .mc-medium .m-value { color: #CA8A04; }
    .mc-low { border-top: 3px solid #16A34A; }
    .mc-low .m-value { color: #16A34A; }

    /* ── Risk badge ── */
    .badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        vertical-align: middle;
        margin-right: 0.4rem;
    }
    .badge-Critical { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    .badge-High     { background: #FFF7ED; color: #9A3412; border: 1px solid #FED7AA; }
    .badge-Medium   { background: #FEFCE8; color: #854D0E; border: 1px solid #FEF08A; }
    .badge-Low      { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }

    /* ── Risk register row ── */
    .risk-row {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #94A3B8;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }
    .risk-row-Critical { border-left-color: #DC2626; background: #FFFAFA; }
    .risk-row-High     { border-left-color: #EA580C; background: #FFFDF9; }
    .risk-row-Medium   { border-left-color: #CA8A04; background: #FFFEF0; }
    .risk-row-Low      { border-left-color: #16A34A; background: #F7FFF9; }
    .risk-row .risk-desc {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 0.35rem;
    }
    .risk-row .risk-meta {
        font-size: 0.8rem;
        color: #64748B;
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .risk-row .risk-action {
        font-size: 0.82rem;
        color: #1E40AF;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    /* ── Info block (replaces st.info/warning) ── */
    .info-block {
        background: #EFF6FF;
        border-left: 3px solid #3B82F6;
        border-radius: 0 6px 6px 0;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #1E3A5F;
        line-height: 1.55;
    }
    .warn-block {
        background: #FFFBEB;
        border-left: 3px solid #F59E0B;
        border-radius: 0 6px 6px 0;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #78350F;
        line-height: 1.55;
    }
    .danger-block {
        background: #FEF2F2;
        border-left: 3px solid #DC2626;
        border-radius: 0 6px 6px 0;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #7F1D1D;
        line-height: 1.55;
    }
    .success-block {
        background: #F0FDF4;
        border-left: 3px solid #16A34A;
        border-radius: 0 6px 6px 0;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #14532D;
        line-height: 1.55;
    }

    /* ── Tag chip ── */
    .tag {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        border-radius: 4px;
        padding: 0.15rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem 0.2rem 0.15rem 0;
    }
    .tag-purple { background: #F5F3FF; color: #6D28D9; }
    .tag-green  { background: #F0FDF4; color: #15803D; }
    .tag-orange { background: #FFF7ED; color: #C2410C; }

    /* ── Framework card ── */
    .fw-card {
        background: #FAFBFF;
        border: 1px solid #DBEAFE;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.85rem;
    }
    .fw-card h4 {
        font-size: 0.97rem;
        font-weight: 700;
        color: #1E40AF;
        margin: 0 0 0.4rem 0;
    }
    .fw-card p { font-size: 0.86rem; color: #334155; margin: 0.3rem 0; line-height: 1.55; }
    .fw-card .fw-why {
        background: #EFF6FF;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.83rem;
        color: #1E3A5F;
        margin-top: 0.5rem;
    }
    .fw-card .fw-blind {
        font-size: 0.8rem;
        color: #7C3AED;
        font-style: italic;
        margin-top: 0.3rem;
    }

    /* ── Benchmark card ── */
    .bench-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.7rem;
    }
    .bench-card h4 { font-size: 0.92rem; font-weight: 700; color: #0F172A; margin: 0 0 0.6rem 0; }
    .bench-stat { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.35rem; }
    .bench-stat .bs-icon { font-size: 1rem; flex-shrink: 0; }
    .bench-stat .bs-text { font-size: 0.83rem; color: #334155; line-height: 1.4; }
    .bench-stat .bs-label { font-weight: 600; color: #0F172A; }

    /* ── Form section header ── */
    .form-section-hdr {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 0.4rem;
        margin: 1.2rem 0 0.8rem 0;
    }

    /* ── Submit button override ── */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #1D4ED8, #0EA5E9) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        transition: opacity 0.2s !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover { opacity: 0.9 !important; }

    /* ── Expander polish ── */
    details { border: 1px solid #E2E8F0 !important; border-radius: 10px !important; margin-bottom: 0.5rem !important; }
    summary { font-weight: 600 !important; font-size: 0.93rem !important; color: #0F172A !important; }

    /* ── Footer ── */
    .app-footer {
        background: #0F172A;
        border-radius: 10px;
        padding: 1.25rem 1.75rem;
        margin-top: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .app-footer .ft-left { font-size: 0.82rem; color: #94A3B8; }
    .app-footer .ft-left strong { color: #E2E8F0; }
    .app-footer .ft-right { font-size: 0.78rem; color: #64748B; }

    /* ── Citation block ── */
    .cite-block {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.55rem 0.85rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        color: #475569;
        line-height: 1.6;
        font-style: italic;
    }

    /* ── List item row ── */
    .list-row {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.45rem 0;
        border-bottom: 1px solid #F1F5F9;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
    }
    .list-row:last-child { border-bottom: none; }
    .list-row .lr-icon { flex-shrink: 0; width: 1.4rem; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helper functions ──────────────────────────────────────────────────────────

def _section_heading(icon: str, title: str) -> None:
    st.markdown(
        f"""<div class="section-heading">
            <div class="bar"></div>
            <p class="text">{icon}&nbsp; {title}</p>
        </div>""",
        unsafe_allow_html=True,
    )


def _badge(level: str) -> str:
    return f'<span class="badge badge-{level}">{level}</span>'


def _info(text: str) -> None:
    st.markdown(f'<div class="info-block">{text}</div>', unsafe_allow_html=True)


def _warn(text: str) -> None:
    st.markdown(f'<div class="warn-block">{text}</div>', unsafe_allow_html=True)


def _danger(text: str) -> None:
    st.markdown(f'<div class="danger-block">{text}</div>', unsafe_allow_html=True)


def _success(text: str) -> None:
    st.markdown(f'<div class="success-block">{text}</div>', unsafe_allow_html=True)


def _list_row(icon: str, text: str) -> None:
    st.markdown(
        f'<div class="list-row"><span class="lr-icon">{icon}</span><span>{text}</span></div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size:1.35rem; font-weight:700; color:#F8FAFC; letter-spacing:-0.02em;">
                🔷 Risk Assessment Agent
            </div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:0.2rem; text-transform:uppercase;
                        letter-spacing:0.07em;">
                Project Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        """
        <div style="font-size:0.82rem; color:#94A3B8; line-height:1.65;">
            Based on the doctoral thesis<br>
            <span style="color:#E2E8F0; font-style:italic;">
            "Understanding Risk Awareness and Decision Making in Early-Stage Project Planning"
            </span><br><br>
            <span style="color:#64748B;">Devarshi Kansara — HDBW Munich, 2026</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        """
        <div style="font-size:0.8rem; color:#94A3B8; line-height:1.7;">
            <div style="color:#60A5FA; font-weight:600; margin-bottom:0.4rem;">How it works</div>
            <div>1️⃣ &nbsp;Complete the assessment form</div>
            <div>2️⃣ &nbsp;Receive your personalised risk profile</div>
            <div>3️⃣ &nbsp;Review consultant insights &amp; frameworks</div>
            <div>4️⃣ &nbsp;Plan your 20% Reality Check</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#475569; line-height:1.55; background:#1E293B;
                    border-radius:8px; padding:0.75rem 0.85rem; border:1px solid #334155;">
            ⚡ <strong style="color:#E2E8F0;">Research finding:</strong>
            ~70% of project failures originate from decisions made in the
            <strong style="color:#60A5FA;">first 20%</strong> of the project lifecycle.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <div class="pill">Early-Stage Project Intelligence</div>
        <h1>Risk Assessment Agent</h1>
        <p>
            A thesis-derived decision-support system that identifies, prioritises, and mitigates
            the risks that determine project success in the critical first 20% of the lifecycle.
            Personalised to your industry, experience level, and cultural archetype.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("risk_form"):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-hdr">Section 1 — Your Background</div>', unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-hdr">Section 2 — Early Risk Focus</div>', unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-hdr">Section 3 — Decision Style</div>', unsafe_allow_html=True)
    decision_style = st.radio(
        "When deciding which risks to take seriously, you rely on:",
        ["Mostly experience and intuition", "A balance of intuition and tools", "Mostly formal tools and methods"],
        horizontal=True,
        index=1,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-hdr">Section 4 — Time Pressure</div>', unsafe_allow_html=True)
    time_pressure = st.select_slider(
        "Time pressure at project start",
        options=["Low", "Medium", "High"],
        value="Medium",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("🔍 Generate Risk Assessment", use_container_width=True)

# ── Process & display report ──────────────────────────────────────────────────
if submitted:
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

    _success("✅ &nbsp;<strong>Assessment complete.</strong> &nbsp;Scroll down to review your personalised risk report.")

    # ── Risk Metrics ──────────────────────────────────────────────────────────
    _section_heading("📊", "Risk Summary")
    critical_count = sum(1 for r in report.risk_register if r.level == "Critical")
    high_count     = sum(1 for r in report.risk_register if r.level == "High")
    medium_count   = sum(1 for r in report.risk_register if r.level == "Medium")
    low_count      = sum(1 for r in report.risk_register if r.level == "Low")

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card mc-critical">
                <div class="m-value">{critical_count}</div>
                <div class="m-label">Critical</div>
            </div>
            <div class="metric-card mc-high">
                <div class="m-value">{high_count}</div>
                <div class="m-label">High</div>
            </div>
            <div class="metric-card mc-medium">
                <div class="m-value">{medium_count}</div>
                <div class="m-label">Medium</div>
            </div>
            <div class="metric-card mc-low">
                <div class="m-value">{low_count}</div>
                <div class="m-label">Low</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if critical_count > 0:
        _danger(
            f"⛔ &nbsp;<strong>STOP-AND-FIX:</strong> &nbsp;You have {critical_count} Critical risk(s). "
            "Do not proceed until these are resolved or formally accepted by your sponsor."
        )

    # ── Consultant Insights ───────────────────────────────────────────────────
    _section_heading("🧠", "Consultant Insights")
    st.markdown(
        '<p style="font-size:0.88rem;color:#64748B;margin:-0.4rem 0 1rem 0;">'
        "Industry-specific analysis personalised to your profile, experience level, and cultural archetype."
        "</p>",
        unsafe_allow_html=True,
    )

    # Persona analysis
    persona = consultant_insights["persona_analysis"]
    with st.expander("👤 Your Persona Profile & Blind Spots", expanded=True):
        st.markdown(
            f'<div style="display:inline-block;background:#EFF6FF;border:1px solid #BFDBFE;'
            f'border-radius:6px;padding:0.3rem 0.85rem;font-size:0.9rem;font-weight:700;'
            f'color:#1D4ED8;margin-bottom:0.8rem;">'
            f'{persona.get("archetype", "")}</div>',
            unsafe_allow_html=True,
        )
        col_s, col_b = st.columns(2)
        with col_s:
            st.markdown("**Strengths**")
            for s in persona.get("strengths", []):
                _list_row("✅", s)
        with col_b:
            st.markdown("**Blind Spots**")
            for bs in persona.get("blind_spots", []):
                _list_row("⚠️", bs)
        st.markdown(
            f'<div style="margin-top:0.8rem;display:flex;gap:1.5rem;flex-wrap:wrap;">'
            f'<div><span style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.06em;color:#64748B;">Decision Pattern</span>'
            f'<div style="font-size:0.88rem;color:#0F172A;margin-top:0.15rem;">'
            f'{persona.get("decision_pattern", "")}</div></div>'
            f'<div><span style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.06em;color:#64748B;">Risk Tolerance</span>'
            f'<div style="font-size:0.88rem;color:#0F172A;margin-top:0.15rem;">'
            f'{persona.get("risk_tolerance", "")}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if persona.get("time_pressure_note"):
            _danger(persona["time_pressure_note"])

    # Industry benchmarks
    benchmarks = consultant_insights["industry_benchmarks"]
    if benchmarks:
        with st.expander("📊 Industry Benchmarks — How You Compare"):
            for key, data in benchmarks.items():
                st.markdown(
                    f'<div class="bench-card">'
                    f'<h4>{data.get("label", key)}</h4>'
                    f'<div class="bench-stat"><span class="bs-icon">📌</span>'
                    f'<span class="bs-text"><span class="bs-label">Frequency: </span>'
                    f'{data.get("frequency", "")}</span></div>'
                    f'<div class="bench-stat"><span class="bs-icon">✅</span>'
                    f'<span class="bs-text"><span class="bs-label">Success rate: </span>'
                    f'{data.get("success_rate", "")}</span></div>'
                    f'<div class="bench-stat"><span class="bs-icon">💰</span>'
                    f'<span class="bs-text"><span class="bs-label">Mitigation cost: </span>'
                    f'{data.get("typical_mitigation_cost", "")}</span></div>'
                    f'<div class="bench-stat"><span class="bs-icon">🔥</span>'
                    f'<span class="bs-text"><span class="bs-label">Failure cost: </span>'
                    f'{data.get("typical_failure_cost", "")}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Blind spots
    all_blind_spots = consultant_insights["blind_spots"]
    if all_blind_spots:
        with st.expander("⚡ Blind Spots — Profile & Industry Specific"):
            for bs in all_blind_spots:
                _warn(bs)

    # Recommended frameworks
    rec_frameworks = consultant_insights["recommended_frameworks"]
    if rec_frameworks:
        with st.expander("🧰 Recommended Frameworks — Personalised Rationale"):
            for fw in rec_frameworks:
                st.markdown(
                    f'<div class="fw-card">'
                    f'<h4>▸ {fw["name"]}</h4>'
                    f'<p>{fw.get("description", "")}</p>'
                    f'<div class="fw-why">💡 <strong>Why this matters for you:</strong> '
                    f'{fw.get("rationale", "")}</div>'
                    f'<p class="fw-blind">🎯 Blind spot addressed: {fw.get("blind_spot_addressed", "")}</p>'
                    f'<p><strong>When:</strong> {fw.get("when_to_apply", "")}</p>'
                    f'<p><em>Example: {fw.get("example", "")}</em></p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Black swan warnings
    black_swans = consultant_insights["black_swan_warnings"]
    if black_swans:
        with st.expander("🦢 Black Swan Warnings — Low-Probability, High-Impact"):
            for warning in black_swans:
                _danger(warning)

    # Regulatory intelligence
    reg_intel = consultant_insights["regulatory_intelligence"]
    if reg_intel:
        with st.expander("⚖️ Regulatory Intelligence"):
            for item in reg_intel:
                _info(item)

    # Market signals
    market_signals = consultant_insights["market_signals"]
    if market_signals:
        with st.expander("📈 Market Signals"):
            for signal in market_signals:
                _list_row("📌", signal)

    # Cross-industry insights
    cross_insights = consultant_insights["cross_industry_insights"]
    if cross_insights:
        with st.expander("🔀 Cross-Industry Insights"):
            for insight in cross_insights:
                _list_row("🔗", insight)

    # Research citations
    citations = consultant_insights["research_citations"]
    if citations:
        with st.expander("📚 Research Citations (APA Format)"):
            for cite in citations:
                st.markdown(f'<div class="cite-block">{cite}</div>', unsafe_allow_html=True)

    # ── Risk Register ─────────────────────────────────────────────────────────
    _section_heading("📋", "Risk Register")
    st.markdown(
        '<p style="font-size:0.88rem;color:#64748B;margin:-0.4rem 0 1rem 0;">'
        "Sorted by severity score (highest first). Expand any item for full details."
        "</p>",
        unsafe_allow_html=True,
    )
    level_colors = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
    for i, risk in enumerate(report.risk_register, 1):
        icon = level_colors.get(risk.level, "⚪")
        with st.expander(f"{icon} #{i} — {risk.description}"):
            st.markdown(
                f'<div class="risk-row risk-row-{risk.level}">'
                f'<div class="risk-desc">{_badge(risk.level)} {risk.description}</div>'
                f'<div class="risk-meta">'
                f'<span><strong>Category:</strong> {risk.category}</span>'
                f'<span><strong>Probability:</strong> {risk.probability}</span>'
                f'<span><strong>Impact:</strong> {risk.impact}</span>'
                f'<span><strong>Detectability:</strong> {risk.detectability}</span>'
                f'<span><strong>Score:</strong> {risk.score}</span>'
                f'</div>'
                f'<div class="risk-action">→ {risk.action}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Industry Context ──────────────────────────────────────────────────────
    _section_heading("🏗", f"Industry Context — {industry}")
    ind_data = report.industry_risks
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**External Risks**")
        for r in ind_data.get("primary_external", []):
            _list_row("🌐", r)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Internal Risks**")
        for r in ind_data.get("primary_internal", []):
            _list_row("⚙️", r)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("**⚡ Blind Spots for Outsiders**")
    for r in ind_data.get("blind_spots_for_outsiders", []):
        _warn(r)

    # ── Experience-Level Guidance ─────────────────────────────────────────────
    exp = report.experience_guidance
    _section_heading("👤", f"Guidance — {ctx.experience_level.title()} Project Managers")
    col_s, col_d = st.columns(2)
    with col_s:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Strengths ✅**")
        for s in exp.get("strengths", []):
            _list_row("✅", s)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Development Areas 📌**")
        for d in exp.get("development_areas", []):
            _list_row("📌", d)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("**Recommended Actions for the First 20%**")
    for a in exp.get("recommended_actions", []):
        _info(f"→ {a}")

    # ── Decision Frameworks ───────────────────────────────────────────────────
    _section_heading("🧰", "Decision Frameworks")
    for fw in report.framework_recommendations:
        with st.expander(f"▸ {fw['name']}"):
            st.markdown(
                f'<div class="fw-card">'
                f'<h4>{fw["name"]}</h4>'
                f'<p>{fw["description"]}</p>'
                f'<p><strong>When to apply:</strong> {fw["when_to_apply"]}</p>'
                f'<p><em>Example: {fw["example"]}</em></p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 20% Reality Check ────────────────────────────────────────────────────
    _section_heading("📅", "20% Reality Check Milestone")
    rc = report.reality_check_plan
    _info(rc["description"])
    st.markdown("**Workshop Agenda**")
    for item in rc.get("agenda_items", []):
        st.checkbox(item, key=item)
    _success(f"<strong>Expected output:</strong> {rc.get('output', '')}")

    # ── First 20% Action Checklist ────────────────────────────────────────────
    _section_heading("🚀", f"First 20% Action Checklist — {industry}")
    for action in ind_data.get("first_20_percent_actions", []):
        st.checkbox(action, key=action)

    # ── Cultural Archetype ────────────────────────────────────────────────────
    arch = CULTURAL_ARCHETYPES.get(ctx.cultural_region)
    if arch:
        _section_heading("🌍", f"Cultural Archetype — {ctx.cultural_region.replace('_', ' ').title()}")
        col_char, col_dev = st.columns(2)
        with col_char:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Key Characteristics**")
            for c in arch.get("characteristics", []):
                _list_row("•", c)
            st.markdown("**Blind Spots**")
            for bs in arch.get("blind_spots", []):
                _warn(bs)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_dev:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Development Recommendation**")
            _info(arch.get("recommended_development", ""))
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="app-footer">
            <div class="ft-left">
                Generated by <strong>Risk Assessment Agent</strong> &nbsp;·&nbsp;
                Thesis: <em>Understanding Risk Awareness and Decision Making in
                Early-Stage Project Planning</em>
            </div>
            <div class="ft-right">Devarshi Kansara &nbsp;·&nbsp; HDBW Munich &nbsp;·&nbsp; 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
