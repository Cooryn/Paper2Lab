from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ManualPaperImport(BaseModel):
    topic_id: int
    title: str = Field(min_length=3)
    abstract: str | None = None
    authors: list[str] = Field(default_factory=list)
    source_url: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)


class SamplePaperImport(BaseModel):
    topic_id: int
    sample_name: str


class UrlPaperImport(BaseModel):
    topic_id: int
    url: str


class PaperImportResponse(BaseModel):
    id: int
    title: str
    status: str
    import_source: str


class PaperResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    authors: list[str]
    abstract: str | None
    source_url: str | None
    pdf_path: str | None
    published_at: datetime | None
    status: str
    priority: int
    tags: list[str]
    import_source: str
    created_at: datetime
    updated_at: datetime


class PaperDetailResponse(PaperResponse):
    assessment_id: int | None = None
    repro_project_ids: list[int] = Field(default_factory=list)
    assessment: dict | None = None
    repro_projects: list[dict] = Field(default_factory=list)
