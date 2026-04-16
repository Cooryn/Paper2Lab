from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportResponse])
def list_reports(topic_id: int | None = None, db: Session = Depends(get_db)) -> list[ReportResponse]:
    return ReportService(db).list_reports(topic_id=topic_id)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    return ReportService(db).get_report(report_id)

