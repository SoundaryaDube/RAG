from __future__ import annotations

from datetime import date, timedelta


def build_timeline(*, start_date: date, target_intake: str, target: str) -> list[dict]:
    """
    Simple timeline generator for demo.
    Produces milestones with suggested dates.
    """
    weeks = 1
    if target == "Domestic":
        base = [
            ("Shortlist programs/institutes", 1),
            ("Prepare tests / entrance (if needed)", 6),
            ("Collect transcripts & documents", 2),
            ("Applications submission", 8),
            ("Interviews / follow-ups", 4),
            ("Financing plan + loan precheck", 2),
            ("Confirm admission + pay fees", 2),
        ]
    else:
        base = [
            ("Country & program shortlist", 2),
            ("GRE/IELTS/TOEFL plan", 8),
            ("SOP/LoR drafting", 5),
            ("University applications", 6),
            ("Loan eligibility + co-applicant prep", 3),
            ("Visa documents + appointments", 5),
            ("Pre-departure planning", 3),
        ]

    # Small adjustment for spring intake
    intake_shift = -2 if target_intake == "Spring" else 0

    rows = []
    cursor = start_date
    for label, dur_weeks in base:
        dur = max(1, dur_weeks + intake_shift if "Visa" not in label else dur_weeks)
        end = cursor + timedelta(days=dur * 7)
        rows.append(
            {
                "milestone": label,
                "start": cursor.isoformat(),
                "end": end.isoformat(),
            }
        )
        cursor = end + timedelta(days=weeks * 7)
    return rows

