from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ReproProject(TimestampMixin, Base):
    __tablename__ = "repro_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_dir: Mapped[str] = mapped_column(String(1000), nullable=False)
    plan_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    todo_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    setup_script_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    run_script_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    config_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ready")

    paper = relationship("Paper", back_populates="repro_projects")
    experiment_logs = relationship(
        "ExperimentLog", back_populates="repro_project", cascade="all, delete-orphan"
    )

