from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("research_topics.id"), index=True)
    report_type: Mapped[str] = mapped_column(String(50), default="weekly", index=True)
    report_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, default="")

    topic = relationship("ResearchTopic", back_populates="reports")

