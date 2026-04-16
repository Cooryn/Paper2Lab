from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Report


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get(self, report_id: int) -> Report | None:
        return self.db.get(Report, report_id)

    def list_all(self, topic_id: int | None = None) -> list[Report]:
        stmt = select(Report).order_by(Report.created_at.desc())
        if topic_id is not None:
            stmt = stmt.where(Report.topic_id == topic_id)
        return list(self.db.scalars(stmt).all())

    def count_for_topic(self, topic_id: int) -> int:
        return self.db.scalar(select(func.count(Report.id)).where(Report.topic_id == topic_id)) or 0

