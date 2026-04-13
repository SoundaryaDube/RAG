from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass(frozen=True)
class MentorCopilot:
    api_key: Optional[str]
    model: str

    def reply(self, *, prompt: str, profile: dict) -> str:
        if not self.api_key:
            return self._fallback(prompt=prompt, profile=profile)
        try:
            return self._openai(prompt=prompt, profile=profile)
        except Exception:
            # demo should never crash even if key is invalid/rate-limited
            return self._fallback(prompt=prompt, profile=profile)

    def _fallback(self, *, prompt: str, profile: dict) -> str:
        stage = profile.get("stage", "Exploration")
        target = profile.get("target", "Abroad")
        countries = profile.get("countries", [])
        domain = profile.get("domain", "Data Science")
        return "\n".join(
            [
                f"You’re currently in **{stage}** stage for **{target}** studies ({domain}).",
                "",
                "Here’s a quick, practical answer (demo mode):",
                f"- If you’re targeting {', '.join(countries) or 'your preferred countries'}, shortlist 6–8 programs (2 safe / 4 match / 2 ambitious).",
                "- Build a weekly plan: tests → SOP/LoRs → applications → loan precheck → docs checklist.",
                "- For loan readiness: finalize co-applicant income docs early and keep a clean checklist.",
                "",
                f"Your question was: {prompt}",
                "",
                "If you add `OPENAI_API_KEY`, I can respond in a more personalized, conversational way.",
            ]
        )

    def _openai(self, *, prompt: str, profile: dict) -> str:
        """
        Minimal OpenAI Responses-style call. Works if the key is present; otherwise we fallback.
        """
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        system = (
            "You are a helpful mentor for Indian students planning higher studies. "
            "Be concise, actionable, and include checklists. "
            "Always connect guidance back to next best action in the platform and the loan readiness steps."
        )
        user = {
            "prompt": prompt,
            "profile": {
                "stage": profile.get("stage"),
                "target": profile.get("target"),
                "countries": profile.get("countries"),
                "domain": profile.get("domain"),
                "ug_gpa": profile.get("ug_gpa"),
                "gre": profile.get("gre"),
                "work_years": profile.get("work_years"),
                "budget_inr": profile.get("budget_inr"),
            },
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user)},
            ],
            "temperature": 0.4,
        }
        with httpx.Client(timeout=20.0) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"].strip()

