from __future__ import annotations

import json
import shutil

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import BadRequestError
from app.schemas.assessment import AssessmentRequest, AssessmentResponse
from app.schemas.paper import ManualPaperImport, PaperDetailResponse, PaperResponse
from app.schemas.repro import ReproProjectResponse
from app.services.assessment_service import AssessmentService
from app.services.paper_service import PaperService
from app.services.repro_service import ReproService


router = APIRouter(prefix="/papers", tags=["papers"])


def _is_upload_file(value: object) -> bool:
    return hasattr(value, "filename") and hasattr(value, "file")


@router.post("/import", response_model=PaperResponse)
async def import_paper(request: Request, db: Session = Depends(get_db)) -> PaperResponse:
    service = PaperService(db)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        mode = body.get("import_mode", "manual")
        if mode == "manual":
            return service.import_manual(ManualPaperImport(**body))
        if mode == "sample":
            return service.import_sample(topic_id=int(body["topic_id"]), sample_name=body["sample_name"])
        if mode == "url":
            return service.import_url(topic_id=int(body["topic_id"]), url=body["url"])
        raise BadRequestError(f"Unsupported import mode: {mode}")

    form = await request.form()
    mode = str(form.get("import_mode", "manual"))
    if mode == "pdf":
        upload = form.get("file")
        if not _is_upload_file(upload):
            raise BadRequestError("PDF import requires a file upload.")
        settings = get_settings()
        temp_path = settings.upload_dir / str(upload.filename)
        with temp_path.open("wb") as handle:
            shutil.copyfileobj(upload.file, handle)
        return service.import_pdf(topic_id=int(form["topic_id"]), source_path=temp_path)

    if mode == "manual":
        authors = json.loads(str(form.get("authors", "[]")))
        tags = json.loads(str(form.get("tags", "[]")))
        payload = ManualPaperImport(
            topic_id=int(form["topic_id"]),
            title=str(form["title"]),
            abstract=str(form.get("abstract") or ""),
            authors=authors,
            source_url=str(form.get("source_url") or "") or None,
            priority=int(form.get("priority", 3)),
            tags=tags,
        )
        return service.import_manual(payload)

    if mode == "sample":
        return service.import_sample(topic_id=int(form["topic_id"]), sample_name=str(form["sample_name"]))

    if mode == "url":
        return service.import_url(topic_id=int(form["topic_id"]), url=str(form["url"]))

    raise BadRequestError(f"Unsupported form import mode: {mode}")


@router.get("", response_model=list[PaperResponse])
def list_papers(topic_id: int | None = None, db: Session = Depends(get_db)) -> list[PaperResponse]:
    return PaperService(db).list_papers(topic_id=topic_id)


@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(paper_id: int, db: Session = Depends(get_db)) -> PaperDetailResponse:
    return PaperService(db).get_paper_detail(paper_id)


@router.post("/{paper_id}/assess", response_model=AssessmentResponse)
def assess_paper(
    paper_id: int,
    payload: AssessmentRequest,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    return AssessmentService(db).assess_paper(paper_id=paper_id, use_llm=payload.use_llm, notes=payload.notes)


@router.post("/{paper_id}/start-repro", response_model=ReproProjectResponse)
def start_repro(paper_id: int, db: Session = Depends(get_db)) -> ReproProjectResponse:
    return ReproService(db).start_repro(paper_id)
