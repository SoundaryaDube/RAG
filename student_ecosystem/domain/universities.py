from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class UniversityProgram:
    university: str
    country: str
    program: str
    domain: str
    duration_years: float
    tuition_per_year_inr: float
    living_per_year_inr: float
    typical_gre: int
    typical_gpa: float
    avg_start_salary_inr: float


def _data_path() -> Path:
    # Keep data small and explicit for hackathon demos.
    return Path(__file__).resolve().parents[2] / "data" / "universities.json"


def load_universities() -> list[UniversityProgram]:
    p = _data_path()
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [UniversityProgram(**item) for item in raw]


def filter_programs(
    programs: Iterable[UniversityProgram],
    *,
    preferred_countries: list[str],
    domain: str,
    target: str,
) -> list[UniversityProgram]:
    if target == "Domestic":
        # For the prototype we treat "India" as domestic.
        preferred = {"India"}
    else:
        preferred = set(preferred_countries)

    return [
        p
        for p in programs
        if (p.country in preferred) and (p.domain == domain)
    ]

