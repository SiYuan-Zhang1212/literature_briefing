"""翻译逻辑"""

import time
import logging
from typing import List
from .sources.base import Paper
from .llm.base import LLMProvider

log = logging.getLogger(__name__)

SYSTEM_PROMPT = "你是专业的学术翻译。将以下英文学术文本翻译成中文，保持术语准确。只输出译文，不要添加任何解释或前缀。"


def translate_text(llm: LLMProvider, text: str) -> str:
    if not text or not text.strip():
        return text
    try:
        return llm.call(text, system=SYSTEM_PROMPT)
    except Exception as e:
        log.warning(f"翻译失败，保留原文: {e}")
        return text


def translate_papers(llm: LLMProvider, papers: List[Paper]):
    total = len(papers)
    for idx, p in enumerate(papers):
        log.info(f"  翻译 [{idx + 1}/{total}] {p.source_id}")
        p.title_zh = translate_text(llm, p.title)
        time.sleep(0.2)
        abstract_raw = p.abstract
        if len(abstract_raw) > 800:
            abstract_raw = abstract_raw[:800] + "..."
        p.abstract_zh = translate_text(llm, abstract_raw)
        time.sleep(0.3)
