from __future__ import annotations

from enum import Enum


class PaperStatus(str, Enum):
    NEW = "new"
    SCREENED = "screened"
    ASSESSED = "assessed"
    REPRO_STARTED = "repro_started"
    BLOCKED = "blocked"
    DONE = "done"


class DifficultyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationType(str, Enum):
    QUICK_BASELINE = "quick_baseline"
    FULL_REPRO = "full_repro"
    HOLD = "hold"


class DiagnosisType(str, Enum):
    MISSING_DEPENDENCY = "missing_dependency"
    CUDA_OOM = "cuda_oom"
    PATH_NOT_FOUND = "path_not_found"
    DATA_FORMAT_ERROR = "data_format_error"
    CHECKPOINT_LOAD_FAILED = "checkpoint_load_failed"
    CONFIG_MISSING = "config_missing"
    NAN_OR_GRADIENT = "nan_or_gradient"
    UNKNOWN = "unknown"


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class ImportSourceType(str, Enum):
    PDF_UPLOAD = "pdf_upload"
    SAMPLE = "sample"
    MANUAL = "manual"
    URL = "url"
    ARXIV = "arxiv"


class ReproStatus(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    BLOCKED = "blocked"
    DONE = "done"

