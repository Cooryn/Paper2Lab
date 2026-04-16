from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.enums import PaperStatus
from app.models import PaperAssessment
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.paper_repository import PaperRepository
from app.schemas.assessment import AssessmentPayload
from app.services.assessment_engine import AssessmentEngine
from app.utils.files import write_text
from app.utils.json import dumps
from app.utils.markdown import write_markdown
from app.utils.slug import slugify


class ReaderAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.paper_repo = PaperRepository(db)
        self.assessment_repo = AssessmentRepository(db)
        self.engine = AssessmentEngine()

    def assess(self, *, paper, topic_name: str, use_llm: bool, notes: str | None) -> PaperAssessment:
        raw_text = paper.abstract or paper.title
        if paper.pdf_path and Path(paper.pdf_path).exists():
            from app.parsers.pdf_parser import PaperParser

            parsed = PaperParser().parse(Path(paper.pdf_path))
            raw_text = parsed.get("raw_text", raw_text)
            if not paper.abstract:
                paper.abstract = parsed.get("abstract")
        payload: AssessmentPayload = self.engine.run(
            title=paper.title,
            abstract=paper.abstract or "",
            raw_text=raw_text,
            use_llm=use_llm,
            notes=notes,
        )
        topic_slug = slugify(topic_name)
        paper_slug = slugify(paper.title)
        root = Path("backend/generated/topics") / topic_slug / "papers" / paper_slug
        json_path = root / "assessment.json"
        markdown_path = root / "assessment.md"
        structured_json = payload.model_dump()
        write_text(json_path, dumps(structured_json))
        write_markdown(
            markdown_path,
            f"""
# Paper Assessment

## 论文题目
{paper.title}

## 任务定义
{payload.task_definition}

## 核心创新点
{payload.novelty_summary}

## 方法概要
{payload.method_summary}

## 数据集
{", ".join(payload.datasets)}

## 评价指标
{", ".join(payload.metrics)}

## 复现依赖
{", ".join(payload.dependencies)}

## 复现难度
{payload.difficulty}

## 复现建议
{payload.recommendation}

## 适用场景
{", ".join(payload.applicable_scenarios)}

## 风险点
{", ".join(payload.risks)}
""",
        )
        assessment = paper.assessment or PaperAssessment(paper_id=paper.id)
        assessment.novelty_summary = payload.novelty_summary
        assessment.task_definition = payload.task_definition
        assessment.method_summary = payload.method_summary
        assessment.datasets = dumps(payload.datasets)
        assessment.metrics = dumps(payload.metrics)
        assessment.dependencies = dumps(payload.dependencies)
        assessment.difficulty = payload.difficulty
        assessment.recommendation = payload.recommendation
        assessment.risks = dumps(payload.risks)
        assessment.applicable_scenarios = dumps(payload.applicable_scenarios)
        assessment.structured_json = dumps(structured_json)
        assessment.markdown_path = str(markdown_path.resolve())
        assessment.json_path = str(json_path.resolve())
        paper.status = PaperStatus.ASSESSED.value
        self.paper_repo.update(paper)
        return self.assessment_repo.upsert(assessment)

