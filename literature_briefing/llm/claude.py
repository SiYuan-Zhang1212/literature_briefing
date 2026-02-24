"""Anthropic Claude 原生 API 提供商"""

import requests
from .base import LLMProvider, register


@register("claude")
class ClaudeProvider(LLMProvider):
    URL = "https://api.anthropic.com/v1/messages"

    def call(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        resp = requests.post(
            self.URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip()
