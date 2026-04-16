from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import ResearchTopic
from app.repositories.topic_repository import TopicRepository
from app.schemas.topic import TopicCreate
from app.services.serializers import topic_to_detail, topic_to_response
from app.utils.json import dumps


class TopicService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.topic_repo = TopicRepository(db)

    def create_topic(self, payload: TopicCreate):
        topic = ResearchTopic(name=payload.name, description=payload.description, keywords=dumps(payload.keywords))
        return topic_to_response(self.topic_repo.create(topic))

    def list_topics(self):
        return [topic_to_response(topic) for topic in self.topic_repo.list_all()]

    def get_topic_detail(self, topic_id: int):
        topic, paper_count, report_count = self.topic_repo.get_with_counts(topic_id)
        if not topic:
            raise NotFoundError(f"Topic {topic_id} not found.")
        return topic_to_detail(topic, paper_count=paper_count, report_count=report_count)

    def get_topic_model(self, topic_id: int):
        topic = self.topic_repo.get(topic_id)
        if not topic:
            raise NotFoundError(f"Topic {topic_id} not found.")
        return topic

