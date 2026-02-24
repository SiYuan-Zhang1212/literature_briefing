"""OpenRouter 提供商（OpenAI 兼容格式）"""

import requests
from .base import LLMProvider, register


@register("openrouter")
class OpenRouterProvider(LLMProvider):
    URL = "https://openrouter.ai/api/v1/chat/completions"

    def call(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = requests.post(
            self.URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
            },
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
