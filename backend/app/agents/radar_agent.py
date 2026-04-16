from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.parsers.paper_sources import ArxivProvider, OfflineMetadataProvider
from app.repositories.topic_repository import TopicRepository
from app.services.paper_service import PaperService
from app.utils.json import loads_list


class RadarAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.paper_service = PaperService(db)
        self.topic_repo = TopicRepository(db)
        self.offline_provider = OfflineMetadataProvider()
        self.online_provider = ArxivProvider()

    def scan_topic(self, topic_id: int) -> list[int]:
        topic = self.topic_repo.get(topic_id)
        if not topic:
            return []
        keywords = loads_list(topic.keywords)
        candidates = self.offline_provider.fetch(topic.name, keywords)
        if self.settings.enable_online_sources:
            try:
                candidates.extend(self.online_provider.fetch(topic.name, keywords))
            except Exception:
                pass
        paper_ids: list[int] = []
        for candidate in candidates:
            paper = self.paper_service.import_candidate(topic_id=topic.id, candidate=candidate)
            paper_ids.append(paper.id)
        return paper_ids

