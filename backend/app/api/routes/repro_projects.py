from __future__ import annotations

import shutil

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import BadRequestError
from app.schemas.logs import ExperimentLogResponse
from app.schemas.repro import ReproProjectResponse
from app.services.repro_service import ReproService


router = APIRouter(prefix="/repro-projects", tags=["repro-projects"])


def _is_upload_file(value: object) -> bool:
    return hasattr(value, "filename") and hasattr(value, "file")


@router.get("/{project_id}", response_model=ReproProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ReproProjectResponse:
    return ReproService(db).get_project(project_id)


@router.post("/{project_id}/analyze-log", response_model=ExperimentLogResponse)
async def analyze_log(project_id: int, request: Request, db: Session = Depends(get_db)) -> ExperimentLogResponse:
    service = ReproService(db)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        if body.get("sample_log_name"):
            path = get_settings().samples_dir / "logs" / body["sample_log_name"]
            return service.analyze_log(project_id=project_id, log_path=str(path.resolve()))
        if body.get("log_path"):
            return service.analyze_log(project_id=project_id, log_path=body["log_path"])
        raise BadRequestError("JSON payload must include sample_log_name or log_path.")

    form = await request.form()
    upload = form.get("file")
    if _is_upload_file(upload):
        temp_path = get_settings().upload_dir / str(upload.filename)
        with temp_path.open("wb") as handle:
            shutil.copyfileobj(upload.file, handle)
        return service.analyze_log(project_id=project_id, log_path=str(temp_path.resolve()))
    if form.get("sample_log_name"):
        path = get_settings().samples_dir / "logs" / str(form["sample_log_name"])
        return service.analyze_log(project_id=project_id, log_path=str(path.resolve()))
    raise BadRequestError("Log analysis requires either a file or sample_log_name.")
