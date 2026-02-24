"""文献简报生成器 - 入口与流程编排"""

import os
import sys
import json
import socket
import logging
from datetime import datetime, timedelta

from .config import load_config, save_config, get_env_fallback, SCRIPT_DIR
from .llm import get_provider
from .sources.pubmed import PubMedSource
from .sources.arxiv import ArxivSource
from .translator import translate_papers
from .highlights import generate_highlights
from .output import generate_markdown
from .notify import notify_start, notify_done

STATE_FILE = "last_fetch_state.json"
LOG_FILE = os.path.join(SCRIPT_DIR, "briefing.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def check_internet(timeout=5):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


def _get_state_path(cfg):
    return os.path.join(cfg["output_path"], cfg["output_folder"], STATE_FILE)


def _load_state(cfg):
    path = _get_state_path(cfg)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_fetch": None, "seen_ids": []}


def _save_state(cfg, state):
    path = _get_state_path(cfg)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    log.info("=" * 40)
    log.info("文献简报生成器启动")

    cfg = get_env_fallback(load_config())

    if not check_internet():
        log.error("无法连接互联网，退出。")
        sys.exit(1)
    log.info("网络连接正常")

    # 弹窗确认
    no_notify = "--no-notify" in sys.argv
    if not no_notify and not notify_start(cfg["schedule"]):
        log.info("用户取消了检索。")
        sys.exit(0)

    output_dir = os.path.join(cfg["output_path"], cfg["output_folder"])
    os.makedirs(output_dir, exist_ok=True)

    state = _load_state(cfg)
    seen_ids = set(state.get("seen_ids", []) + state.get("seen_pmids", []))

    if state["last_fetch"]:
        date_from = state["last_fetch"]
    else:
        date_from = (datetime.now() - timedelta(days=cfg["default_lookback_days"])).strftime("%Y/%m/%d")
    date_to = datetime.now().strftime("%Y/%m/%d")
    log.info(f"检索范围: {date_from} ~ {date_to}")

    # 初始化 LLM
    llm = None
    if cfg["llm"]["api_key"]:
        try:
            llm = get_provider(cfg["llm"])
        except Exception as e:
            log.warning(f"LLM 初始化失败: {e}")

    # 收集所有文献
    papers_by_source = {}
    all_papers = []
    new_ids = []

    # PubMed
    if cfg["sources"]["pubmed"]["enabled"]:
        pm = PubMedSource(cfg["sources"]["pubmed"])
        pm_papers = pm.search(date_from, date_to, cfg["max_results"], seen_ids)
        core = [p for p in pm_papers if "core" in p.categories]
        extended = [p for p in pm_papers if "extended" in p.categories]
        papers_by_source["pubmed"] = {"core": core, "extended": extended}
        all_papers.extend(pm_papers)
        new_ids.extend(p.source_id for p in pm_papers)

    # arXiv
    if cfg["sources"]["arxiv"]["enabled"]:
        ax = ArxivSource(cfg["sources"]["arxiv"])
        ax_papers = ax.search(date_from, date_to, cfg["max_results"], seen_ids)
        papers_by_source["arxiv"] = ax_papers
        all_papers.extend(ax_papers)
        new_ids.extend(p.source_id for p in ax_papers)

    total = len(all_papers)
    log.info(f"共获取 {total} 篇文献")

    # 翻译
    if llm and cfg["llm"].get("enable_translation", True) and all_papers:
        log.info("翻译文献...")
        translate_papers(llm, all_papers)

    # 亮点
    highlights = ""
    if llm and cfg["llm"].get("enable_highlights", True) and all_papers:
        highlights = generate_highlights(llm, all_papers)

    # 生成 Markdown
    markdown = generate_markdown(papers_by_source, date_from, date_to, highlights)
    filename = f"文献简报_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    log.info(f"简报已保存: {filepath}")

    # 更新状态
    new_seen = list(seen_ids | set(new_ids))[-5000:]
    _save_state(cfg, {"last_fetch": datetime.now().strftime("%Y/%m/%d"), "seen_ids": new_seen})
    log.info(f"完成！共 {total} 篇新文献。")

    if not no_notify:
        notify_done(total, filepath)


if __name__ == "__main__":
    main()
