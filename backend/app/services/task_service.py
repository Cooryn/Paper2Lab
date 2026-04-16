from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.labops_agent import LabOpsAgent
from app.agents.radar_agent import RadarAgent
from app.repositories.topic_repository import TopicRepository
from app.services.report_service import ReportService


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.radar_agent = RadarAgent(db)
        self.labops_agent = LabOpsAgent(db)
        self.topic_repo = TopicRepository(db)
        self.report_service = ReportService(db)

    def run_topic_scan(self, topic_id: int) -> dict:
        paper_ids = self.radar_agent.scan_topic(topic_id)
        return {"topic_id": topic_id, "paper_ids": paper_ids, "count": len(paper_ids)}

    def run_nightly_summary(self) -> dict:
        return self.labops_agent.nightly_summary()

    def run_weekly_report(self, topic_id: int) -> dict:
        report = self.report_service.generate_weekly_report(topic_id)
        return report.model_dump()

