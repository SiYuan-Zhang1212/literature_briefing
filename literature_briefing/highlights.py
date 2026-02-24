"""亮点生成"""

import logging
from typing import List
from .sources.base import Paper
from .llm.base import LLMProvider

log = logging.getLogger(__name__)


def generate_highlights(llm: LLMProvider, papers: List[Paper]) -> str:
    if not papers:
        return ""
    paper_list = "\n".join(
        f"{i+1}. [{p.journal_abbr}] {p.title}"
        for i, p in enumerate(papers)
    )
    prompt = f"""以下是本期文献简报中的所有论文（共{len(papers)}篇）。
请从中挑选最值得关注的3-5篇，用中文简要说明每篇为什么值得关注（每篇1-2句话）。
关注标准：方法学突破、重要发现、临床转化价值、领域热点。

{paper_list}

请以Markdown列表格式输出，每篇用 - 开头，包含论文序号。"""
    try:
        log.info("生成本期亮点...")
        return llm.call(prompt, max_tokens=1500)
    except Exception as e:
        log.warning(f"生成亮点失败: {e}")
        return ""
