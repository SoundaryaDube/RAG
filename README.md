# Unified Student Engagement Ecosystem (AI-first)

Prototype for **TenzorX 2026 National AI Hackathon** – Problem Statement 2: *Building a Unified Student Engagement Ecosystem for Education and Financing Choices*.

## What this demo includes
- **Engagement (Top-of-funnel)**: Career Navigator, ROI/EMI, Admission Probability, Application Timeline, Mentor Copilot (chat).
- **AI-led growth hooks** (simulated): persona-based journeys, streaks, nudges, referral prompts.
- **Conversion (Loan funnel)**: eligibility estimate, repayment scenarios, doc checklist, AI-assisted application draft.

## Run locally
1. Install Python 3.10+.
2. Create a venv and install deps:

```bash
pip install -r requirements.txt
```

3. (Optional) set LLM key:
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

4. Start the app:

```bash
streamlit run app.py
```

## Project structure
- `app.py`: Streamlit UI (single entrypoint)
- `student_ecosystem/`: domain logic (scoring, calculators, journeys, copy)
- `data/`: small sample datasets used by the prototype
- `docs/`: slide outlines and architecture notes (generated manually)
