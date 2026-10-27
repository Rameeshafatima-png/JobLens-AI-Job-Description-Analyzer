
import os
import json
import time
import html

import streamlit as st
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# Read Streamlit Cloud secrets before importing the AI workflow.
try:
    for key in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
    ):
        value = st.secrets.get(key)
        if value:
            os.environ[key] = str(value)
except Exception:
    # Local development can continue using the .env file.
    pass

from joblens.workflow import analyze_job_description


# =========================================================
# THEME: VANILLA CREAM / BLUSH PETAL / ROSEWOOD / SAGE LEAF
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --cream: #FFF7E6;
    --blush: #F7C8D3;
    --rose: #B46A72;
    --sage: #A8B58A;
    --mist: #A9B7C6;
    --midnight: #2D3A47;
    --ink: #293640;
    --muted: #68737A;
    --line: #E5DDD2;
    --white: #FFFDF8;
}

.stApp {
    background: var(--cream);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(255,247,230,.96);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--midnight) !important;
    letter-spacing: -.5px;
}

p, label, li {
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: var(--midnight);
    border-right: 1px solid #46525D;
}

[data-testid="stSidebar"] * {
    color: #FFF7E6;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #C8D0D4 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #52606A;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -1.2px;
    color: var(--cream);
    margin-bottom: 2rem;
}

.brand span {
    color: var(--blush);
}

.sidebar-label, .eyebrow {
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: 1.8px;
    color: var(--rose);
    margin-bottom: .6rem;
}

.sidebar-label {
    color: var(--blush);
}

.hero {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 28px rgba(45,58,71,.045);
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(2.1rem, 4vw, 3.3rem);
    line-height: 1.12;
    font-weight: 800;
    letter-spacing: -1.5px;
    color: var(--midnight);
    margin: .4rem 0 .8rem;
}

.hero-title span {
    color: var(--rose);
}

.hero-copy {
    max-width: 740px;
    font-size: .98rem;
    line-height: 1.8;
    color: var(--muted);
}

.tag {
    display: inline-block;
    padding: .38rem .68rem;
    margin: .25rem .3rem .1rem 0;
    background: #FCE5E9;
    border: 1px solid #EBC0C9;
    border-radius: 6px;
    color: #854A54;
    font-size: .76rem;
    font-weight: 600;
}

.panel {
    background: rgba(255,253,248,.9);
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 1.25rem;
    box-shadow: 0 5px 20px rgba(45,58,71,.04);
}

.panel-heading {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.25rem;
    color: var(--midnight);
    margin: .35rem 0;
}

.panel-subtitle {
    font-size: .86rem;
    line-height: 1.7;
    color: var(--muted);
}

div[data-testid="stTextArea"] textarea {
    background: #FFFDF8 !important;
    color: var(--midnight) !important;
    border: 1px solid #DCD3C7 !important;
    border-radius: 9px !important;
    line-height: 1.7 !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--rose) !important;
    box-shadow: 0 0 0 1px var(--rose) !important;
}

div[data-testid="stTextArea"] label {
    color: var(--midnight) !important;
    font-weight: 700 !important;
}

.stButton > button,
.stDownloadButton > button {
    background: var(--rose);
    color: white;
    border: 1px solid var(--rose);
    border-radius: 8px;
    min-height: 2.65rem;
    font-weight: 700;
    transition: all .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #985660;
    border-color: #985660;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(180,106,114,.18);
}

.stButton > button:focus,
.stDownloadButton > button:focus {
    box-shadow: 0 0 0 2px var(--blush) !important;
}

div[data-testid="stMetric"] {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1rem;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted);
}

div[data-testid="stMetricValue"] {
    color: var(--midnight);
    font-size: 1.35rem;
}

.skill-chip {
    display: inline-block;
    padding: .4rem .65rem;
    margin: 0 .35rem .45rem 0;
    border: 1px solid #D6DFC6;
    background: #EDF1E5;
    color: #52613F;
    border-radius: 6px;
    font-size: .82rem;
    font-weight: 600;
}

.skill-chip.priority {
    background: #FCE5E9;
    border-color: #EBC0C9;
    color: #854A54;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    color: var(--midnight);
    font-size: 1rem;
    border-top: 1px solid var(--line);
    padding-top: 1rem;
    margin-top: 1.2rem;
    margin-bottom: .75rem;
}

.summary-box {
    background: linear-gradient(90deg, #FCE5E9, #FFF9F4);
    border-left: 4px solid var(--rose);
    border-radius: 0 9px 9px 0;
    padding: 1rem 1.1rem;
    line-height: 1.8;
    color: #4E5960;
}

.priority-card {
    min-height: 105px;
    padding: .85rem;
    border: 1px solid #EBC0C9;
    background: #FFF3F3;
    border-radius: 9px;
    overflow-wrap: anywhere;
}

.priority-number {
    color: var(--rose);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: .45rem;
}

.empty-state {
    min-height: 330px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
    background: var(--white);
    border: 1px dashed #D7C9BB;
    border-radius: 13px;
}

.empty-icon {
    font-size: 2.6rem;
    color: var(--rose);
    margin-bottom: .7rem;
}

div[data-testid="stAlert"] {
    border-radius: 9px;
}

[data-testid="stProgressBar"] > div > div {
    background: var(--sage);
}

hr {
    border-color: var(--line);
}

footer {
    visibility: hidden;
}

@media (max-width: 800px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero {
        padding: 1.35rem;
    }
    .hero-title {
        font-size: 2.1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SAMPLE JOB DESCRIPTIONS
# =========================================================

SAMPLES = {
    "AI Engineer": """AI Engineer
Company: ABC Technologies
Experience: 2–4 years | Employment: Full-time | Work arrangement: Hybrid

About the role:
We are looking for an AI Engineer to build, deploy, and maintain intelligent applications.

Responsibilities:
- Build AI workflows and integrate language models into backend services.
- Develop APIs using Python and FastAPI.
- Orchestrate multi-step AI tasks using LangGraph.
- Evaluate model outputs and improve reliability.
- Collaborate with cross-functional teams.

Requirements:
- Strong Python programming skills.
- Experience with FastAPI and REST APIs.
- Familiarity with LangGraph, LLM APIs, and prompt engineering.
- Understanding of SQL and data handling.
- Communication, teamwork, and problem-solving skills.
- A computer science degree or equivalent experience is preferred.""",

    "Data Analyst": """Data Analyst
Company: Northstar Insights
Experience: 1–3 years | Employment: Full-time | Work arrangement: Remote

We are seeking a detail-oriented Data Analyst to turn business data into useful insights.

Responsibilities:
- Clean, validate, and analyze datasets.
- Build dashboards and reports for stakeholders.
- Use SQL to query data and Python for analysis.
- Identify trends and explain findings clearly.

Requirements:
- Strong SQL and spreadsheet skills.
- Experience with Python, Pandas, and data visualization.
- Familiarity with Power BI or Tableau.
- Analytical thinking, attention to detail, and communication skills.""",

    "Web Developer": """Frontend Web Developer
Company: PixelCraft Studio
Experience: 1–2 years | Employment: Contract | Work arrangement: On-site

We need a frontend developer to create responsive and accessible web experiences.

Responsibilities:
- Build interfaces using HTML, CSS, and JavaScript.
- Work with designers to implement polished layouts.
- Connect frontend components to REST APIs.
- Test across screen sizes and fix interface issues.

Requirements:
- Practical experience with HTML, CSS, and JavaScript.
- Familiarity with React and Git.
- Understanding of responsive design and accessibility.
- Problem-solving, collaboration, and time-management skills."""
}


# =========================================================
# SESSION STATE
# =========================================================

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

if "report" not in st.session_state:
    st.session_state.report = None


def safe_text(value):
    """Escape generated text before placing it in HTML."""
    return html.escape(str(value if value is not None else ""))


def render_chips(values, priority=False):
    if not values:
        st.caption("Not specified in the job description.")
        return

    css_class = "skill-chip priority" if priority else "skill-chip"
    chips = "".join(
        f'<span class="{css_class}">{safe_text(value)}</span>'
        for value in values
    )
    st.markdown(chips, unsafe_allow_html=True)


def report_to_markdown(report):
    lines = [
        f"# {report.get('job_title') or 'Job Description Analysis'}",
        "",
        f"**Company:** {report.get('company_name') or 'Not specified'}",
        f"**Category:** {report.get('job_category') or 'Not specified'}",
        f"**Experience:** {report.get('required_experience') or 'Not specified'}",
        f"**Employment:** {report.get('employment_type') or 'Not specified'}",
        f"**Work arrangement:** {report.get('work_arrangement') or 'Not specified'}",
        "",
        "## Summary",
        report.get("summary") or "Not available",
        "",
    ]

    for title, key in [
        ("Top Priority Skills", "top_3_skills"),
        ("Technical Skills", "technical_skills"),
        ("Soft Skills", "soft_skills"),
        ("Required Skills", "required_skills"),
        ("Responsibilities", "responsibilities"),
        ("Qualifications", "qualifications"),
    ]:
        lines.extend([f"## {title}", ""])
        values = report.get(key, [])
        if values:
            lines.extend([f"- {item}" for item in values])
        else:
            lines.append("- Not specified")
        lines.append("")

    lines.extend([
        "## Analysis Note",
        report.get("analysis_note") or "Verify the findings against the original job post.",
    ])
    return "\n".join(lines)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand">JobLens <span>AI</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown("### Job description analyzer")
    st.caption("AI-powered job intelligence")
    st.divider()

    st.markdown("**ANALYSIS WORKFLOW**")
    workflow_steps = [
        ("01", "Information extraction", "Role, company and experience"),
        ("02", "Job classification", "Category and work setup"),
        ("03", "Skill analysis", "Technical and soft skills"),
        ("04", "Hiring report", "Summary and requirements"),
    ]

    for number, title, description in workflow_steps:
        st.markdown(f"**{number} · {title}**")
        st.caption(description)

    st.divider()
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    st.markdown("**AI PROVIDER**")
    st.caption(
        "Groq API" if provider == "groq"
        else "Google Gemini" if provider == "gemini"
        else provider.upper()
    )
    st.caption("API credentials are read from your local .env file.")
    st.caption("Keep your API key private and out of GitHub.")


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">JOB INTELLIGENCE WORKSPACE</div>
    <div class="hero-title">
        Understand the role.<br>
        <span>Own the opportunity.</span>
    </div>
    <div class="hero-copy">
        Turn a job description into a structured hiring brief.
        Identify essential skills, experience requirements,
        responsibilities and the signals that matter most.
    </div>
    <br>
    <span class="tag">LangGraph workflow</span>
    <span class="tag">AI-powered analysis</span>
    <span class="tag">Downloadable reports</span>
</div>
""", unsafe_allow_html=True)


# =========================================================
# MAIN WORKSPACE
# =========================================================

left, right = st.columns([0.92, 1.08], gap="large")

with left:
    st.markdown('<div class="eyebrow">01 / INPUT</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-heading">Job description</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-subtitle">Paste the job post or load a sample to begin.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    sample_cols = st.columns(3)
    for column, sample_name in zip(sample_cols, SAMPLES):
        if column.button(sample_name, use_container_width=True, key=f"sample_{sample_name}"):
            st.session_state.job_text = SAMPLES[sample_name]
            st.rerun()

    job_text = st.text_area(
        "JOB POSTING",
        key="job_text",
        height=315,
        max_chars=15000,
        placeholder=(
            "Paste the full job description here...\n\n"
            "Include responsibilities, qualifications, experience, "
            "technical skills and employment details."
        ),
    )

    st.caption(f"{len(job_text):,} / 15,000 characters · Minimum 40 characters")

    st.markdown(
        '<div class="panel-subtitle">Your description is sent to your configured AI provider only when you analyze it.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    analyze = st.button(
        "✦  Analyze job description",
        use_container_width=True,
        type="primary",
    )

    if analyze:
        if len(job_text.strip()) < 40:
            st.error("Please enter a job description with at least 40 characters.")
        else:
            provider = os.getenv("LLM_PROVIDER", "groq").lower()

            if provider == "groq" and not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY is missing from .env. Add it and restart the app.")
            elif provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
                st.error("GEMINI_API_KEY is missing from .env. Add it and restart the app.")
            else:
                progress = st.progress(0, text="Preparing analysis...")
                status = st.empty()

                try:
                    stages = [
                        "Step 1/4 · Extracting job information",
                        "Step 2/4 · Classifying the position",
                        "Step 3/4 · Analyzing skills",
                        "Step 4/4 · Preparing the report",
                    ]

                    for index, stage in enumerate(stages):
                        status.caption(stage)
                        progress.progress((index + 1) * 15, text=stage)
                        time.sleep(0.12)

                    with st.spinner("Running the AI workflow..."):
                        report = analyze_job_description(job_text.strip())

                    if not isinstance(report, dict):
                        raise ValueError(
                            "The workflow returned an unexpected result. "
                            "Check joblens/workflow.py."
                        )

                    progress.progress(100, text="Analysis complete")
                    status.empty()
                    st.session_state.report = report
                    st.success("Your hiring report is ready.")

                except Exception as exc:
                    progress.empty()
                    status.empty()

                    message = str(exc).lower()

                    if any(word in message for word in ["rate limit", "quota", "429"]):
                        st.error("The AI provider rate limit or quota was reached. Wait and try again.")
                    elif any(word in message for word in ["api key", "authentication", "unauthorized", "401", "403"]):
                        st.error("The AI provider rejected the API key. Check your .env settings.")
                    elif any(word in message for word in ["model", "not found", "404"]):
                        st.error("The selected AI model is unavailable. Check LLM_MODEL in .env.")
                    else:
                        st.error("Analysis failed. Check the error details below and your terminal logs.")

                    with st.expander("Technical error details"):
                        st.code(str(exc))


# =========================================================
# REPORT PANEL
# =========================================================

with right:
    st.markdown('<div class="eyebrow">02 / RESULTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-heading">Hiring intelligence report</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-subtitle">A structured overview of the role and its requirements.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    report = st.session_state.report

    if not report:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">✦</div>
            <h3>Your report starts here</h3>
            <div class="panel-subtitle" style="max-width:350px">
                Add a job description and run the analysis to reveal the role,
                essential skills and hiring priorities.
            </div>
            <br>
            <div style="color:#68737A;line-height:2">
                ✓ Role and experience<br>
                ✓ Technical and soft skills<br>
                ✓ Responsibilities and qualifications<br>
                ✓ Exportable analysis report
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        title = safe_text(report.get("job_title") or "Job title not specified")
        company = safe_text(report.get("company_name") or "Company not specified")
        category = safe_text(report.get("job_category") or "Other")
        summary = safe_text(report.get("summary") or "Summary not available.")

        st.markdown(f"## {title}")
        st.caption(company)
        st.markdown(f'<span class="tag">{category}</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="summary-box">{summary}</div>',
            unsafe_allow_html=True,
        )

        st.write("")
        metric1, metric2 = st.columns(2)
        metric1.metric("Experience", report.get("required_experience") or "Not specified")
        metric2.metric("Employment", report.get("employment_type") or "Not specified")

        metric3, metric4 = st.columns(2)
        metric3.metric("Work setup", report.get("work_arrangement") or "Not specified")
        metric4.metric("Required skills", len(report.get("required_skills", [])))

        st.markdown('<div class="section-title">✦ Top priority skills</div>', unsafe_allow_html=True)
        top_skills = report.get("top_3_skills", [])

        if top_skills:
            priority_cols = st.columns(min(3, len(top_skills)))
            for index, skill in enumerate(top_skills[:3]):
                priority_cols[index].markdown(
                    f"""
                    <div class="priority-card">
                        <div class="priority-number">PRIORITY 0{index + 1}</div>
                        <strong>{safe_text(skill)}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No priority skills were returned.")

        for heading, key in [
            ("Technical skills", "technical_skills"),
            ("Soft skills", "soft_skills"),
            ("All required skills", "required_skills"),
        ]:
            st.markdown(
                f'<div class="section-title">{heading}</div>',
                unsafe_allow_html=True,
            )
            render_chips(report.get(key, []), priority=(key == "required_skills"))

        for heading, key in [
            ("Key responsibilities", "responsibilities"),
            ("Qualifications", "qualifications"),
        ]:
            st.markdown(
                f'<div class="section-title">{heading}</div>',
                unsafe_allow_html=True,
            )
            values = report.get(key, [])

            if values:
                for value in values:
                    st.markdown(f"- {value}")
            else:
                st.caption("Not specified in the job description.")

        st.caption(
            report.get(
                "analysis_note",
                "AI-generated analysis. Verify findings against the original job post."
            )
        )

        st.divider()

        json_report = json.dumps(report, indent=2, ensure_ascii=False)
        markdown_report = report_to_markdown(report)

        download_json, download_md = st.columns(2)

        with download_json:
            st.download_button(
                "Download JSON",
                data=json_report,
                file_name="joblens-hiring-report.json",
                mime="application/json",
                use_container_width=True,
            )

        with download_md:
            st.download_button(
                "Download Markdown",
                data=markdown_report,
                file_name="joblens-hiring-report.md",
                mime="text/markdown",
                use_container_width=True,
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()
footer_left, footer_right = st.columns([1, 1])

with footer_left:
    st.caption("JOBLENS AI  /  JOB DESCRIPTION INTELLIGENCE")

with footer_right:
    st.caption("AI-generated insights should be verified against the original job posting.")
