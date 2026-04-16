from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.labops_agent import LabOpsAgent
from app.core.exceptions import NotFoundError
from app.repositories.report_repository import ReportRepository
from app.repositories.topic_repository import TopicRepository
from app.services.serializers import report_to_response


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.agent = LabOpsAgent(db)
        self.topic_repo = TopicRepository(db)
        self.report_repo = ReportRepository(db)

    def generate_weekly_report(self, topic_id: int):
        topic = self.topic_repo.get(topic_id)
        if not topic:
            raise NotFoundError(f"Topic {topic_id} not found.")
        report = self.agent.generate_weekly_report(topic=topic)
        return report_to_response(report)

    def get_report(self, report_id: int):
        report = self.report_repo.get(report_id)
        if not report:
            raise NotFoundError(f"Report {report_id} not found.")
        return report_to_response(report)

    def list_reports(self, topic_id: int | None = None):
        return [report_to_response(report) for report in self.report_repo.list_all(topic_id=topic_id)]

