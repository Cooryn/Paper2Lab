from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import PaperStatus, ReportType, ReproStatus
from app.diagnostics.rules import LogDiagnosisEngine
from app.models import ExperimentLog, Report
from app.repositories.experiment_log_repository import ExperimentLogRepository
from app.repositories.paper_repository import PaperRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.repro_repository import ReproProjectRepository
from app.utils.files import read_text
from app.utils.markdown import write_markdown
from app.utils.notifications import ConsoleNotifier, MarkdownNotifier, NotificationMessage
from app.utils.slug import slugify
from app.utils.time import normalize_utc, start_of_week_window


class LabOpsAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.paper_repo = PaperRepository(db)
        self.report_repo = ReportRepository(db)
        self.repro_repo = ReproProjectRepository(db)
        self.log_repo = ExperimentLogRepository(db)
        self.engine = LogDiagnosisEngine()
        self.console_notifier = ConsoleNotifier()
        self.markdown_notifier = MarkdownNotifier(Path("backend/generated/notifications"))

    def analyze_log(self, *, project, paper, log_path: Path) -> ExperimentLog:
        matches = self.engine.diagnose(read_text(log_path))
        top = matches[0]
        diagnosis_path = Path(project.project_dir) / "diagnosis.md"
        write_markdown(
            diagnosis_path,
            f"""
# Experiment Log Diagnosis

## Diagnosis Type
{top.diagnosis_type.value}

## Root Cause
{top.root_cause}

## Suggestion
{top.suggestion}

## Confidence
{top.confidence}
""",
        )
        if top.confidence >= 0.89:
            project.status = ReproStatus.BLOCKED.value
            paper.status = PaperStatus.BLOCKED.value
            self.paper_repo.update(paper)
        self.repro_repo.update(project)
        experiment_log = ExperimentLog(
            repro_project_id=project.id,
            log_path=str(log_path.resolve()),
            diagnosis_type=top.diagnosis_type.value,
            root_cause=top.root_cause,
            suggestion=top.suggestion,
            confidence=top.confidence,
            diagnosis_path=str(diagnosis_path.resolve()),
        )
        return self.log_repo.create(experiment_log)

    def generate_weekly_report(self, *, topic) -> Report:
        cutoff = start_of_week_window()
        papers = [paper for paper in topic.papers if normalize_utc(paper.created_at) >= cutoff]
        assessed = [paper for paper in papers if paper.assessment is not None]
        repro_started = [paper for paper in papers if paper.status == PaperStatus.REPRO_STARTED.value]
        blocked = [paper for paper in papers if paper.status == PaperStatus.BLOCKED.value]
        week_str = datetime.now().strftime("%Y-W%W")
        report_slug = slugify(topic.name)
        report_path = Path("backend/generated/reports") / report_slug / f"weekly-{week_str}.md"
        summary_text = (
            f"[{topic.name}] 本周新增 {len(papers)} 篇候选论文，"
            f"已评估 {len(assessed)} 篇，已启动复现 {len(repro_started)} 篇，"
            f"阻塞 {len(blocked)} 项。建议优先处理最高优先级论文与阻塞日志。"
        )
        write_markdown(
            report_path,
            f"""
# Weekly Report

## 本周新增论文
{chr(10).join(f"- {paper.title}" for paper in papers) or "- 无"}

## 已完成评估
{chr(10).join(f"- {paper.title}" for paper in assessed) or "- 无"}

## 已启动复现
{chr(10).join(f"- {paper.title}" for paper in repro_started) or "- 无"}

## 当前阻塞项
{chr(10).join(f"- {paper.title}" for paper in blocked) or "- 无"}

## 下步建议
- 优先处理最高优先级论文的 baseline 跑通。
- 对阻塞日志补充数据、依赖和 checkpoint 检查。
- 把已评估论文按复现价值分成“快速 baseline”和“完整复现”两队列。
""",
        )
        self.console_notifier.notify(NotificationMessage(title=f"Weekly Report {topic.name}", body=summary_text))
        self.markdown_notifier.notify(NotificationMessage(title=f"weekly_{topic.name}", body=summary_text))
        report = Report(
            topic_id=topic.id,
            report_type=ReportType.WEEKLY.value,
            report_path=str(report_path.resolve()),
            summary_text=summary_text,
        )
        return self.report_repo.create(report)

    def nightly_summary(self) -> dict:
        blocked = list(self.db.scalars(select(ExperimentLog).order_by(ExperimentLog.created_at.desc()).limit(5)).all())
        return {"recent_log_issues": [log.root_cause for log in blocked]}
