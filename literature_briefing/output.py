"""Markdown 简报生成"""

from datetime import datetime
from typing import List
from .sources.base import Paper


def format_paper(paper: Paper) -> list:
    link = paper.url
    lines = []
    if paper.title_zh and paper.title_zh != paper.title:
        lines.append(f"#### {paper.title_zh}")
        lines.append(f"*{paper.title}*  [链接]({link})")
    else:
        lines.append(f"#### [{paper.title}]({link})")

    authors_str = ", ".join(paper.authors[:5])
    if len(paper.authors) > 5:
        authors_str += " et al."
    lines.append(f"- Authors: {authors_str}")

    meta = f"- Date: {paper.date}"
    if paper.source == "pubmed":
        meta += f"  |  PMID: {paper.source_id}"
    elif paper.source == "arxiv":
        meta += f"  |  arXiv: {paper.source_id}"
        if paper.categories:
            meta += f"  |  {', '.join(paper.categories[:3])}"
    lines.append(meta)

    if paper.abstract_zh:
        lines.append(f"\n> {paper.abstract_zh}")
    elif paper.abstract:
        trunc = paper.abstract[:600]
        if len(paper.abstract) > 600:
            trunc += "..."
        lines.append(f"\n> {trunc}")
    lines.append("")
    return lines


def generate_markdown(papers_by_source: dict, date_from: str, date_to: str,
                      highlights: str = "") -> str:
    """生成完整的 Markdown 简报

    papers_by_source: {"pubmed": {"core": [...], "extended": [...]}, "arxiv": [...]}
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = sum(
        len(ps) if isinstance(ps, list) else sum(len(v) for v in ps.values())
        for ps in papers_by_source.values()
    )

    lines = [f"# 文献简报 {now}", "",
             f"> 检索范围: {date_from} ~ {date_to}"]

    # 统计行
    stats = []
    for source_name, ps in papers_by_source.items():
        if isinstance(ps, dict):
            for group, group_papers in ps.items():
                stats.append(f"{source_name}/{group}: {len(group_papers)} 篇")
        else:
            stats.append(f"{source_name}: {len(ps)} 篇")
    lines.append(f"> {' | '.join(stats)}")
    lines.append("")

    if total == 0:
        lines.append("本次检索未发现新文献。")
        return "\n".join(lines)

    # 本期亮点
    if highlights:
        lines += ["---", "## 本期亮点", "", highlights, ""]

    # PubMed 核心期刊
    pubmed_data = papers_by_source.get("pubmed", {})
    if isinstance(pubmed_data, dict):
        core = pubmed_data.get("core", [])
        extended = pubmed_data.get("extended", [])

        if core:
            lines += ["---", "## 核心期刊最新文献", ""]
            lines.extend(_group_by_journal(core))

        if extended:
            lines += ["---", "## 关键词相关文献（扩展期刊）", ""]
            lines.extend(_group_by_journal(extended))

    # arXiv
    arxiv_papers = papers_by_source.get("arxiv", [])
    if arxiv_papers:
        lines += ["---", "## arXiv 预印本", ""]
        for p in arxiv_papers:
            lines.extend(format_paper(p))

    return "\n".join(lines)


def _group_by_journal(papers: List[Paper]) -> list:
    by_journal = {}
    for p in papers:
        key = p.journal_abbr or p.journal
        by_journal.setdefault(key, []).append(p)
    lines = []
    for journal, jpapers in by_journal.items():
        lines.append(f"### {journal}（{len(jpapers)} 篇）")
        lines.append("")
        for p in jpapers:
            lines.extend(format_paper(p))
    return lines
