"""LLM 提供商抽象基类 + 注册表"""

import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

_REGISTRY = {}


def register(name):
    def decorator(cls):
        _REGISTRY[name] = cls
        return cls
    return decorator


class LLMProvider(ABC):
    def __init__(self, api_key: str, model: str, temperature: float = 0.1):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def call(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        ...


def get_provider(cfg_llm: dict) -> LLMProvider:
    """根据配置实例化对应的 LLM 提供商"""
    # 触发注册
    from . import openrouter, openai_provider, gemini, claude  # noqa: F401

    name = cfg_llm["provider"]
    if name not in _REGISTRY:
        raise ValueError(f"未知的 LLM 提供商: {name}，可选: {list(_REGISTRY.keys())}")
    cls = _REGISTRY[name]
    return cls(
        api_key=cfg_llm["api_key"],
        model=cfg_llm["model"],
        temperature=cfg_llm.get("temperature", 0.1),
    )
