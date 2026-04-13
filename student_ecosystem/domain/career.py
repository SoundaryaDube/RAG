from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz

from student_ecosystem.domain.finance import total_cost_of_study
from student_ecosystem.domain.universities import UniversityProgram, filter_programs


@dataclass(frozen=True)
class ProgramRecommendation:
    university: str
    country: str
    program: str
    est_total_cost_inr: float
    est_first_year_salary_inr: float
    affordability_score_0_100: int
    admit_fit_score_0_100: int
    overall_score_0_100: int


def _affordability(total_cost_inr: float, budget_inr: float) -> int:
    if budget_inr <= 0:
        return 0
    ratio = total_cost_inr / budget_inr
    # <= 1.0 is best; > 2.0 becomes quite hard
    if ratio <= 0.9:
        return 95
    if ratio <= 1.0:
        return 90
    if ratio <= 1.2:
        return 75
    if ratio <= 1.5:
        return 55
    if ratio <= 2.0:
        return 35
    return 15


def _admit_fit(ug_gpa: float, gre: int, typical_gpa: float, typical_gre: int, work_years: float) -> int:
    gpa_gap = ug_gpa - typical_gpa
    gpa_score = 50 + int(gpa_gap * 18)
    gpa_score = max(0, min(100, gpa_score))

    if typical_gre <= 0:
        gre_score = 70
    else:
        gre_gap = gre - typical_gre
        gre_score = 50 + int(gre_gap * 1.5)
        gre_score = max(0, min(100, gre_score))

    work_bonus = min(15, int(work_years * 5))
    return max(0, min(100, int(0.55 * gpa_score + 0.45 * gre_score) + work_bonus))


def recommend_programs(
    *,
    universities: list[UniversityProgram],
    preferred_countries: list[str],
    domain: str,
    budget_inr: float,
    ug_gpa: float,
    gre: int,
    work_years: float,
    target: str,
    top_k: int = 10,
) -> list[ProgramRecommendation]:
    programs = filter_programs(
        universities,
        preferred_countries=preferred_countries,
        domain=domain,
        target=target,
    )
    if not programs:
        # fallback: best-effort fuzzy domain match, to keep demo robust
        best = sorted(
            universities,
            key=lambda p: fuzz.token_set_ratio(p.domain, domain),
            reverse=True,
        )
        programs = best[: min(10, len(best))]

    recs: list[ProgramRecommendation] = []
    for p in programs:
        total = total_cost_of_study(
            tuition_per_year_inr=float(p.tuition_per_year_inr),
            living_per_year_inr=float(p.living_per_year_inr),
            duration_years=float(p.duration_years),
            scholarship_total_inr=0.0,
        )
        affordability = _affordability(total, budget_inr)
        admit_fit = _admit_fit(ug_gpa, gre, p.typical_gpa, p.typical_gre, work_years)
        overall = int(0.45 * affordability + 0.55 * admit_fit)
        recs.append(
            ProgramRecommendation(
                university=p.university,
                country=p.country,
                program=p.program,
                est_total_cost_inr=float(total),
                est_first_year_salary_inr=float(p.avg_start_salary_inr),
                affordability_score_0_100=int(affordability),
                admit_fit_score_0_100=int(admit_fit),
                overall_score_0_100=int(overall),
            )
        )

    recs.sort(key=lambda r: (r.overall_score_0_100, r.affordability_score_0_100), reverse=True)
    return recs[:top_k]

