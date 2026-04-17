import os
from dataclasses import asdict
from datetime import date
from html import escape

import streamlit as st
from dotenv import load_dotenv

from student_ecosystem.domain.admissions import admit_probability_score, admit_probability_tips
from student_ecosystem.domain.career import recommend_programs
from student_ecosystem.domain.copy import STAGES
from student_ecosystem.domain.finance import (
    emi,
    eligible_loan_amount_estimate,
    repayment_scenarios,
    total_cost_of_study,
)
from student_ecosystem.domain.timeline import build_timeline
from student_ecosystem.domain.universities import load_universities
from student_ecosystem.llm.chat import MentorCopilot


def _set_page() -> None:
    st.set_page_config(
        page_title="FutureMintAI",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def _inject_theme() -> None:
    st.markdown(
        """
<style>
:root {
  --fm-bg: #FAFAFA;
  --fm-bg-soft: #F8FAFC;
  --fm-card: rgba(255, 255, 255, 0.9);
  --fm-card-strong: #FFFFFF;
  --fm-border: rgba(229, 231, 235, 1);
  --fm-divider: #F1F5F9;
  --fm-ink: #111827;
  --fm-ink-soft: #6B7280;
  --fm-ink-muted: #9CA3AF;
  --fm-primary: #2563EB;
  --fm-primary-2: #1D4ED8;
  --fm-success: #16A34A;
  --fm-success-2: #22C55E;
  --fm-accent: #D97706;
  --fm-danger: #DC2626;
  --fm-shadow: 0 10px 30px rgba(17, 24, 39, 0.05);
}

.stApp {
  color: var(--fm-ink);
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
  background: linear-gradient(180deg, #ffffff 0%, var(--fm-bg) 100%);
}

[data-testid="stHeader"] {
  background: rgba(250, 250, 250, 0.9);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
  border-right: 1px solid var(--fm-border);
}

[data-testid="stSidebar"] * {
  color: var(--fm-ink) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: var(--fm-ink-soft) !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
  background: #ffffff !important;
  color: var(--fm-ink) !important;
  border: 1px solid var(--fm-border) !important;
  border-radius: 12px !important;
}

.block-container {
  padding-top: 1.6rem;
  padding-bottom: 2rem;
}

.fm-kicker {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.74rem;
  font-weight: 800;
  color: var(--fm-primary);
  margin-bottom: 0.55rem;
}

.fm-hero {
  position: relative;
  overflow: hidden;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 1.6rem 1.6rem 1.4rem 1.6rem;
  border: 1px solid var(--fm-border);
  box-shadow: var(--fm-shadow);
  color: var(--fm-ink);
  margin-bottom: 1rem;
}

.fm-hero::after {
  content: "";
  position: absolute;
  inset: auto 0 0 auto;
  width: 120px;
  height: 120px;
  border-radius: 18px 0 20px 0;
  background: rgba(37, 99, 235, 0.05);
}

.fm-hero h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.1rem);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.fm-hero p {
  margin: 0.8rem 0 0 0;
  max-width: 760px;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--fm-ink-soft);
}

.fm-pill-row {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.fm-pill {
  background: #EFF6FF;
  border: 1px solid #DBEAFE;
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--fm-primary);
}

.fm-panel {
  background: var(--fm-card);
  border: 1px solid var(--fm-border);
  border-radius: 16px;
  padding: 1.15rem 1.15rem 1rem 1.15rem;
  box-shadow: var(--fm-shadow);
  margin-bottom: 1rem;
}

.fm-panel h3,
.fm-panel h4 {
  margin: 0;
  color: var(--fm-ink);
}

.fm-panel p {
  margin: 0.45rem 0 0 0;
  color: var(--fm-ink-soft);
  line-height: 1.55;
}

.fm-section-label {
  display: inline-block;
  margin-bottom: 0.5rem;
  color: var(--fm-primary);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.fm-mini-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.fm-metric-card {
  background: var(--fm-card-strong);
  border: 1px solid var(--fm-border);
  border-radius: 12px;
  padding: 1rem;
  min-height: 120px;
}

.fm-metric-card .label {
  color: var(--fm-ink-soft);
  font-size: 0.86rem;
  font-weight: 700;
}

.fm-metric-card .value {
  margin-top: 0.35rem;
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--fm-ink);
}

.fm-metric-card .meta {
  margin-top: 0.5rem;
  color: var(--fm-ink-soft);
  font-size: 0.9rem;
  line-height: 1.45;
}

.fm-story-card {
  background: #FFFFFF;
  border: 1px solid var(--fm-border);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: 0 8px 24px rgba(17, 24, 39, 0.04);
  margin-bottom: 0.9rem;
}

.fm-story-card .eyebrow {
  color: var(--fm-accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.fm-story-card .headline {
  margin-top: 0.35rem;
  font-size: 1.12rem;
  font-weight: 800;
  color: var(--fm-ink);
}

.fm-story-card .body {
  margin-top: 0.45rem;
  color: var(--fm-ink-soft);
  line-height: 1.55;
}

.fm-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.75rem;
}

.fm-tag {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.35rem 0.55rem;
  border-radius: 999px;
  background: #EFF6FF;
  color: var(--fm-primary);
}

.fm-score-card {
  background: #FFFFFF;
}

.fm-list {
  margin: 0.75rem 0 0 0;
  padding-left: 1.1rem;
  color: var(--fm-ink-soft);
}

.fm-list li {
  margin: 0.35rem 0;
}

div[data-testid="stMetric"] {
  background: #FFFFFF;
  border: 1px solid var(--fm-border);
  border-radius: 12px;
  padding: 0.6rem 0.7rem;
}

div[data-testid="stMetricLabel"] {
  color: var(--fm-ink-soft);
  font-weight: 700;
}

button[kind="primary"],
.stButton > button {
  border: 1px solid var(--fm-border) !important;
  color: var(--fm-ink) !important;
  font-weight: 800 !important;
  background: #FFFFFF !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.45rem;
  margin-bottom: 0.6rem;
}

.stTabs [data-baseweb="tab"] {
  background: #FFFFFF;
  border: 1px solid var(--fm-border);
  border-radius: 999px;
  color: var(--fm-ink-soft);
  font-weight: 700;
  padding: 0.45rem 1rem;
}

.stTabs [aria-selected="true"] {
  background: var(--fm-primary) !important;
  color: #FFFFFF !important;
  border: 1px solid var(--fm-primary) !important;
}

.stProgress > div > div > div > div {
  background: var(--fm-primary);
}

div[data-testid="stExpander"] {
  border: 1px solid var(--fm-border);
  border-radius: 12px;
  background: #FFFFFF;
}

.stAlert {
  border-radius: 12px !important;
  border: 1px solid var(--fm-border) !important;
  background: #FFFFFF !important;
}

[data-testid="stNotificationContentInfo"] {
  border-left-color: var(--fm-accent) !important;
}

[data-testid="stNotificationContentSuccess"] {
  border-left-color: var(--fm-success) !important;
}

[data-testid="stChatMessage"] {
  background: #FFFFFF;
  border: 1px solid var(--fm-border);
  border-radius: 12px;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-baseweb="select"] > div {
  background: #FFFFFF !important;
  color: var(--fm-ink) !important;
  border: 1px solid var(--fm-border) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
  color: var(--fm-ink-muted) !important;
}

.stMultiSelect [data-baseweb="tag"] {
  background: #EFF6FF !important;
  border: 1px solid #BFDBFE !important;
}

.stMultiSelect [data-baseweb="tag"] span,
.stMultiSelect [data-baseweb="tag"] svg {
  color: var(--fm-primary) !important;
  fill: var(--fm-primary) !important;
}

.stForm {
  background: #FFFFFF;
  border: 1px solid var(--fm-border);
  border-radius: 16px;
  padding: 1rem;
}

.fm-nav-note {
  color: var(--fm-ink-soft);
  font-size: 0.94rem;
  margin: 0.2rem 0 1rem 0;
}

.stCodeBlock {
  border-radius: 12px;
  border: 1px solid var(--fm-border);
}
</style>
""",
        unsafe_allow_html=True,
    )


def _currency_short(amount: float) -> str:
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"₹{amount / 100_000:.1f} L"
    return f"₹{amount:,.0f}"


def _score_label(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Promising"
    if score >= 50:
        return "Developing"
    return "Needs work"


def _profile_strength(profile: dict) -> int:
    gpa_score = min(100, int((profile["ug_gpa"] / 10) * 100))
    gre_score = int((profile["gre"] - 260) / 80 * 100)
    gre_score = max(0, min(100, gre_score))
    work_score = min(100, int(profile["work_years"] * 20))
    country_score = min(100, 50 + len(profile["countries"]) * 12)
    return int(0.4 * gpa_score + 0.25 * gre_score + 0.15 * work_score + 0.2 * country_score)


def _stage_completion(stage: str) -> int:
    try:
        return int(((STAGES.index(stage) + 1) / len(STAGES)) * 100)
    except ValueError:
        return 20


def _next_actions(stage: str, score: int) -> list[str]:
    actions = {
        "Exploration": [
            "Lock two target countries and build a focused shortlist.",
            "Use the admit predictor before you spend time on essays.",
            "Run the ROI planner to set a realistic financing ceiling.",
        ],
        "Shortlisting": [
            "Freeze 6 to 8 applications with safe, match, and ambitious picks.",
            "Draft SOP and document requirements before deadlines pile up.",
            "Start a loan precheck now to avoid later drop-off.",
        ],
        "Applications in progress": [
            "Turn timeline milestones into weekly application sprints.",
            "Use mentor support for SOP, LoR, and interview preparation.",
            "Keep the document checklist above 70% completion.",
        ],
        "Admit received": [
            "Compare EMI scenarios with your post-study salary target.",
            "Prepare co-applicant proof and loan paperwork immediately.",
            "Book a callback after selecting your final admit.",
        ],
        "Visa/Onboarding": [
            "Complete finance paperwork before travel documents.",
            "Track visa or fee-payment tasks against the deadline plan.",
            "Keep emergency funds and repayment assumptions conservative.",
        ],
    }
    picks = actions.get(stage, actions["Exploration"]).copy()
    if score < 60:
        picks.insert(0, "Raise your profile strength with tests, projects, or work evidence before applying.")
    return picks[:3]


def _render_metric_card(label: str, value: str, meta: str) -> None:
    st.markdown(
        f"""
<div class="fm-metric-card">
  <div class="label">{escape(label)}</div>
  <div class="value">{escape(value)}</div>
  <div class="meta">{escape(meta)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_story_card(eyebrow: str, headline: str, body: str, tags: list[str] | None = None) -> None:
    tag_html = ""
    if tags:
        tag_html = '<div class="fm-tag-row">' + "".join(
            f'<span class="fm-tag">{escape(tag)}</span>' for tag in tags
        ) + "</div>"
    st.markdown(
        f"""
<div class="fm-story-card">
  <div class="eyebrow">{escape(eyebrow)}</div>
  <div class="headline">{escape(headline)}</div>
  <div class="body">{escape(body)}</div>
  {tag_html}
</div>
""",
        unsafe_allow_html=True,
    )


def _default_profile() -> dict:
    return {
        "full_name": "Aarav Mehta",
        "email": "aarav@example.com",
        "stage": STAGES[0],
        "degree": "B.Tech",
        "target": "Abroad",
        "budget_inr": 2_500_000.0,
        "duration_years": 2.0,
        "ug_gpa": 7.6,
        "gre": 315,
        "work_years": 1.0,
        "dream_salary_lpa": 25,
        "countries": ["US", "Canada"],
        "domain": "Data Science",
    }


def _ensure_state() -> None:
    st.session_state.setdefault("profile", _default_profile())
    st.session_state.setdefault("app_page", "landing")
    st.session_state.setdefault("active_module", "discover")
    st.session_state.setdefault("chat", [])


def _collect_profile_from_inputs() -> dict:
    return {
        "full_name": st.session_state.full_name,
        "email": st.session_state.email,
        "stage": st.session_state.stage,
        "degree": st.session_state.degree,
        "target": st.session_state.target,
        "budget_inr": float(st.session_state.budget_inr),
        "duration_years": float(st.session_state.duration_years),
        "ug_gpa": float(st.session_state.ug_gpa),
        "gre": int(st.session_state.gre),
        "work_years": float(st.session_state.work_years),
        "dream_salary_lpa": int(st.session_state.dream_salary_lpa),
        "countries": st.session_state.countries,
        "domain": st.session_state.domain,
    }


def _compute_insights(profile: dict, universities: list) -> dict:
    recs = recommend_programs(
        universities=universities,
        preferred_countries=profile["countries"],
        domain=profile["domain"],
        budget_inr=profile["budget_inr"],
        ug_gpa=profile["ug_gpa"],
        gre=profile["gre"],
        work_years=profile["work_years"],
        target=profile["target"],
    )
    top_pick = recs[0] if recs else None
    admit_score = admit_probability_score(
        ug_gpa=profile["ug_gpa"],
        gre=profile["gre"],
        work_years=profile["work_years"],
        target=profile["target"],
    )
    tuition_default = 1_200_000 if profile["target"] == "Abroad" else 450_000
    living_default = 600_000 if profile["target"] == "Abroad" else 180_000
    scholarship_default = 200_000 if profile["target"] == "Abroad" else 50_000
    total = total_cost_of_study(
        tuition_per_year_inr=float(tuition_default),
        living_per_year_inr=float(living_default),
        duration_years=profile["duration_years"],
        scholarship_total_inr=float(scholarship_default),
    )
    estimated_loan_needed = max(0.0, total - (0.15 * profile["budget_inr"]))
    estimated_eligibility = eligible_loan_amount_estimate(
        ug_gpa=profile["ug_gpa"],
        gre=profile["gre"],
        work_years=profile["work_years"],
        target=profile["target"],
        declared_budget_inr=profile["budget_inr"],
    )
    return {
        "recs": recs,
        "top_pick": top_pick,
        "admit_score": admit_score,
        "tuition_default": tuition_default,
        "living_default": living_default,
        "scholarship_default": scholarship_default,
        "estimated_total": total,
        "estimated_loan_needed": estimated_loan_needed,
        "estimated_eligibility": estimated_eligibility,
        "journey_progress": _stage_completion(profile["stage"]),
        "readiness_score": _profile_strength(profile),
        "top_country": profile["countries"][0] if profile["countries"] else ("India" if profile["target"] == "Domestic" else "US"),
    }


def _render_sidebar(profile: dict | None) -> None:
    st.sidebar.markdown("## FutureMintAI")
    if not profile:
        st.sidebar.caption("Step 1 of 4")
        st.sidebar.write("Complete your profile on the landing page to start the guided flow.")
        return

    progress = {
        "landing": 25,
        "hub": 50,
        "detail": 100,
    }.get(st.session_state.app_page, 25)
    st.sidebar.caption(f"Step progress: {progress}%")
    st.sidebar.progress(progress / 100)
    st.sidebar.metric("Profile strength", f"{_profile_strength(profile)}/100", _score_label(_profile_strength(profile)))
    st.sidebar.write(f"**Student:** {profile['full_name']}")
    st.sidebar.write(f"**Focus:** {profile['domain']} in {', '.join(profile['countries']) or 'selected countries'}")

    if st.session_state.app_page != "landing":
        if st.sidebar.button("Edit profile", use_container_width=True):
            st.session_state.app_page = "landing"
            st.rerun()
    if st.session_state.app_page == "detail":
        if st.sidebar.button("Back to options", use_container_width=True):
            st.session_state.app_page = "hub"
            st.rerun()


def _render_landing_page(profile: dict) -> None:
    st.markdown(
        """
<div class="fm-kicker">Page 1 of 4</div>
<div class="fm-hero">
  <h1>Start with the student profile.</h1>
  <p>
    This first screen is only for inputs. Fill in the profile once, then FutureMintAI will take you
    to a cleaner options hub instead of showing everything at once.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("student_profile_form"):
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("### Personal and academic")
            st.text_input("Full name", value=profile["full_name"], key="full_name")
            st.text_input("Email", value=profile["email"], key="email")
            st.selectbox("Journey stage", STAGES, index=STAGES.index(profile["stage"]), key="stage")
            st.selectbox("Current degree", ["B.Tech", "B.Sc", "BBA", "B.Com", "BE", "Other"], index=["B.Tech", "B.Sc", "BBA", "B.Com", "BE", "Other"].index(profile["degree"]), key="degree")
            st.selectbox("Study track", ["Abroad", "Domestic"], index=["Abroad", "Domestic"].index(profile["target"]), key="target")
            st.number_input("CGPA (0-10)", min_value=0.0, max_value=10.0, value=float(profile["ug_gpa"]), step=0.1, key="ug_gpa")
            st.number_input("GRE (260-340)", min_value=260, max_value=340, value=int(profile["gre"]), step=1, key="gre")
        with right:
            st.markdown("### Budget and preferences")
            st.number_input("Work experience (years)", min_value=0.0, value=float(profile["work_years"]), step=0.5, key="work_years")
            st.number_input("Budget (₹)", min_value=50_000, value=int(profile["budget_inr"]), step=50_000, key="budget_inr")
            st.number_input("Program duration (years)", min_value=1.0, value=float(profile["duration_years"]), step=0.5, key="duration_years")
            st.number_input("Dream salary (LPA)", min_value=3, max_value=200, value=int(profile["dream_salary_lpa"]), step=1, key="dream_salary_lpa")
            st.multiselect(
                "Preferred countries",
                ["US", "UK", "Canada", "Germany", "Ireland", "Australia", "Netherlands"],
                default=profile["countries"],
                key="countries",
            )
            st.selectbox(
                "Preferred field",
                ["Computer Science", "Data Science", "MBA", "Finance", "Product", "Mechanical"],
                index=["Computer Science", "Data Science", "MBA", "Finance", "Product", "Mechanical"].index(profile["domain"]),
                key="domain",
            )

        submitted = st.form_submit_button("Continue", use_container_width=True, type="primary")
        if submitted:
            st.session_state.profile = _collect_profile_from_inputs()
            st.session_state.app_page = "hub"
            st.rerun()


def _render_options_hub(profile: dict, insights: dict) -> None:
    st.markdown(
        f"""
<div class="fm-kicker">Page 2 of 4</div>
<div class="fm-hero">
  <h1>Choose one path for {escape(profile["full_name"])}.</h1>
  <p>
    This screen shows all major options, but only as entry points. Click any option and FutureMintAI
    will open the focused detail screen instead of stacking everything here.
  </p>
  <div class="fm-pill-row">
    <span class="fm-pill">{escape(profile["domain"])}</span>
    <span class="fm-pill">{escape(insights["top_country"])}</span>
    <span class="fm-pill">{insights["readiness_score"]}/100 readiness</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<p class="fm-nav-note">Use the button below to go back and edit the input form, or open any module to continue.</p>', unsafe_allow_html=True)

    back_col, spacer_col = st.columns([0.22, 0.78])
    with back_col:
        if st.button("Back to inputs", use_container_width=True):
            st.session_state.app_page = "landing"
            st.rerun()

    cards = [
        ("discover", "Discover Fit", "Explore best-fit countries, universities, and programs.", f"Top pick: {insights['top_pick'].university if insights['top_pick'] else 'No match yet'}"),
        ("prepare", "Prepare", "See admit confidence, milestones, and execution planning.", f"Admit score: {insights['admit_score']}/100"),
        ("finance", "Finance & Convert", "Review total cost, eligibility, EMI, and loan readiness.", f"Eligibility: {_currency_short(insights['estimated_eligibility'])}"),
        ("mentor", "Mentor", "Open the AI mentor for interactive guidance and next steps.", "Use guided prompts or ask your own question."),
    ]

    cols = st.columns(2, gap="large")
    for idx, (module_id, title, body, meta) in enumerate(cards):
        with cols[idx % 2]:
            _render_story_card("Option", title, body, [meta])
            if st.button(f"Open {title}", key=f"open_{module_id}", use_container_width=True):
                st.session_state.active_module = module_id
                st.session_state.app_page = "detail"
                st.rerun()


def _render_discover_module(profile: dict, insights: dict) -> None:
    st.markdown('<div class="fm-panel"><span class="fm-section-label">Career navigator</span><h3>Best-fit matching</h3><p>Focused recommendations for country, university, and program fit.</p></div>', unsafe_allow_html=True)
    if insights["top_pick"]:
        _render_story_card(
            "Top recommendation",
            f'{insights["top_pick"].program} at {insights["top_pick"].university}',
            f'Best current fit in {insights["top_pick"].country} with strong affordability and admit balance.',
            [
                f'Overall {insights["top_pick"].overall_score_0_100}/100',
                f'Cost {_currency_short(insights["top_pick"].est_total_cost_inr)}',
                f'Salary {_currency_short(insights["top_pick"].est_first_year_salary_inr)}',
            ],
        )
    st.dataframe([asdict(r) for r in insights["recs"]], use_container_width=True, hide_index=True)


def _render_prepare_module(profile: dict, insights: dict) -> None:
    st.markdown('<div class="fm-panel"><span class="fm-section-label">Preparation</span><h3>Admit readiness and timeline</h3><p>See where the application stands and what should happen next.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([0.85, 1.15], gap="large")
    with left:
        st.progress(insights["admit_score"] / 100.0)
        st.metric("Admission probability score", f'{insights["admit_score"]}/100', _score_label(insights["admit_score"]))
        for tip in admit_probability_tips(insights["admit_score"]):
            st.write(f"- {tip}")
    with right:
        start = st.date_input("Start date", value=date.today())
        target_term = st.selectbox("Target intake", ["Fall", "Spring"], index=0)
        tl = build_timeline(start_date=start, target_intake=target_term, target=profile["target"])
        st.dataframe(tl, use_container_width=True, hide_index=True)


def _render_finance_module(profile: dict, insights: dict) -> None:
    st.markdown('<div class="fm-panel"><span class="fm-section-label">Finance and conversion</span><h3>ROI, eligibility, and loan readiness</h3><p>Financial planning and the loan funnel are grouped into one focused workspace.</p></div>', unsafe_allow_html=True)
    tuition = st.number_input("Tuition per year (₹)", min_value=0, value=insights["tuition_default"], step=50_000)
    living = st.number_input("Living per year (₹)", min_value=0, value=insights["living_default"], step=25_000)
    scholarship = st.number_input("Scholarship total (₹)", min_value=0, value=insights["scholarship_default"], step=25_000)
    total = total_cost_of_study(
        tuition_per_year_inr=float(tuition),
        living_per_year_inr=float(living),
        duration_years=profile["duration_years"],
        scholarship_total_inr=float(scholarship),
    )
    loan_needed = max(0.0, total - (0.15 * profile["budget_inr"]))
    est_eligible = eligible_loan_amount_estimate(
        ug_gpa=profile["ug_gpa"],
        gre=profile["gre"],
        work_years=profile["work_years"],
        target=profile["target"],
        declared_budget_inr=profile["budget_inr"],
    )
    a, b, c = st.columns(3)
    with a:
        st.metric("Total study cost", _currency_short(total))
    with b:
        st.metric("Likely loan need", _currency_short(loan_needed))
    with c:
        st.metric("Estimated eligibility", _currency_short(est_eligible))
    rate = st.slider("Interest rate (annual %)", min_value=6.0, max_value=16.0, value=11.0, step=0.1)
    tenure_years = st.slider("Tenure (years)", min_value=3, max_value=15, value=10, step=1)
    principal = st.number_input("Principal (₹)", min_value=0, value=int(min(loan_needed, est_eligible)), step=50_000)
    monthly = emi(principal=float(principal), annual_rate_pct=float(rate), tenure_years=int(tenure_years))
    st.metric("Estimated EMI", f"{_currency_short(monthly)} / month")
    st.dataframe(repayment_scenarios(principal=float(principal)), use_container_width=True, hide_index=True)
    st.success(f"Estimated eligible loan amount: {_currency_short(est_eligible)}")


def _render_mentor_module(profile: dict) -> None:
    st.markdown('<div class="fm-panel"><span class="fm-section-label">Mentor</span><h3>Ask for help</h3><p>Use the mentor as a dedicated screen instead of mixing chat into the dashboard.</p></div>', unsafe_allow_html=True)
    suggestions = [
        "How do I shortlist safe, match, and ambitious universities?",
        "What documents should I prepare before a loan precheck?",
        "How should I improve my profile in the next 60 days?",
    ]
    cols = st.columns(3)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx]:
            _render_story_card("Prompt idea", suggestion, "Useful starter prompt for a hesitant student.")

    copilot = MentorCopilot(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask about applications, ROI, loans, visa prep, or next best actions...")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        answer = copilot.reply(prompt=prompt, profile=profile)
        st.session_state.chat.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)


def _render_detail_page(profile: dict, insights: dict) -> None:
    module_titles = {
        "discover": "Discover Fit",
        "prepare": "Prepare",
        "finance": "Finance & Convert",
        "mentor": "Mentor",
    }
    active_title = module_titles[st.session_state.active_module]
    st.markdown(
        f"""
<div class="fm-kicker">Page 4 of 4</div>
<div class="fm-hero">
  <h1>{escape(active_title)}</h1>
  <p>
    You are now on the focused module screen. This keeps the experience clean by showing just one workflow at a time.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<p class="fm-nav-note">Use the navigation buttons to return to the options hub or jump to another module directly.</p>', unsafe_allow_html=True)

    nav_cols = st.columns(5)
    with nav_cols[0]:
        if st.button("Back to options", use_container_width=True):
            st.session_state.app_page = "hub"
            st.rerun()
    for idx, module_id in enumerate(module_titles, start=1):
        with nav_cols[idx]:
            if st.button(module_titles[module_id], key=f"switch_{module_id}", use_container_width=True):
                st.session_state.active_module = module_id
                st.rerun()

    if st.session_state.active_module == "discover":
        _render_discover_module(profile, insights)
    elif st.session_state.active_module == "prepare":
        _render_prepare_module(profile, insights)
    elif st.session_state.active_module == "finance":
        _render_finance_module(profile, insights)
    else:
        _render_mentor_module(profile)


def main() -> None:
    load_dotenv()
    _set_page()
    _inject_theme()
    _ensure_state()

    profile = st.session_state.profile
    _render_sidebar(profile if st.session_state.app_page != "landing" else None)
    universities = load_universities()
    insights = _compute_insights(profile, universities)

    if st.session_state.app_page == "landing":
        _render_landing_page(profile)
    elif st.session_state.app_page == "hub":
        _render_options_hub(profile, insights)
    else:
        _render_detail_page(profile, insights)


if __name__ == "__main__":
    main()
