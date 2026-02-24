"""
文献简报生成器 - 自动从 PubMed 获取最新文献并生成 Obsidian 简报
翻译与亮点均通过 OpenRouter Gemini Flash 实现
"""

import requests
import xml.etree.ElementTree as ET
import json
import os
import sys
import socket
import time
import logging
import ctypes
import tkinter as tk
from datetime import datetime, timedelta

# ============ 加载配置 ============
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as _f:
    CFG = json.load(_f)

OBSIDIAN_VAULT = CFG["obsidian_vault"]
BRIEFING_FOLDER = CFG["briefing_folder"]
PUBMED_API_KEY = CFG.get("pubmed_api_key", "")
OPENROUTER_KEY = CFG.get("openrouter_api_key", "")
OPENROUTER_MODEL = CFG.get("openrouter_model", "google/gemini-2.0-flash-001")
CORE_JOURNALS = CFG["core_journals"]
EXTENDED_JOURNALS = CFG["extended_journals"]
KEYWORDS = CFG["keywords"]
SPECIES_FILTER = CFG.get("species_filter", [])
MAX_RESULTS = CFG.get("max_results", 200)
DEFAULT_LOOKBACK_DAYS = CFG.get("default_lookback_days", 7)

STATE_FILE = "last_fetch_state.json"
LOG_FILE = os.path.join(SCRIPT_DIR, "briefing.log")
PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger(__name__)


# ============ 工具函数 ============

def check_internet(timeout=5):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


def get_state_path():
    return os.path.join(OBSIDIAN_VAULT, BRIEFING_FOLDER, STATE_FILE)


def load_state():
    path = get_state_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_fetch": None, "seen_pmids": []}


def save_state(state):
    path = get_state_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ============ 翻译（OpenRouter Gemini Flash） ============

def _openrouter_call(prompt, system="", max_tokens=2000):
    """调用 OpenRouter API"""
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                 "Content-Type": "application/json"},
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                *([{"role": "system", "content": system}] if system else []),
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def translate(text):
    """用 Gemini Flash 翻译英文为中文"""
    if not text or not text.strip():
        return text
    try:
        return _openrouter_call(
            text,
            system="你是专业的学术翻译。将以下英文学术文本翻译成中文，保持术语准确。只输出译文，不要添加任何解释或前缀。",
        )
    except Exception as e:
        log.warning(f"翻译失败，保留原文: {e}")
        return text


def translate_papers(papers):
    """批量翻译论文标题和摘要"""
    total = len(papers)
    for idx, p in enumerate(papers):
        log.info(f"  翻译 [{idx + 1}/{total}] {p['pmid']}")
        p["title_zh"] = translate(p["title"])
        time.sleep(0.2)
        abstract_raw = p["abstract"]
        if len(abstract_raw) > 800:
            abstract_raw = abstract_raw[:800] + "..."
        p["abstract_zh"] = translate(abstract_raw)
        time.sleep(0.3)
    return papers


# ============ LLM 本期亮点 ============

def generate_highlights(all_papers):
    """用 Gemini Flash 从所有文献中挑选本期亮点"""
    if not OPENROUTER_KEY or not all_papers:
        return ""
    paper_list = "\n".join(
        f"{i+1}. [{p['journal_abbr']}] {p['title']}"
        for i, p in enumerate(all_papers)
    )
    prompt = f"""以下是本期文献简报中的所有论文（共{len(all_papers)}篇）。
请从中挑选最值得神经科学研究者关注的3-5篇，用中文简要说明每篇为什么值得关注（每篇1-2句话）。
关注标准：方法学突破、重要发现、临床转化价值、领域热点。

{paper_list}

请以Markdown列表格式输出，每篇用 - 开头，包含论文序号。"""
    try:
        log.info("生成本期亮点...")
        return _openrouter_call(prompt, max_tokens=1500)
    except Exception as e:
        log.warning(f"生成亮点失败: {e}")
        return ""


# ============ 通知弹窗（不抢焦点） ============

def _make_popup(title_text, body_text, buttons=None, countdown_sec=0):
    result = {"clicked": None}
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.configure(bg="#1e1e2e")

    w, h = 400, 150
    sx, sy = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = sx - w - 16, sy - h - 50
    root.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(root, text=title_text, font=("Microsoft YaHei", 12, "bold"),
             bg="#1e1e2e", fg="#cdd6f4").pack(pady=(12, 4))
    msg_label = tk.Label(root, text=body_text, font=("Microsoft YaHei", 10),
                         bg="#1e1e2e", fg="#a6adc8", wraplength=370)
    msg_label.pack(pady=4)

    if buttons:
        bf = tk.Frame(root, bg="#1e1e2e")
        bf.pack(pady=10)
        for name, label in buttons:
            def _click(n=name):
                result["clicked"] = n
                root.destroy()
            tk.Button(bf, text=label, command=_click, font=("Microsoft YaHei", 9),
                      width=10, relief="flat", bg="#313244", fg="#cdd6f4",
                      activebackground="#45475a", activeforeground="#cdd6f4",
                      cursor="hand2").pack(side="left", padx=8)

    remaining = [countdown_sec]
    def _tick():
        if remaining[0] <= 0:
            if result["clicked"] is None:
                result["clicked"] = "timeout"
            root.destroy()
            return
        remaining[0] -= 1
        if countdown_sec > 0:
            msg_label.config(text=f"{body_text}（{remaining[0]}s）")
        root.after(1000, _tick)
    if countdown_sec > 0:
        root.after(1000, _tick)

    root.deiconify()
    root.update_idletasks()
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        ctypes.windll.user32.SetWindowPos(hwnd, -1, x, y, w, h, 0x0010)
    except Exception:
        root.attributes("-topmost", True)
    root.mainloop()
    return result["clicked"]


def notify_start():
    clicked = _make_popup(
        "文献简报", "即将开始检索最新文献，如需取消请点击「取消」",
        buttons=[("go", "开始检索"), ("cancel", "取消")], countdown_sec=30)
    return clicked != "cancel"


def notify_done(total, filepath):
    fname = os.path.basename(filepath)
    _make_popup("文献简报完成", f"共检索到 {total} 篇新文献，已保存至 {fname}",
                buttons=[("ok", "知道了")], countdown_sec=10)


# ============ PubMed API ============

def _pubmed_params(extra=None):
    params = {"db": "pubmed", "retmode": "json"}
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY
    if extra:
        params.update(extra)
    return params


def pubmed_search(query, retmax=MAX_RESULTS):
    url = f"{PUBMED_BASE}/esearch.fcgi"
    params = _pubmed_params({"term": query, "retmax": retmax, "sort": "pub_date"})
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("esearchresult", {}).get("idlist", [])


def pubmed_fetch(pmids):
    if not pmids:
        return []
    papers = []
    for i in range(0, len(pmids), 50):
        batch = pmids[i:i + 50]
        params = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
        if PUBMED_API_KEY:
            params["api_key"] = PUBMED_API_KEY
        resp = requests.get(f"{PUBMED_BASE}/efetch.fcgi", params=params, timeout=60)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        for article in root.findall(".//PubmedArticle"):
            paper = parse_article(article)
            if paper:
                papers.append(paper)
        time.sleep(0.15)  # API key 允许更高频率
    return papers


def parse_article(article):
    try:
        medline = article.find(".//MedlineCitation")
        pmid = medline.findtext(".//PMID")
        art = medline.find(".//Article")
        title = art.findtext(".//ArticleTitle", "")
        abstract_parts = []
        for at in art.findall(".//Abstract/AbstractText"):
            label = at.get("Label", "")
            txt = ET.tostring(at, encoding="unicode", method="text").strip()
            abstract_parts.append(f"**{label}**: {txt}" if label else txt)
        abstract = " ".join(abstract_parts)
        journal = art.findtext(".//Journal/Title", "")
        journal_abbr = art.findtext(".//Journal/ISOAbbreviation", "")
        pub_date = art.find(".//Journal/JournalIssue/PubDate")
        date_str = ""
        if pub_date is not None:
            y, m, d = (pub_date.findtext("Year", ""),
                       pub_date.findtext("Month", ""),
                       pub_date.findtext("Day", ""))
            date_str = f"{y} {m} {d}".strip()
        doi = ""
        for eid in article.findall(".//ArticleIdList/ArticleId"):
            if eid.get("IdType") == "doi":
                doi = eid.text or ""
                break
        authors = []
        for au in art.findall(".//AuthorList/Author"):
            last = au.findtext("LastName", "")
            first = au.findtext("ForeName", "")
            if last:
                authors.append(f"{last} {first}".strip())
        return {"pmid": pmid, "title": title, "abstract": abstract,
                "journal": journal, "journal_abbr": journal_abbr,
                "date": date_str, "doi": doi, "authors": authors}
    except Exception as e:
        log.warning(f"解析文献失败: {e}")
        return None


# ============ 查询构建 ============

def build_core_query(date_from, date_to):
    journals = " OR ".join(f'"{j}"[Journal]' for j in CORE_JOURNALS)
    return f'({journals}) AND ("{date_from}"[PDAT] : "{date_to}"[PDAT])'


def build_keyword_query(date_from, date_to):
    journals = " OR ".join(f'"{j}"[Journal]' for j in EXTENDED_JOURNALS)
    keywords = " OR ".join(f'"{k}"[Title/Abstract]' for k in KEYWORDS)
    query = f'({keywords}) AND ({journals}) AND ("{date_from}"[PDAT] : "{date_to}"[PDAT])'
    if SPECIES_FILTER:
        species = " OR ".join(SPECIES_FILTER)
        query += f" AND ({species})"
    return query


# ============ Markdown 生成 ============

def format_paper(paper):
    link = f"https://doi.org/{paper['doi']}" if paper["doi"] else \
           f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"
    title_zh = paper.get("title_zh", "")
    lines = []
    if title_zh and title_zh != paper["title"]:
        lines.append(f"#### {title_zh}")
        lines.append(f"*{paper['title']}*  [链接]({link})")
    else:
        lines.append(f"#### [{paper['title']}]({link})")
    authors_str = ", ".join(paper["authors"][:5])
    if len(paper["authors"]) > 5:
        authors_str += " et al."
    lines.append(f"- Authors: {authors_str}")
    lines.append(f"- Date: {paper['date']}  |  PMID: {paper['pmid']}")
    abstract_zh = paper.get("abstract_zh", "")
    if abstract_zh:
        lines.append(f"\n> {abstract_zh}")
    elif paper["abstract"]:
        trunc = paper["abstract"][:600]
        if len(paper["abstract"]) > 600:
            trunc += "..."
        lines.append(f"\n> {trunc}")
    lines.append("")
    return lines


def generate_markdown(core_papers, kw_papers, date_from, date_to, highlights=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 文献简报 {now}", "",
        f"> 检索范围: {date_from} ~ {date_to}",
        f"> 核心期刊: {len(core_papers)} 篇 | 神经调控扩展: {len(kw_papers)} 篇", "",
    ]
    if not core_papers and not kw_papers:
        lines.append("本次检索未发现新文献。")
        return "\n".join(lines)

    # 本期亮点
    if highlights:
        lines += ["---", "## 本期亮点", "", highlights, ""]

    # 核心期刊
    if core_papers:
        lines += ["---", "## 核心期刊最新文献", ""]
        by_journal = {}
        for p in core_papers:
            by_journal.setdefault(p["journal_abbr"] or p["journal"], []).append(p)
        for journal, papers in by_journal.items():
            lines.append(f"### {journal}（{len(papers)} 篇）")
            lines.append("")
            for p in papers:
                lines.extend(format_paper(p))

    # 扩展期刊
    if kw_papers:
        lines += ["---", "## 神经调控相关文献（扩展期刊）", ""]
        by_journal = {}
        for p in kw_papers:
            by_journal.setdefault(p["journal_abbr"] or p["journal"], []).append(p)
        for journal, papers in by_journal.items():
            lines.append(f"### {journal}（{len(papers)} 篇）")
            lines.append("")
            for p in papers:
                lines.extend(format_paper(p))

    return "\n".join(lines)


# ============ 主流程 ============

def main():
    log.info("=" * 40)
    log.info("文献简报生成器启动")

    if not check_internet():
        log.error("无法连接互联网，退出。")
        sys.exit(1)
    log.info("网络连接正常")

    if not notify_start():
        log.info("用户取消了检索。")
        sys.exit(0)

    output_dir = os.path.join(OBSIDIAN_VAULT, BRIEFING_FOLDER)
    os.makedirs(output_dir, exist_ok=True)

    state = load_state()
    seen_pmids = set(state.get("seen_pmids", []))

    if state["last_fetch"]:
        date_from = state["last_fetch"]
    else:
        date_from = (datetime.now() - timedelta(days=DEFAULT_LOOKBACK_DAYS)).strftime("%Y/%m/%d")
    date_to = datetime.now().strftime("%Y/%m/%d")
    log.info(f"检索范围: {date_from} ~ {date_to}")

    log.info("检索核心期刊...")
    core_pmids = pubmed_search(build_core_query(date_from, date_to))
    core_pmids = [p for p in core_pmids if p not in seen_pmids]
    log.info(f"  核心期刊新文献: {len(core_pmids)} 篇")
    time.sleep(0.15)

    log.info("检索神经调控关键词...")
    kw_pmids = pubmed_search(build_keyword_query(date_from, date_to))
    kw_pmids = [p for p in kw_pmids if p not in seen_pmids and p not in set(core_pmids)]
    log.info(f"  扩展期刊新文献: {len(kw_pmids)} 篇")

    log.info("获取文献详情...")
    core_papers = pubmed_fetch(core_pmids)
    kw_papers = pubmed_fetch(kw_pmids)
    total = len(core_papers) + len(kw_papers)
    log.info(f"共获取 {total} 篇文献")

    if core_papers:
        log.info("翻译核心期刊文献...")
        translate_papers(core_papers)
    if kw_papers:
        log.info("翻译扩展期刊文献...")
        translate_papers(kw_papers)

    highlights = generate_highlights(core_papers + kw_papers)

    markdown = generate_markdown(core_papers, kw_papers, date_from, date_to, highlights)
    filename = f"文献简报_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    log.info(f"简报已保存: {filepath}")

    all_new = core_pmids + kw_pmids
    new_seen = list(seen_pmids | set(all_new))[-5000:]
    save_state({"last_fetch": datetime.now().strftime("%Y/%m/%d"), "seen_pmids": new_seen})
    log.info(f"完成！共 {total} 篇新文献。")

    notify_done(total, filepath)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-notify", action="store_true")
    args = parser.parse_args()
    if args.no_notify:
        notify_start = lambda: True
        notify_done = lambda *a: None
    main()
