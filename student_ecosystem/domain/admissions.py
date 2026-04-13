from __future__ import annotations


def admit_probability_score(*, ug_gpa: float, gre: int, work_years: float, target: str) -> int:
    """
    A transparent scoring model for demo purposes.
    Output is 0-100.
    """
    gpa = max(0.0, min(10.0, ug_gpa))
    gpa_score = (gpa / 10.0) * 55.0

    if target == "Domestic":
        gre_score = 10.0
    else:
        gre_clamped = max(260, min(340, gre))
        gre_score = ((gre_clamped - 260) / (340 - 260)) * 30.0

    work_score = min(15.0, work_years * 5.0)
    score = int(round(gpa_score + gre_score + work_score))
    return max(0, min(100, score))


def admit_probability_tips(score: int) -> list[str]:
    if score >= 80:
        return [
            "Target a balanced shortlist (safe/match/ambitious).",
            "Invest in SOP and strong LoRs to differentiate.",
            "Start early on scholarship and assistantship opportunities.",
        ]
    if score >= 60:
        return [
            "Raise GRE/standardized tests if your target country needs it.",
            "Build 1-2 standout projects aligned to your program.",
            "Refine SOP narrative to show clarity of goals.",
        ]
    return [
        "Consider strengthening GPA via final-year performance or relevant certifications.",
        "Add internships/projects to demonstrate readiness.",
        "Pick programs where prerequisites match your background to improve fit.",
    ]

