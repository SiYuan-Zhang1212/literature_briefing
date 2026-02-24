"""PubMed 文献源"""

import time
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List
from .base import Paper, LiteratureSource

log = logging.getLogger(__name__)
PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedSource(LiteratureSource):
    def __init__(self, cfg_pubmed: dict):
        self.api_key = cfg_pubmed.get("api_key", "")
        self.core_journals = cfg_pubmed.get("core_journals", [])
        self.extended_journals = cfg_pubmed.get("extended_journals", [])
        self.keywords = cfg_pubmed.get("keywords", [])
        self.species_filter = cfg_pubmed.get("species_filter", [])

    @property
    def name(self) -> str:
        return "pubmed"

    def search(self, date_from: str, date_to: str, max_results: int,
               seen_ids: set) -> List[Paper]:
        core_papers = []
        kw_papers = []

        # 核心期刊搜索
        if self.core_journals:
            log.info("检索核心期刊...")
            core_query = self._build_core_query(date_from, date_to)
            core_pmids = self._esearch(core_query, max_results)
            core_pmids = [p for p in core_pmids if p not in seen_ids]
            log.info(f"  核心期刊新文献: {len(core_pmids)} 篇")
            time.sleep(0.15)
            core_papers = self._efetch(core_pmids)

        # 关键词扩展搜索
        if self.keywords and self.extended_journals:
            log.info("检索关键词扩展期刊...")
            kw_query = self._build_keyword_query(date_from, date_to)
            kw_pmids = self._esearch(kw_query, max_results)
            core_ids = {p.source_id for p in core_papers}
            kw_pmids = [p for p in kw_pmids if p not in seen_ids and p not in core_ids]
            log.info(f"  扩展期刊新文献: {len(kw_pmids)} 篇")
            kw_papers = self._efetch(kw_pmids)

        # 标记搜索类型
        for p in core_papers:
            p.categories = ["core"]
        for p in kw_papers:
            p.categories = ["extended"]

        return core_papers + kw_papers

    # --- PubMed API ---

    def _params(self, extra=None):
        params = {"db": "pubmed", "retmode": "json"}
        if self.api_key:
            params["api_key"] = self.api_key
        if extra:
            params.update(extra)
        return params

    def _esearch(self, query: str, retmax: int) -> List[str]:
        resp = requests.get(
            f"{PUBMED_BASE}/esearch.fcgi",
            params=self._params({"term": query, "retmax": retmax, "sort": "pub_date"}),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("esearchresult", {}).get("idlist", [])

    def _efetch(self, pmids: List[str]) -> List[Paper]:
        if not pmids:
            return []
        papers = []
        for i in range(0, len(pmids), 50):
            batch = pmids[i:i + 50]
            params = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
            if self.api_key:
                params["api_key"] = self.api_key
            resp = requests.get(f"{PUBMED_BASE}/efetch.fcgi", params=params, timeout=60)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            for article in root.findall(".//PubmedArticle"):
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)
            time.sleep(0.15)
        return papers

    def _parse_article(self, article) -> Paper | None:
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
                y = pub_date.findtext("Year", "")
                m = pub_date.findtext("Month", "")
                d = pub_date.findtext("Day", "")
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

            url = f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return Paper(
                source="pubmed", source_id=pmid, title=title, abstract=abstract,
                authors=authors, journal=journal, journal_abbr=journal_abbr,
                date=date_str, doi=doi, url=url,
            )
        except Exception as e:
            log.warning(f"解析文献失败: {e}")
            return None

    # --- 查询构建 ---

    def _build_core_query(self, date_from, date_to):
        journals = " OR ".join(f'"{j}"[Journal]' for j in self.core_journals)
        return f'({journals}) AND ("{date_from}"[PDAT] : "{date_to}"[PDAT])'

    def _build_keyword_query(self, date_from, date_to):
        journals = " OR ".join(f'"{j}"[Journal]' for j in self.extended_journals)
        keywords = " OR ".join(f'"{k}"[Title/Abstract]' for k in self.keywords)
        query = f'({keywords}) AND ({journals}) AND ("{date_from}"[PDAT] : "{date_to}"[PDAT])'
        if self.species_filter:
            species = " OR ".join(self.species_filter)
            query += f" AND ({species})"
        return query
