from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.labops_agent import LabOpsAgent
from app.agents.repro_agent import ReproAgent
from app.core.exceptions import NotFoundError
from app.repositories.repro_repository import ReproProjectRepository
from app.repositories.topic_repository import TopicRepository
from app.services.paper_service import PaperService
from app.services.serializers import experiment_log_to_response, repro_to_response


class ReproService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repro_agent = ReproAgent(db)
        self.labops_agent = LabOpsAgent(db)
        self.repro_repo = ReproProjectRepository(db)
        self.topic_repo = TopicRepository(db)
        self.paper_service = PaperService(db)

    def start_repro(self, paper_id: int):
        paper = self.paper_service.get_paper_model(paper_id)
        if paper.repro_projects:
            return repro_to_response(paper.repro_projects[0])
        topic = self.topic_repo.get(paper.topic_id)
        project = self.repro_agent.start_repro(paper=paper, topic_name=topic.name if topic else "unknown-topic")
        return repro_to_response(project)

    def get_project(self, project_id: int):
        project = self.repro_repo.get(project_id)
        if not project:
            raise NotFoundError(f"Repro project {project_id} not found.")
        return repro_to_response(project)

    def analyze_log(self, *, project_id: int, log_path: str):
        project = self.repro_repo.get(project_id)
        if not project:
            raise NotFoundError(f"Repro project {project_id} not found.")
        paper = self.paper_service.get_paper_model(project.paper_id)
        experiment_log = self.labops_agent.analyze_log(project=project, paper=paper, log_path=Path(log_path))
        return experiment_log_to_response(experiment_log)
