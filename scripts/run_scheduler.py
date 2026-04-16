from __future__ import annotations

import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.task_service import TaskService
from app.tasks.scheduler_adapter import LocalSchedulerAdapter


def run_topic_scan_all() -> None:
    db = SessionLocal()
    try:
        task_service = TaskService(db)
        topic_ids = [topic.id for topic in task_service.topic_repo.list_all()]
        for topic_id in topic_ids:
            task_service.run_topic_scan(topic_id)
    finally:
        db.close()


def run_nightly_summary() -> None:
    db = SessionLocal()
    try:
        TaskService(db).run_nightly_summary()
    finally:
        db.close()


def run_weekly_reports() -> None:
    db = SessionLocal()
    try:
        task_service = TaskService(db)
        topic_ids = [topic.id for topic in task_service.topic_repo.list_all()]
        for topic_id in topic_ids:
            task_service.run_weekly_report(topic_id)
    finally:
        db.close()


def main() -> None:
    settings = get_settings()
    if not settings.scheduler_enabled:
        print("Scheduler disabled by configuration.")
        return
    scheduler = LocalSchedulerAdapter()
    scheduler.add_jobs(run_topic_scan_all, run_nightly_summary, run_weekly_reports)
    scheduler.start()
    print("Paper2Lab local scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()

