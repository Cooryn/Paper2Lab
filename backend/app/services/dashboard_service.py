from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import PaperStatus, ReproStatus
from app.models import Paper, PaperAssessment, ReproProject, Report, ResearchTopic
from app.schemas.dashboard import DashboardStats
from app.utils.time import normalize_utc, start_of_week_window


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_stats(self) -> DashboardStats:
        created_since = start_of_week_window()
        topic_count = self.db.scalar(select(func.count(ResearchTopic.id))) or 0
        new_papers_this_week = sum(
            1 for paper in self.db.scalars(select(Paper)).all() if normalize_utc(paper.created_at) >= created_since
        )
        assessed_papers = self.db.scalar(select(func.count(PaperAssessment.id))) or 0
        repro_active = self.db.scalar(select(func.count(ReproProject.id)).where(ReproProject.status == ReproStatus.ACTIVE.value)) or 0
        blocked_count = self.db.scalar(select(func.count(Paper.id)).where(Paper.status == PaperStatus.BLOCKED.value)) or 0
        reports = list(self.db.scalars(select(Report).order_by(Report.created_at.desc()).limit(5)).all())
        return DashboardStats(
            topic_count=topic_count,
            new_papers_this_week=new_papers_this_week,
            assessed_papers=assessed_papers,
            repro_active=repro_active,
            blocked_count=blocked_count,
            recent_reports=[
                {"id": report.id, "topic_id": report.topic_id, "report_path": report.report_path, "summary_text": report.summary_text}
                for report in reports
            ],
        )
