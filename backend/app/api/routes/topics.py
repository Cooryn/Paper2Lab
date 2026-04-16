from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import ReportResponse
from app.schemas.topic import TopicCreate, TopicDetailResponse, TopicResponse
from app.services.report_service import ReportService
from app.services.topic_service import TopicService


router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("", response_model=TopicResponse)
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)) -> TopicResponse:
    return TopicService(db).create_topic(payload)


@router.get("", response_model=list[TopicResponse])
def list_topics(db: Session = Depends(get_db)) -> list[TopicResponse]:
    return TopicService(db).list_topics()


@router.get("/{topic_id}", response_model=TopicDetailResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)) -> TopicDetailResponse:
    return TopicService(db).get_topic_detail(topic_id)


@router.post("/{topic_id}/generate-weekly-report", response_model=ReportResponse)
def generate_weekly_report(topic_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    return ReportService(db).generate_weekly_report(topic_id)

