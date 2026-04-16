from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Paper(TimestampMixin, Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("research_topics.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    authors: Mapped[str] = mapped_column(Text, default="[]")
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    tags: Mapped[str] = mapped_column(Text, default="[]")
    import_source: Mapped[str] = mapped_column(String(50), default="manual")

    topic = relationship("ResearchTopic", back_populates="papers")
    assessment = relationship(
        "PaperAssessment", back_populates="paper", uselist=False, cascade="all, delete-orphan"
    )
    repro_projects = relationship("ReproProject", back_populates="paper", cascade="all, delete-orphan")

