from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import PaperStatus, ReproStatus
from app.models import ReproProject
from app.repositories.paper_repository import PaperRepository
from app.repositories.repro_repository import ReproProjectRepository
from app.services.repro_artifact_generator import ReproArtifactGenerator
from app.utils.exec_runner import ExecRunner
from app.utils.json import loads_dict


class ReproAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.paper_repo = PaperRepository(db)
        self.repro_repo = ReproProjectRepository(db)
        self.generator = ReproArtifactGenerator()
        self.exec_runner = ExecRunner()

    def start_repro(self, *, paper, topic_name: str) -> ReproProject:
        assessment = loads_dict(paper.assessment.structured_json) if paper.assessment else {}
        artifacts = self.generator.generate(paper_title=paper.title, assessment=assessment, topic_name=topic_name)
        self.exec_runner.run(
            agent_name="ReproAgent",
            command=["python", "--version"],
            cwd=self.settings.backend_dir.parent,
        )
        project = ReproProject(
            paper_id=paper.id,
            project_name=artifacts["project_name"],
            project_dir=artifacts["project_dir"],
            plan_path=artifacts["plan_path"],
            todo_path=artifacts["todo_path"],
            setup_script_path=artifacts["setup_script_path"],
            run_script_path=artifacts["run_script_path"],
            config_path=artifacts["config_path"],
            status=ReproStatus.ACTIVE.value,
        )
        paper.status = PaperStatus.REPRO_STARTED.value
        self.paper_repo.update(paper)
        return self.repro_repo.create(project)

