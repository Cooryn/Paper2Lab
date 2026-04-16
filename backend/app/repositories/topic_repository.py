from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Report, ResearchTopic


class TopicRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, topic: ResearchTopic) -> ResearchTopic:
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def list_all(self) -> list[ResearchTopic]:
        return list(self.db.scalars(select(ResearchTopic).order_by(ResearchTopic.created_at.desc())).all())

    def get(self, topic_id: int) -> ResearchTopic | None:
        return self.db.get(ResearchTopic, topic_id)

    def get_with_counts(self, topic_id: int) -> tuple[ResearchTopic | None, int, int]:
        topic = self.get(topic_id)
        if not topic:
            return None, 0, 0
        paper_count = len(topic.papers)
        report_count = self.db.scalar(
            select(func.count(Report.id)).where(Report.topic_id == topic_id)
        ) or 0
        return topic, paper_count, report_count

