from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import ExperimentLog


class ExperimentLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, experiment_log: ExperimentLog) -> ExperimentLog:
        self.db.add(experiment_log)
        self.db.commit()
        self.db.refresh(experiment_log)
        return experiment_log

