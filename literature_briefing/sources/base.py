"""文献源抽象基类 + Paper 数据类"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List


@dataclass
class Paper:
    source: str  # "pubmed" / "arxiv"
    source_id: str  # PMID / arXiv ID
    title: str
    abstract: str
    authors: List[str] = field(default_factory=list)
    journal: str = ""
    journal_abbr: str = ""
    date: str = ""
    doi: str = ""
    url: str = ""
    categories: List[str] = field(default_factory=list)
    # 翻译后填充
    title_zh: str = ""
    abstract_zh: str = ""


class LiteratureSource(ABC):
    @abstractmethod
    def search(self, date_from: str, date_to: str, max_results: int,
               seen_ids: set) -> List[Paper]:
        """搜索并返回去重后的论文列表"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
