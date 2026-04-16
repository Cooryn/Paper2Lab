from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ReproProject


class ReproProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, project: ReproProject) -> ReproProject:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get(self, project_id: int) -> ReproProject | None:
        stmt = (
            select(ReproProject)
            .options(selectinload(ReproProject.experiment_logs), selectinload(ReproProject.paper))
            .where(ReproProject.id == project_id)
        )
        return self.db.scalar(stmt)

    def update(self, project: ReproProject) -> ReproProject:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

