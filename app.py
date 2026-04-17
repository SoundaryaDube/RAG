import os
from dataclasses import asdict
from datetime import date
from html import escape

import streamlit as st
from dotenv import load_dotenv

from student_ecosystem.domain.admissions import admit_probability_score, admit_probability_tips
from student_ecosystem.domain.career import recommend_programs
from student_ecosystem.domain.copy import STAGES, generate_nudges
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
  --fm-ink: #10233d;
  --fm-ink-soft: #4a607d;
  --fm-surface: rgba(255, 255, 255, 0.84);
  --fm-surface-strong: rgba(255, 255, 255, 0.94);
  --fm-border: rgba(27, 72, 129, 0.14);
  --fm-primary: #0d6e8f;
  --fm-primary-2: #19a7a3;
  --fm-secondary: #ff9b54;
  --fm-secondary-2: #ffd166;
  --fm-success: #1b8f67;
  --fm-danger: #d75a4a;
  --fm-shadow: 0 18px 40px rgba(16, 35, 61, 0.08);
}

.stApp {
  color: var(--fm-ink);
  font-family: "Trebuchet MS", "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(255, 209, 102, 0.35), transparent 28%),
    radial-gradient(circle at 88% 12%, rgba(25, 167, 163, 0.22), transparent 24%),
    linear-gradient(180deg, #f7f2e8 0%, #f2f7fb 42%, #eef5fa 100%);
}

[data-testid="stHeader"] {
  background: rgba(247, 242, 232, 0.72);
}

[data-testid="stSidebar"] {
  background:
    linear-gradient(180deg, rgba(14, 57, 93, 0.98) 0%, rgba(8, 35, 61, 0.98) 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] * {
  color: #eef8ff !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: rgba(238, 248, 255, 0.76) !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
  background: rgba(255, 255, 255, 0.08) !important;
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
  background:
    radial-gradient(circle at top right, rgba(255, 209, 102, 0.34), transparent 28%),
    linear-gradient(135deg, #0e4065 0%, #0c6b8f 44%, #1baea4 100%);
  border-radius: 28px;
  padding: 1.6rem 1.6rem 1.4rem 1.6rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 30px 60px rgba(8, 35, 61, 0.22);
  color: #f8feff;
  margin-bottom: 1rem;
}

.fm-hero::after {
  content: "";
  position: absolute;
  inset: auto -12% -28% auto;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  filter: blur(6px);
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
  color: rgba(248, 254, 255, 0.88);
}

.fm-pill-row {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.fm-pill {
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.14);
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 700;
}

.fm-panel {
  background: var(--fm-surface);
  backdrop-filter: blur(12px);
  border: 1px solid var(--fm-border);
  border-radius: 24px;
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
  background: var(--fm-surface-strong);
  border: 1px solid rgba(27, 72, 129, 0.12);
  border-radius: 20px;
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
  background: linear-gradient(180deg, rgba(255,255,255,0.94) 0%, rgba(249,253,255,0.94) 100%);
  border: 1px solid rgba(27, 72, 129, 0.12);
  border-radius: 22px;
  padding: 1rem;
  box-shadow: 0 12px 28px rgba(16, 35, 61, 0.06);
  margin-bottom: 0.9rem;
}

.fm-story-card .eyebrow {
  color: var(--fm-secondary);
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
  background: rgba(13, 110, 143, 0.08);
  color: var(--fm-primary);
}

.fm-score-card {
  background:
    radial-gradient(circle at top right, rgba(255, 209, 102, 0.18), transparent 32%),
    linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(242,248,251,0.96) 100%);
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
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(27, 72, 129, 0.1);
  border-radius: 18px;
  padding: 0.6rem 0.7rem;
}

div[data-testid="stMetricLabel"] {
  color: var(--fm-ink-soft);
  font-weight: 700;
}

button[kind="primary"],
.stButton > button {
  border: none !important;
  color: #083347 !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, var(--fm-secondary-2) 0%, var(--fm-secondary) 100%) !important;
  border-radius: 14px !important;
  box-shadow: 0 12px 24px rgba(255, 155, 84, 0.22) !important;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.45rem;
  margin-bottom: 0.6rem;
}

.stTabs [data-baseweb="tab"] {
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(27, 72, 129, 0.12);
  border-radius: 999px;
  color: var(--fm-ink);
  font-weight: 700;
  padding: 0.45rem 1rem;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #0d6e8f 0%, #19a7a3 100%) !important;
  color: #f8feff !important;
  border: none !important;
}

.stProgress > div > div > div > div {
  background: linear-gradient(90deg, #ffd166 0%, #ff9b54 45%, #19a7a3 100%);
}

div[data-testid="stExpander"] {
  border: 1px solid rgba(27, 72, 129, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
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


def _sidebar_profile() -> dict:
    st.sidebar.markdown("## FutureMintAI")
    st.sidebar.caption("Student command center for discovery, admissions, and loan readiness")

    full_name = st.sidebar.text_input("Full name", value="Aarav Mehta")
    email = st.sidebar.text_input("Email", value="aarav@example.com")
    stage = st.sidebar.selectbox("Journey stage", STAGES, index=0)
    degree = st.sidebar.selectbox("Current degree", ["B.Tech", "B.Sc", "BBA", "B.Com", "BE", "Other"], index=0)

    st.sidebar.markdown("### Academic profile")
    target = st.sidebar.selectbox("Study track", ["Abroad", "Domestic"])
    ug_gpa = st.sidebar.number_input("CGPA (0-10)", min_value=0.0, max_value=10.0, value=7.6, step=0.1)
    gre = st.sidebar.number_input("GRE (260-340)", min_value=260, max_value=340, value=315, step=1)
    work_years = st.sidebar.number_input("Work experience (years)", min_value=0.0, value=1.0, step=0.5)

    st.sidebar.markdown("### Budget and goals")
    budget = st.sidebar.number_input("Budget (₹)", min_value=50_000, value=2_500_000, step=50_000)
    years = st.sidebar.number_input("Program duration (years)", min_value=1.0, value=2.0, step=0.5)
    dream_salary_lpa = st.sidebar.number_input("Dream salary (LPA)", min_value=3, max_value=200, value=25, step=1)

    st.sidebar.markdown("### Preferences")
    countries = st.sidebar.multiselect(
        "Preferred countries",
        ["US", "UK", "Canada", "Germany", "Ireland", "Australia", "Netherlands"],
        default=["US", "Canada"],
    )
    domain = st.sidebar.selectbox(
        "Preferred field",
        ["Computer Science", "Data Science", "MBA", "Finance", "Product", "Mechanical"],
        index=1,
    )

    profile = {
        "full_name": full_name,
        "email": email,
        "stage": stage,
        "degree": degree,
        "target": target,
        "budget_inr": float(budget),
        "duration_years": float(years),
        "ug_gpa": float(ug_gpa),
        "gre": int(gre),
        "work_years": float(work_years),
        "dream_salary_lpa": int(dream_salary_lpa),
        "countries": countries,
        "domain": domain,
    }

    strength = _profile_strength(profile)
    progress = _stage_completion(stage)
    st.sidebar.markdown("### Readiness snapshot")
    st.sidebar.progress(progress / 100)
    st.sidebar.caption(f"Journey completion: {progress}%")
    st.sidebar.metric("Profile strength", f"{strength}/100", _score_label(strength))

    st.sidebar.markdown("### Smart nudges")
    for nudge in generate_nudges(profile):
        st.sidebar.info(nudge)

    return profile


def main() -> None:
    load_dotenv()
    _set_page()
    _inject_theme()

    profile = _sidebar_profile()
    universities = load_universities()
    readiness_score = _profile_strength(profile)
    journey_progress = _stage_completion(profile["stage"])
    top_country = profile["countries"][0] if profile["countries"] else ("India" if profile["target"] == "Domestic" else "US")

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
    timeline = build_timeline(
        start_date=date.today(),
        target_intake="Fall",
        target=profile["target"],
    )

    st.markdown(
        f"""
<div class="fm-kicker">AI-first student engagement ecosystem</div>
<div class="fm-hero">
  <h1>Plan your higher-ed journey like a product, not a paperwork maze.</h1>
  <p>
    FutureMintAI turns discovery, admissions, financial planning, and loan conversion into one
    guided experience for <strong>{escape(profile["full_name"])}</strong>. Right now your focus is
    <strong>{escape(profile["domain"])}</strong> in <strong>{escape(top_country)}</strong>, and the
    platform is tuned for the <strong>{escape(profile["stage"])}</strong> stage.
  </p>
  <div class="fm-pill-row">
    <span class="fm-pill">{escape(profile["target"])} track</span>
    <span class="fm-pill">{escape(profile["degree"])}</span>
    <span class="fm-pill">{journey_progress}% journey progress</span>
    <span class="fm-pill">{readiness_score}/100 profile strength</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    overview_left, overview_right = st.columns([1.45, 1], gap="large")

    with overview_left:
        st.markdown('<div class="fm-panel"><span class="fm-section-label">Mission control</span><h3>Your snapshot</h3><p>A fast read on profile readiness, affordability, and near-term momentum.</p></div>', unsafe_allow_html=True)
        metric_cols = st.columns(4)
        with metric_cols[0]:
            _render_metric_card("CGPA", f'{profile["ug_gpa"]:.1f}/10', "Academic foundation")
        with metric_cols[1]:
            _render_metric_card("Dream salary", f'{profile["dream_salary_lpa"]} LPA', "Outcome ambition")
        with metric_cols[2]:
            _render_metric_card("Budget", _currency_short(profile["budget_inr"]), "Declared spend capacity")
        with metric_cols[3]:
            _render_metric_card("Admit score", f"{admit_score}/100", _score_label(admit_score))

        highlight_cols = st.columns([1.15, 0.85], gap="medium")
        with highlight_cols[0]:
            if top_pick:
                _render_story_card(
                    "Top recommendation",
                    f"{top_pick.program} at {top_pick.university}",
                    f"Best current fit across affordability, admissions fit, and early salary upside in {top_pick.country}.",
                    [
                        f"Overall {top_pick.overall_score_0_100}/100",
                        f"Cost {_currency_short(top_pick.est_total_cost_inr)}",
                        f"Salary {_currency_short(top_pick.est_first_year_salary_inr)}",
                    ],
                )
            else:
                _render_story_card(
                    "Top recommendation",
                    "No exact program match yet",
                    "Try widening country filters or switching domains to unlock stronger recommendations.",
                    ["Fuzzy fallback available", "Profile can be broadened"],
                )
        with highlight_cols[1]:
            _render_story_card(
                "Conversion pulse",
                "Loan readiness is already visible in the journey",
                f"Estimated eligibility is {_currency_short(estimated_eligibility)} against a likely funding need of {_currency_short(estimated_loan_needed)}.",
                ["Eligibility estimate", "Repayment planner", "Document funnel"],
            )

    with overview_right:
        st.markdown(
            f"""
<div class="fm-panel fm-score-card">
  <span class="fm-section-label">Next moves</span>
  <h3>What should happen this week?</h3>
  <p>The product brief rewards stickiness and conversion, so this view keeps the student moving forward with timely prompts.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        for idx, action in enumerate(_next_actions(profile["stage"], admit_score), start=1):
            _render_story_card(f"Action {idx}", action, "Designed to reduce drop-off and keep the journey feeling guided, not overwhelming.")

    tab_overview, tab_discover, tab_prepare, tab_convert, tab_mentor = st.tabs(
        ["Overview", "Discover Fit", "Prepare", "Finance & Convert", "Mentor"]
    )

    with tab_overview:
        col1, col2, col3 = st.columns(3)
        with col1:
            _render_story_card(
                "Sticky loop",
                "Students keep returning because every step reveals the next one",
                "Recommendations, admit confidence, financing, and nudges live in a single flow rather than disconnected tools.",
                ["Personalized nudges", "Stage-aware content", "Habit loop"],
            )
        with col2:
            _render_story_card(
                "Growth angle",
                "Built to feel shareable and mentor-friendly",
                "The interface surfaces clear scores, top picks, and callbacks that can easily power referrals, WhatsApp shares, and counselor follow-ups.",
                ["Referral prompts", "Callback CTA", "Content hooks"],
            )
        with col3:
            _render_story_card(
                "Business outcome",
                "Discovery naturally leads into loan awareness",
                "Funding readiness is not buried in a separate journey, which makes awareness-to-conversion feel much more seamless for students.",
                ["Loan discovery", "Doc readiness", "Higher intent"],
            )

        st.markdown('<div class="fm-panel"><span class="fm-section-label">Shortlist preview</span><h3>Your best-fit programs</h3><p>High-confidence recommendations are surfaced as digestible cards first, with full tables available when needed.</p></div>', unsafe_allow_html=True)
        preview_cols = st.columns(3)
        for idx, rec in enumerate(recs[:3]):
            with preview_cols[idx]:
                _render_story_card(
                    f"Rank #{idx + 1}",
                    f"{rec.university}, {rec.country}",
                    f"{rec.program} balances fit and affordability for your current profile.",
                    [
                        f"Overall {rec.overall_score_0_100}",
                        f"Admit {rec.admit_fit_score_0_100}",
                        f"Affordable {rec.affordability_score_0_100}",
                    ],
                )

        with st.expander("Open full recommendation table"):
            st.dataframe([asdict(r) for r in recs], use_container_width=True, hide_index=True)

    with tab_discover:
        left, right = st.columns([1.15, 0.85], gap="large")
        with left:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">Career navigator</span><h3>AI best-fit matching</h3><p>Country, university, and course guidance generated from budget, profile strength, work experience, and target market.</p></div>', unsafe_allow_html=True)
            st.dataframe([asdict(r) for r in recs], use_container_width=True, hide_index=True)
        with right:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">Admit readiness</span><h3>Where you stand today</h3><p>This scoring block gives the student a sense of traction while also nudging them toward specific actions.</p></div>', unsafe_allow_html=True)
            st.progress(admit_score / 100.0)
            st.metric("Admission probability score", f"{admit_score}/100", _score_label(admit_score))
            st.markdown("**Improvement levers**")
            for tip in admit_probability_tips(admit_score):
                st.write(f"- {tip}")
            _render_story_card(
                "Signal",
                f"{_score_label(admit_score)} admission profile",
                "This panel creates an immediate feedback loop, which is useful both for engagement and for guiding counselor or AI follow-up.",
                ["Predictive scoring", "Actionable feedback"],
            )

    with tab_prepare:
        roadmap_col, timeline_col = st.columns([1, 1], gap="large")
        with roadmap_col:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">Roadmap generator</span><h3>Execution blueprint</h3><p>From shortlist to loan prep, these are the core milestones the student should push through next.</p></div>', unsafe_allow_html=True)
            roadmap_items = [
                f"Complete profile strength upgrades for {profile['domain']} applications.",
                f"Apply to 6 to 8 programs across {', '.join(profile['countries']) if profile['countries'] else 'your selected markets'}.",
                "Build SOP, LoR, project proof, and interview narrative before deadline pressure builds.",
                f"Align post-study roles with a {profile['dream_salary_lpa']} LPA salary ambition.",
            ]
            for idx, item in enumerate(roadmap_items, start=1):
                _render_story_card(f"Milestone {idx}", item, "Sequenced for momentum, clarity, and stronger conversion later in the funnel.")

        with timeline_col:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">Timeline planner</span><h3>Execution timeline</h3><p>A milestone view makes deadlines feel concrete and reduces the chaos of a fragmented application journey.</p></div>', unsafe_allow_html=True)
            start = st.date_input("Start date", value=date.today())
            target_term = st.selectbox("Target intake", ["Fall", "Spring"], index=0)
            tl = build_timeline(start_date=start, target_intake=target_term, target=profile["target"])
            for row in tl[:5]:
                _render_story_card(
                    "Timeline step",
                    row["milestone"],
                    f'{row["start"]} to {row["end"]}',
                    ["Stage-aligned", "Deadline visible"],
                )
            with st.expander("Open full timeline table"):
                st.dataframe(tl, use_container_width=True, hide_index=True)

    with tab_convert:
        fin_left, fin_right = st.columns([0.95, 1.05], gap="large")
        with fin_left:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">ROI and lending</span><h3>Financial planning</h3><p>Affordability and lending fit are treated as part of the student journey, not a separate back-office step.</p></div>', unsafe_allow_html=True)
            tuition = st.number_input("Tuition per year (₹)", min_value=0, value=tuition_default, step=50_000)
            living = st.number_input("Living per year (₹)", min_value=0, value=living_default, step=25_000)
            scholarship = st.number_input("Scholarship total (₹)", min_value=0, value=scholarship_default, step=25_000)

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

        with fin_right:
            st.markdown('<div class="fm-panel"><span class="fm-section-label">Loan funnel</span><h3>Application readiness</h3><p>A guided conversion lane makes the financing step feel transparent and less intimidating for the student.</p></div>', unsafe_allow_html=True)
            st.success(f"Estimated eligible loan amount: {_currency_short(est_eligible)}")

            docs = [
                "ID proof (Aadhaar/PAN/Passport)",
                "Academic transcripts",
                "Admission letter or offer letter",
                "Bank statements or co-applicant income proof",
                "Visa or onboarding documents",
                "Statement of Purpose draft",
            ]
            checked = {doc: st.checkbox(doc, value=False) for doc in docs}
            completed = sum(1 for done in checked.values() if done)
            st.progress(completed / len(docs))
            st.caption(f"Checklist completion: {completed}/{len(docs)}")

            st.markdown("**AI-assisted draft**")
            name = st.text_input("Applicant name", value=profile["full_name"])
            institute = st.text_input("Target institute", value=top_pick.university if top_pick else "Target University")
            purpose = st.text_area(
                "Purpose summary",
                value="I want to pursue postgraduate study to unlock stronger role-fit, global exposure, and higher earning potential.",
            )
            st.code(
                "\n".join(
                    [
                        "LOAN APPLICATION (DRAFT)",
                        f"- Name: {name}",
                        f"- Study track: {profile['target']}",
                        f"- Institute: {institute}",
                        f"- Domain: {profile['domain']}",
                        f"- Estimated eligibility: {_currency_short(est_eligible)}",
                        f"- Notes: {purpose}",
                    ]
                )
            )
            st.button("Book a 15-minute advisor callback")

    with tab_mentor:
        st.markdown('<div class="fm-panel"><span class="fm-section-label">Conversational copilot</span><h3>Ask for help at any point in the journey</h3><p>The mentor layer keeps the product feeling alive even when the student is confused, stuck, or comparing options late in the funnel.</p></div>', unsafe_allow_html=True)
        prompt_suggestions = st.columns(3)
        suggestions = [
            "How do I shortlist safe, match, and ambitious universities?",
            "What documents should I prepare before a loan precheck?",
            "How should I improve my profile in the next 60 days?",
        ]
        for idx, suggestion in enumerate(suggestions):
            with prompt_suggestions[idx]:
                _render_story_card("Prompt idea", suggestion, "Useful starter prompt for a hesitant student.", ["Mentor-ready"])

        st.write(
            "If `OPENAI_API_KEY` is set, responses come from an LLM. Otherwise, the app uses a deterministic mentor response."
        )
        copilot = MentorCopilot(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

        if "chat" not in st.session_state:
            st.session_state.chat = []

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


if __name__ == "__main__":
    main()
