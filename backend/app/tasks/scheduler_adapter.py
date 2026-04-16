from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings


class SchedulerAdapter:
    def start(self) -> None:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError


class LocalSchedulerAdapter(SchedulerAdapter):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.scheduler = BackgroundScheduler(timezone=self.settings.default_timezone)

    def add_jobs(self, run_topic_scan, run_nightly_summary, run_weekly_report) -> None:
        self.scheduler.add_job(run_topic_scan, "cron", hour=9, minute=0, id="daily_topic_scan", replace_existing=True)
        self.scheduler.add_job(run_nightly_summary, "cron", hour=22, minute=30, id="nightly_summary", replace_existing=True)
        self.scheduler.add_job(run_weekly_report, "cron", day_of_week="fri", hour=18, minute=0, id="weekly_report", replace_existing=True)

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

