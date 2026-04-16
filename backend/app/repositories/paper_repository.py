from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Paper


class PaperRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, paper: Paper) -> Paper:
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper

    def update(self, paper: Paper) -> Paper:
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper

    def list_all(self, topic_id: int | None = None) -> list[Paper]:
        stmt = select(Paper).options(selectinload(Paper.assessment), selectinload(Paper.repro_projects))
        if topic_id is not None:
            stmt = stmt.where(Paper.topic_id == topic_id)
        stmt = stmt.order_by(Paper.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get(self, paper_id: int) -> Paper | None:
        stmt = (
            select(Paper)
            .options(selectinload(Paper.assessment), selectinload(Paper.repro_projects))
            .where(Paper.id == paper_id)
        )
        return self.db.scalar(stmt)

    def find_duplicate(self, *, title_norm: str, source_url: str | None, pdf_path: str | None) -> Paper | None:
        candidates = self.list_all()
        for paper in candidates:
            existing_norm = "".join(ch.lower() for ch in paper.title if ch.isalnum())
            if existing_norm == title_norm:
                return paper
            if source_url and paper.source_url and paper.source_url == source_url:
                return paper
            if pdf_path and paper.pdf_path and paper.pdf_path == pdf_path:
                return paper
        return None

    def weekly_new_count(self, created_since) -> int:
        return self.db.scalar(select(func.count(Paper.id)).where(Paper.created_at >= created_since)) or 0

