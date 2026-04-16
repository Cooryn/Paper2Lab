from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.reader_agent import ReaderAgent
from app.repositories.topic_repository import TopicRepository
from app.services.paper_service import PaperService
from app.services.serializers import assessment_to_response


class AssessmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.reader_agent = ReaderAgent(db)
        self.paper_service = PaperService(db)
        self.topic_repo = TopicRepository(db)

    def assess_paper(self, *, paper_id: int, use_llm: bool, notes: str | None):
        paper = self.paper_service.get_paper_model(paper_id)
        topic = self.topic_repo.get(paper.topic_id)
        assessment = self.reader_agent.assess(
            paper=paper,
            topic_name=topic.name if topic else "unknown-topic",
            use_llm=use_llm,
            notes=notes,
        )
        return assessment_to_response(assessment)

