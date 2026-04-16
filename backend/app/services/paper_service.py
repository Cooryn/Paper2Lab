from __future__ import annotations

import json
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import ImportSourceType
from app.core.exceptions import BadRequestError, NotFoundError
from app.models import Paper
from app.parsers.paper_sources import CandidatePaper, OfflineMetadataProvider
from app.parsers.pdf_parser import PaperParser
from app.repositories.paper_repository import PaperRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.paper import ManualPaperImport
from app.services.serializers import paper_to_detail, paper_to_response
from app.utils.files import ensure_dir
from app.utils.json import dumps


class PaperService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.paper_repo = PaperRepository(db)
        self.topic_repo = TopicRepository(db)
        self.parser = PaperParser()
        self.sample_provider = OfflineMetadataProvider()

    def list_papers(self, topic_id: int | None = None):
        return [paper_to_response(paper) for paper in self.paper_repo.list_all(topic_id=topic_id)]

    def get_paper_detail(self, paper_id: int):
        paper = self.paper_repo.get(paper_id)
        if not paper:
            raise NotFoundError(f"Paper {paper_id} not found.")
        return paper_to_detail(paper)

    def get_paper_model(self, paper_id: int) -> Paper:
        paper = self.paper_repo.get(paper_id)
        if not paper:
            raise NotFoundError(f"Paper {paper_id} not found.")
        return paper

    def import_manual(self, payload: ManualPaperImport):
        self._ensure_topic(payload.topic_id)
        paper = Paper(
            topic_id=payload.topic_id,
            title=payload.title,
            abstract=payload.abstract,
            authors=dumps(payload.authors),
            source_url=payload.source_url,
            priority=payload.priority,
            tags=dumps(payload.tags),
            import_source=ImportSourceType.MANUAL.value,
        )
        return paper_to_response(self._save_unique(paper))

    def import_sample(self, *, topic_id: int, sample_name: str):
        self._ensure_topic(topic_id)
        path = self.sample_provider.metadata_dir / sample_name
        if not path.exists():
            raise NotFoundError(f"Sample metadata '{sample_name}' not found.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate = CandidatePaper(
            title=payload["title"],
            authors=payload.get("authors", []),
            abstract=payload.get("abstract"),
            source_url=payload.get("source_url"),
            pdf_path=payload.get("pdf_path"),
            priority=payload.get("priority", 3),
            tags=payload.get("tags", []),
            import_source=payload.get("import_source", ImportSourceType.SAMPLE.value),
        )
        return paper_to_response(self.import_candidate(topic_id=topic_id, candidate=candidate))

    def import_url(self, *, topic_id: int, url: str):
        self._ensure_topic(topic_id)
        title = url.rstrip("/").split("/")[-1].replace("-", " ").strip() or "Imported URL Paper"
        abstract = "URL imported placeholder. Please enrich with manual abstract or PDF upload."
        if "arxiv.org" in url:
            title = f"arXiv import: {title}"
        paper = Paper(
            topic_id=topic_id,
            title=title,
            abstract=abstract,
            source_url=url,
            priority=3,
            tags=dumps(["url-import"]),
            import_source=ImportSourceType.URL.value,
        )
        return paper_to_response(self._save_unique(paper))

    def import_pdf(self, *, topic_id: int, source_path: Path):
        self._ensure_topic(topic_id)
        if source_path.suffix.lower() != ".pdf":
            raise BadRequestError("Only PDF files are supported for upload.")
        target_dir = ensure_dir(self.settings.upload_dir)
        target_path = target_dir / source_path.name
        if source_path.resolve() != target_path.resolve():
            shutil.copy2(source_path, target_path)
        parsed = self.parser.parse(target_path)
        paper = Paper(
            topic_id=topic_id,
            title=parsed["title"],
            abstract=parsed["abstract"],
            pdf_path=str(target_path.resolve()),
            priority=3,
            tags=dumps(parsed.get("sections", [])[:5]),
            import_source=ImportSourceType.PDF_UPLOAD.value,
        )
        return paper_to_response(self._save_unique(paper))

    def import_candidate(self, *, topic_id: int, candidate: CandidatePaper) -> Paper:
        self._ensure_topic(topic_id)
        pdf_path = candidate.pdf_path
        if pdf_path and not Path(pdf_path).is_absolute():
            pdf_path = str((self.settings.backend_dir.parent / pdf_path).resolve())
        paper = Paper(
            topic_id=topic_id,
            title=candidate.title,
            authors=dumps(candidate.authors),
            abstract=candidate.abstract,
            source_url=candidate.source_url,
            pdf_path=pdf_path,
            published_at=candidate.published_at,
            priority=candidate.priority,
            tags=dumps(candidate.tags),
            import_source=candidate.import_source,
        )
        return self._save_unique(paper)

    def _save_unique(self, paper: Paper) -> Paper:
        title_norm = "".join(ch.lower() for ch in paper.title if ch.isalnum())
        duplicate = self.paper_repo.find_duplicate(title_norm=title_norm, source_url=paper.source_url, pdf_path=paper.pdf_path)
        if duplicate:
            return duplicate
        return self.paper_repo.create(paper)

    def _ensure_topic(self, topic_id: int) -> None:
        if not self.topic_repo.get(topic_id):
            raise NotFoundError(f"Topic {topic_id} not found.")
