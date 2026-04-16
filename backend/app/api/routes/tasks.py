from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/run-topic-scan/{topic_id}")
def run_topic_scan(topic_id: int, db: Session = Depends(get_db)) -> dict:
    return TaskService(db).run_topic_scan(topic_id)


@router.post("/run-nightly-summary")
def run_nightly_summary(db: Session = Depends(get_db)) -> dict:
    return TaskService(db).run_nightly_summary()


@router.post("/run-weekly-report/{topic_id}")
def run_weekly_report(topic_id: int, db: Session = Depends(get_db)) -> dict:
    return TaskService(db).run_weekly_report(topic_id)

