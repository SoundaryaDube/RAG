import os
from dataclasses import asdict
from datetime import date

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
        page_title="Unified Student Engagement Ecosystem",
        page_icon="🎓",
        layout="wide",
    )


def _sidebar_profile() -> dict:
    st.sidebar.header("Student profile")
    stage = st.sidebar.selectbox("Journey stage", STAGES, index=0)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        target = st.selectbox("Target", ["Abroad", "Domestic"])
        budget = st.number_input("Budget (₹)", min_value=50_000, value=2_500_000, step=50_000)
        years = st.number_input("Program duration (years)", min_value=1.0, value=2.0, step=0.5)
    with col2:
        ug_gpa = st.number_input("UG GPA (0-10)", min_value=0.0, max_value=10.0, value=7.6, step=0.1)
        gre = st.number_input("GRE (260-340)", min_value=260, max_value=340, value=315, step=1)
        work_years = st.number_input("Work exp (years)", min_value=0.0, value=1.0, step=0.5)

    st.sidebar.subheader("Preferences")
    countries = st.sidebar.multiselect(
        "Preferred countries",
        ["US", "UK", "Canada", "Germany", "Ireland", "Australia", "Netherlands"],
        default=["US", "Canada"],
    )
    domain = st.sidebar.selectbox(
        "Domain",
        ["Computer Science", "Data Science", "MBA", "Finance", "Product", "Mechanical"],
        index=1,
    )

    return {
        "stage": stage,
        "target": target,
        "budget_inr": float(budget),
        "duration_years": float(years),
        "ug_gpa": float(ug_gpa),
        "gre": int(gre),
        "work_years": float(work_years),
        "countries": countries,
        "domain": domain,
    }


def main() -> None:
    load_dotenv()
    _set_page()

    st.title("Unified Student Engagement Ecosystem (AI-first)")
    st.caption("Engage → educate → build trust → convert to education loan application")

    profile = _sidebar_profile()
    universities = load_universities()

    st.sidebar.subheader("Smart nudges")
    nudges = generate_nudges(profile)
    for n in nudges:
        st.sidebar.info(n)

    tabs = st.tabs(
        [
            "AI Career Navigator",
            "ROI & Planning",
            "Admission Probability",
            "Application Timeline",
            "Mentor Copilot",
            "Loan Funnel",
        ]
    )

    with tabs[0]:
        st.subheader("AI Career Navigator")
        st.write(
            "Recommendations below combine your profile + preferences with a simple scoring model "
            "(works without an API key)."
        )
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
        st.dataframe([asdict(r) for r in recs], use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("ROI & Financial Planning")
        st.write("Compare total cost and repayment scenarios (simulated).")

        col1, col2, col3 = st.columns(3)
        with col1:
            tuition = st.number_input("Tuition per year (₹)", min_value=0, value=1_200_000, step=50_000)
        with col2:
            living = st.number_input("Living per year (₹)", min_value=0, value=600_000, step=25_000)
        with col3:
            scholarship = st.number_input("Scholarship total (₹)", min_value=0, value=200_000, step=25_000)

        total = total_cost_of_study(
            tuition_per_year_inr=float(tuition),
            living_per_year_inr=float(living),
            duration_years=profile["duration_years"],
            scholarship_total_inr=float(scholarship),
        )
        st.metric("Estimated total cost (₹)", f"{total:,.0f}")

        loan_needed = max(0.0, total - (0.15 * profile["budget_inr"]))
        est_eligible = eligible_loan_amount_estimate(
            ug_gpa=profile["ug_gpa"],
            gre=profile["gre"],
            work_years=profile["work_years"],
            target=profile["target"],
            declared_budget_inr=profile["budget_inr"],
        )
        colA, colB = st.columns(2)
        with colA:
            st.metric("Estimated loan needed (₹)", f"{loan_needed:,.0f}")
        with colB:
            st.metric("Estimated eligibility (₹)", f"{est_eligible:,.0f}")

        st.divider()
        st.subheader("Repayment scenarios")
        rate = st.slider("Interest rate (annual %)", min_value=6.0, max_value=16.0, value=11.0, step=0.1)
        tenure_years = st.slider("Tenure (years)", min_value=3, max_value=15, value=10, step=1)
        principal = st.number_input("Principal (₹)", min_value=0, value=int(min(loan_needed, est_eligible)), step=50_000)

        monthly = emi(principal=float(principal), annual_rate_pct=float(rate), tenure_years=int(tenure_years))
        st.metric("Estimated EMI (₹ / month)", f"{monthly:,.0f}")
        st.dataframe(
            repayment_scenarios(principal=float(principal)),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[2]:
        st.subheader("Admission Probability Predictor")
        st.write("A transparent scoring model (demo). Replace with ML later.")
        score = admit_probability_score(
            ug_gpa=profile["ug_gpa"],
            gre=profile["gre"],
            work_years=profile["work_years"],
            target=profile["target"],
        )
        st.progress(score / 100.0)
        st.metric("Score (0-100)", f"{score}")
        st.write("How to improve:")
        for tip in admit_probability_tips(score):
            st.write(f"- {tip}")

    with tabs[3]:
        st.subheader("Application Timeline Generator")
        start = st.date_input("Start date", value=date.today())
        target_term = st.selectbox("Target intake", ["Fall", "Spring"], index=0)
        tl = build_timeline(start_date=start, target_intake=target_term, target=profile["target"])
        st.dataframe(tl, use_container_width=True, hide_index=True)

    with tabs[4]:
        st.subheader("Conversational Mentor / Copilot")
        st.write(
            "If `OPENAI_API_KEY` is set, responses come from an LLM. Otherwise, you get a deterministic demo mentor."
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

        prompt = st.chat_input("Ask anything about studying abroad/domestic, admissions, loans, docs...")
        if prompt:
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            answer = copilot.reply(prompt=prompt, profile=profile)
            st.session_state.chat.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.write(answer)

    with tabs[5]:
        st.subheader("Loan Funnel (Conversion)")
        st.write("A guided flow that turns engagement into a loan application-ready packet.")

        st.markdown("**1) Eligibility check**")
        eligible = eligible_loan_amount_estimate(
            ug_gpa=profile["ug_gpa"],
            gre=profile["gre"],
            work_years=profile["work_years"],
            target=profile["target"],
            declared_budget_inr=profile["budget_inr"],
        )
        st.success(f"Estimated eligible loan amount: ₹{eligible:,.0f}")

        st.markdown("**2) Document checklist + autofill draft**")
        docs = [
            "ID proof (Aadhaar/PAN/Passport)",
            "Academic transcripts",
            "Admission letter / offer letter (if available)",
            "Bank statements / income proof (co-applicant)",
            "Visa/I-20/CAS (if applicable)",
            "Statement of Purpose (SOP) draft",
        ]
        checked = {d: st.checkbox(d, value=False) for d in docs}
        done = sum(1 for v in checked.values() if v)
        st.write(f"Checklist completion: **{done}/{len(docs)}**")

        st.markdown("**3) AI-assisted application draft (simulated)**")
        name = st.text_input("Full name", value="Student Name")
        institute = st.text_input("Institute / University", value="Target University")
        purpose = st.text_area("Purpose (2-3 lines)", value="PG program to improve career outcomes.")

        st.code(
            "\n".join(
                [
                    "LOAN APPLICATION (DRAFT)",
                    f"- Name: {name}",
                    f"- Target: {profile['target']}",
                    f"- Institute: {institute}",
                    f"- Domain: {profile['domain']}",
                    f"- Estimated eligibility: ₹{eligible:,.0f}",
                    f"- Notes: {purpose}",
                ]
            )
        )

        st.markdown("**4) Next best action**")
        st.write("Based on your stage, we’d trigger nudges (email/WhatsApp/push) and a call-back slot.")
        st.button("Book a 15-min loan advisor callback (demo)")


if __name__ == "__main__":
    main()

