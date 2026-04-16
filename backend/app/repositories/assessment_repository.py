from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import PaperAssessment


class AssessmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, assessment: PaperAssessment) -> PaperAssessment:
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

