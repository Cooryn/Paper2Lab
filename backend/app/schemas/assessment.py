from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssessmentRequest(BaseModel):
    use_llm: bool = True
    notes: str | None = None


class AssessmentResponse(BaseModel):
    id: int
    paper_id: int
    novelty_summary: str
    task_definition: str
    method_summary: str
    datasets: list[str]
    metrics: list[str]
    dependencies: list[str]
    difficulty: str
    recommendation: str
    risks: list[str]
    applicable_scenarios: list[str]
    structured_json: dict
    markdown_path: str
    json_path: str
    markdown_content: str | None = None
    created_at: datetime
    updated_at: datetime


class AssessmentPayload(BaseModel):
    title: str
    task_definition: str
    novelty_summary: str
    method_summary: str
    datasets: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    difficulty: str
    recommendation: str
    risks: list[str] = Field(default_factory=list)
    applicable_scenarios: list[str] = Field(default_factory=list)
