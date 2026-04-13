from __future__ import annotations


STAGES = [
    "Exploration",
    "Shortlisting",
    "Applications in progress",
    "Admit received",
    "Visa/Onboarding",
]


def generate_nudges(profile: dict) -> list[str]:
    stage = profile.get("stage", "Exploration")
    target = profile.get("target", "Abroad")
    domain = profile.get("domain", "Data Science")
    countries = profile.get("countries", [])

    if stage == "Exploration":
        return [
            f"Try the Career Navigator for {domain} options in {', '.join(countries) or 'your preferred countries'}.",
            "Save 3 programs to unlock a 'shortlist score' (demo).",
            "Take the ROI check: cost vs expected salary.",
        ]
    if stage == "Shortlisting":
        return [
            "Generate your application timeline and set weekly goals.",
            "Check admission probability and get improvement tips.",
            "Run a loan eligibility precheck to reduce last-minute friction.",
        ]
    if stage == "Applications in progress":
        return [
            "Upload/prepare documents checklist to reduce drop-offs.",
            "Set reminders for deadlines and test dates (demo).",
            "Ask Mentor Copilot to polish your SOP outline.",
        ]
    if stage == "Admit received":
        return [
            "Compare repayment scenarios and decide a safe EMI range.",
            "Start the loan application draft with autofill.",
            f"Next step: {'Visa planning' if target == 'Abroad' else 'Fee payment planning'}.",
        ]
    return [
        "Finalize doc checklist and timelines.",
        "Book an advisor callback (demo) for last-mile support.",
        "Invite a friend via referral to unlock rewards (demo).",
    ]

