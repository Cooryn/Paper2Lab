from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ExperimentLog(TimestampMixin, Base):
    __tablename__ = "experiment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repro_project_id: Mapped[int] = mapped_column(ForeignKey("repro_projects.id"), index=True)
    log_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    diagnosis_type: Mapped[str] = mapped_column(String(50), default="unknown")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    suggestion: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(default=0.0)
    diagnosis_path: Mapped[str] = mapped_column(String(1000), default="")

    repro_project = relationship("ReproProject", back_populates="experiment_logs")

