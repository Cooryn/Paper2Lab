from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    keywords: list[str] = Field(default_factory=list)


class TopicResponse(BaseModel):
    id: int
    name: str
    description: str | None
    keywords: list[str]
    created_at: datetime
    updated_at: datetime


class TopicDetailResponse(TopicResponse):
    paper_count: int = 0
    report_count: int = 0

