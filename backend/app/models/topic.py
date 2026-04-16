from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ResearchTopic(TimestampMixin, Base):
    __tablename__ = "research_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str] = mapped_column(Text, default="[]")

    papers = relationship("Paper", back_populates="topic", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="topic", cascade="all, delete-orphan")

