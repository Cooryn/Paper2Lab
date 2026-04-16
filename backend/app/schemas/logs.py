from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LogAnalysisRequest(BaseModel):
    log_path: str | None = None
    sample_log_name: str | None = None


class ExperimentLogResponse(BaseModel):
    id: int
    repro_project_id: int
    log_path: str
    diagnosis_type: str
    root_cause: str
    suggestion: str
    confidence: float
    diagnosis_path: str
    diagnosis_content: str | None = None
    created_at: datetime
    updated_at: datetime
