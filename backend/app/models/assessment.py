from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class PaperAssessment(TimestampMixin, Base):
    __tablename__ = "paper_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), unique=True, index=True)
    novelty_summary: Mapped[str] = mapped_column(Text, default="")
    task_definition: Mapped[str] = mapped_column(Text, default="")
    method_summary: Mapped[str] = mapped_column(Text, default="")
    datasets: Mapped[str] = mapped_column(Text, default="[]")
    metrics: Mapped[str] = mapped_column(Text, default="[]")
    dependencies: Mapped[str] = mapped_column(Text, default="[]")
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")
    recommendation: Mapped[str] = mapped_column(String(50), default="quick_baseline")
    risks: Mapped[str] = mapped_column(Text, default="[]")
    applicable_scenarios: Mapped[str] = mapped_column(Text, default="[]")
    structured_json: Mapped[str] = mapped_column(Text, default="{}")
    markdown_path: Mapped[str] = mapped_column(String(1000), default="")
    json_path: Mapped[str] = mapped_column(String(1000), default="")

    paper = relationship("Paper", back_populates="assessment")

