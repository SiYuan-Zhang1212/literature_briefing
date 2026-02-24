"""Google Gemini 原生 API 提供商"""

import requests
from .base import LLMProvider, register


@register("gemini")
class GeminiProvider(LLMProvider):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def call(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"

        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": system}]})
            contents.append({"role": "model", "parts": [{"text": "好的，我会按照要求执行。"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": contents,
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
