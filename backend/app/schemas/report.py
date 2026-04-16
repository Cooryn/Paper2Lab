from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: int
    topic_id: int
    report_type: str
    report_path: str
    summary_text: str
    content: str | None = None
    created_at: datetime
    updated_at: datetime
