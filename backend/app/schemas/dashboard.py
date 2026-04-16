from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    topic_count: int
    new_papers_this_week: int
    assessed_papers: int
    repro_active: int
    blocked_count: int
    recent_reports: list[dict]

