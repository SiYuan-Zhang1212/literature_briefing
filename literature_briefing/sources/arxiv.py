"""arXiv 文献源"""

import time
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List
from .base import Paper, LiteratureSource

log = logging.getLogger(__name__)
ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivSource(LiteratureSource):
    def __init__(self, cfg_arxiv: dict):
        self.categories = cfg_arxiv.get("categories", [])
        self.keywords = cfg_arxiv.get("keywords", [])

    @property
    def name(self) -> str:
        return "arxiv"

    def search(self, date_from: str, date_to: str, max_results: int,
               seen_ids: set) -> List[Paper]:
        query = self._build_query()
        if not query:
            return []

        log.info("检索 arXiv...")
        papers = []
        start = 0
        batch_size = min(max_results, 100)

        while start < max_results:
            resp = requests.get(
                ARXIV_API,
                params={
                    "search_query": query,
                    "start": start,
                    "max_results": batch_size,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
                timeout=30,
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            entries = root.findall("atom:entry", NS)
            if not entries:
                break

            for entry in entries:
                paper = self._parse_entry(entry)
                if paper and paper.source_id not in seen_ids:
                    # 按日期过滤
                    if self._in_date_range(paper.date, date_from, date_to):
                        papers.append(paper)

            start += batch_size
            if len(entries) < batch_size:
                break
            time.sleep(0.5)

        log.info(f"  arXiv 新文献: {len(papers)} 篇")
        return papers

    def _build_query(self) -> str:
        parts = []
        if self.categories:
            cat_q = " OR ".join(f"cat:{c}" for c in self.categories)
            parts.append(f"({cat_q})")
        if self.keywords:
            kw_q = " OR ".join(f'all:"{k}"' for k in self.keywords)
            parts.append(f"({kw_q})")
        if not parts:
            return ""
        return " AND ".join(parts) if len(parts) > 1 else parts[0]

    def _parse_entry(self, entry) -> Paper | None:
        try:
            arxiv_id = entry.findtext("atom:id", "", NS).split("/abs/")[-1]
            title = entry.findtext("atom:title", "", NS).replace("\n", " ").strip()
            abstract = entry.findtext("atom:summary", "", NS).strip()

            authors = []
            for author in entry.findall("atom:author", NS):
                name = author.findtext("atom:name", "", NS)
                if name:
                    authors.append(name)

            published = entry.findtext("atom:published", "", NS)[:10]  # YYYY-MM-DD

            categories = []
            for cat in entry.findall("atom:category", NS):
                term = cat.get("term", "")
                if term:
                    categories.append(term)

            doi = ""
            for link in entry.findall("atom:link", NS):
                if link.get("title") == "doi":
                    doi = link.get("href", "").replace("http://dx.doi.org/", "")

            url = f"https://arxiv.org/abs/{arxiv_id}"

            return Paper(
                source="arxiv", source_id=arxiv_id, title=title, abstract=abstract,
                authors=authors, journal="arXiv", journal_abbr="arXiv",
                date=published, doi=doi, url=url, categories=categories,
            )
        except Exception as e:
            log.warning(f"解析 arXiv 条目失败: {e}")
            return None

    @staticmethod
    def _in_date_range(date_str: str, date_from: str, date_to: str) -> bool:
        """简单日期范围检查，date_str 为 YYYY-MM-DD，date_from/to 为 YYYY/MM/DD"""
        try:
            d = date_str.replace("-", "")
            f = date_from.replace("/", "")
            t = date_to.replace("/", "")
            return f <= d <= t
        except Exception:
            return True  # 解析失败则保留
