from __future__ import annotations

import math

import numpy as np


def total_cost_of_study(
    *,
    tuition_per_year_inr: float,
    living_per_year_inr: float,
    duration_years: float,
    scholarship_total_inr: float,
) -> float:
    gross = (tuition_per_year_inr + living_per_year_inr) * duration_years
    return max(0.0, gross - scholarship_total_inr)


def emi(*, principal: float, annual_rate_pct: float, tenure_years: int) -> float:
    if principal <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    n = tenure_years * 12
    if r <= 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def repayment_scenarios(principal: float) -> list[dict]:
    scenarios = []
    for annual_rate_pct, tenure_years in [
        (9.5, 8),
        (11.0, 10),
        (12.5, 12),
    ]:
        scenarios.append(
            {
                "rate_%": annual_rate_pct,
                "tenure_years": tenure_years,
                "emi_inr": round(emi(principal=principal, annual_rate_pct=annual_rate_pct, tenure_years=tenure_years)),
            }
        )
    return scenarios


def eligible_loan_amount_estimate(
    *,
    ug_gpa: float,
    gre: int,
    work_years: float,
    target: str,
    declared_budget_inr: float,
) -> float:
    """
    Heuristic estimator for demo. Replace with NBFC rules + bureau + income + co-applicant model later.
    """
    base = 2_000_000 if target == "Domestic" else 4_000_000

    gpa_factor = np.interp(ug_gpa, [5.5, 7.0, 8.5, 10.0], [0.6, 0.9, 1.1, 1.25])
    gre_factor = 1.0 if target == "Domestic" else np.interp(gre, [290, 305, 320, 335], [0.7, 0.9, 1.05, 1.2])
    work_factor = min(1.15, 0.95 + 0.05 * max(0.0, work_years))
    budget_cap = max(1_000_000.0, 0.9 * declared_budget_inr)

    eligible = base * float(gpa_factor) * float(gre_factor) * float(work_factor)
    return float(min(eligible, budget_cap))

