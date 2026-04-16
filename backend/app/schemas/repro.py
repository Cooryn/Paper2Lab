from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReproProjectResponse(BaseModel):
    id: int
    paper_id: int
    project_name: str
    project_dir: str
    plan_path: str
    todo_path: str
    setup_script_path: str
    run_script_path: str
    config_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    generated_files: dict[str, str] | None = None
    generated_contents: dict[str, str] | None = None
    experiment_logs: list[dict] | None = None
