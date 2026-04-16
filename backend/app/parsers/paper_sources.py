from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import httpx

from app.core.config import get_settings


@dataclass
class CandidatePaper:
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    source_url: str | None = None
    pdf_path: str | None = None
    published_at: datetime | None = None
    priority: int = 3
    tags: list[str] = field(default_factory=list)
    import_source: str = "sample"


class PaperSourceProvider(ABC):
    @abstractmethod
    def fetch(self, topic_name: str, keywords: list[str]) -> list[CandidatePaper]:
        raise NotImplementedError


class OfflineMetadataProvider(PaperSourceProvider):
    def __init__(self, metadata_dir: Path | None = None) -> None:
        settings = get_settings()
        self.metadata_dir = metadata_dir or (settings.samples_dir / "metadata")

    def fetch(self, topic_name: str, keywords: list[str]) -> list[CandidatePaper]:
        candidates: list[CandidatePaper] = []
        terms = {topic_name.lower(), *[keyword.lower() for keyword in keywords]}
        for path in sorted(self.metadata_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            haystack = f"{payload.get('title', '')} {payload.get('abstract', '')}".lower()
            if terms and not any(term in haystack for term in terms if term):
                continue
            published_at = None
            if payload.get("published_at"):
                published_at = datetime.fromisoformat(payload["published_at"].replace("Z", "+00:00"))
            candidates.append(
                CandidatePaper(
                    title=payload["title"],
                    authors=payload.get("authors", []),
                    abstract=payload.get("abstract"),
                    source_url=payload.get("source_url"),
                    pdf_path=payload.get("pdf_path"),
                    published_at=published_at,
                    priority=payload.get("priority", 3),
                    tags=payload.get("tags", []),
                    import_source=payload.get("import_source", "sample"),
                )
            )
        return candidates


class ArxivProvider(PaperSourceProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def fetch(self, topic_name: str, keywords: list[str]) -> list[CandidatePaper]:
        query = " OR ".join([topic_name, *keywords]).strip()
        if not query:
            return []
        response = httpx.get(
            self.settings.arxiv_api_url,
            params={"search_query": f"all:{query}", "start": 0, "max_results": 5},
            timeout=20.0,
        )
        response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        candidates: list[CandidatePaper] = []
        for entry in entries:
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            summary = re.sub(r"\s+", " ", entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
            link = entry.findtext("atom:id", default=None, namespaces=ns)
            published_text = entry.findtext("atom:published", default="", namespaces=ns)
            published_at = (
                datetime.fromisoformat(published_text.replace("Z", "+00:00"))
                if published_text
                else datetime.now(timezone.utc)
            )
            authors = [author.findtext("atom:name", default="", namespaces=ns) for author in entry.findall("atom:author", ns)]
            candidates.append(
                CandidatePaper(
                    title=title,
                    authors=[author for author in authors if author],
                    abstract=summary,
                    source_url=link,
                    published_at=published_at,
                    tags=["arxiv"],
                    import_source="arxiv",
                )
            )
        return candidates

