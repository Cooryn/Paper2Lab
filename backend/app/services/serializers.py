from __future__ import annotations

from app.models import ExperimentLog, Paper, PaperAssessment, Report, ReproProject, ResearchTopic
from app.schemas.assessment import AssessmentResponse
from app.schemas.logs import ExperimentLogResponse
from app.schemas.paper import PaperDetailResponse, PaperResponse
from app.schemas.report import ReportResponse
from app.schemas.repro import ReproProjectResponse
from app.schemas.topic import TopicDetailResponse, TopicResponse
from app.utils.files import read_text
from app.utils.json import loads_dict, loads_list


def topic_to_response(topic: ResearchTopic) -> TopicResponse:
    return TopicResponse(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        keywords=loads_list(topic.keywords),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


def topic_to_detail(topic: ResearchTopic, *, paper_count: int, report_count: int) -> TopicDetailResponse:
    return TopicDetailResponse(
        **topic_to_response(topic).model_dump(),
        paper_count=paper_count,
        report_count=report_count,
    )


def paper_to_response(paper: Paper) -> PaperResponse:
    return PaperResponse(
        id=paper.id,
        topic_id=paper.topic_id,
        title=paper.title,
        authors=loads_list(paper.authors),
        abstract=paper.abstract,
        source_url=paper.source_url,
        pdf_path=paper.pdf_path,
        published_at=paper.published_at,
        status=paper.status,
        priority=paper.priority,
        tags=loads_list(paper.tags),
        import_source=paper.import_source,
        created_at=paper.created_at,
        updated_at=paper.updated_at,
    )


def paper_to_detail(paper: Paper) -> PaperDetailResponse:
    return PaperDetailResponse(
        **paper_to_response(paper).model_dump(),
        assessment_id=paper.assessment.id if paper.assessment else None,
        repro_project_ids=[project.id for project in paper.repro_projects],
        assessment=assessment_to_response(paper.assessment).model_dump() if paper.assessment else None,
        repro_projects=[repro_to_response(project).model_dump() for project in paper.repro_projects],
    )


def assessment_to_response(assessment: PaperAssessment) -> AssessmentResponse:
    markdown_content = None
    if assessment.markdown_path:
        try:
            markdown_content = read_text(__import__("pathlib").Path(assessment.markdown_path))
        except FileNotFoundError:
            markdown_content = None
    return AssessmentResponse(
        id=assessment.id,
        paper_id=assessment.paper_id,
        novelty_summary=assessment.novelty_summary,
        task_definition=assessment.task_definition,
        method_summary=assessment.method_summary,
        datasets=loads_list(assessment.datasets),
        metrics=loads_list(assessment.metrics),
        dependencies=loads_list(assessment.dependencies),
        difficulty=assessment.difficulty,
        recommendation=assessment.recommendation,
        risks=loads_list(assessment.risks),
        applicable_scenarios=loads_list(assessment.applicable_scenarios),
        structured_json=loads_dict(assessment.structured_json),
        markdown_path=assessment.markdown_path,
        json_path=assessment.json_path,
        markdown_content=markdown_content,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


def repro_to_response(project: ReproProject) -> ReproProjectResponse:
    generated_contents = {}
    for key, path in {
        "plan": project.plan_path,
        "todo": project.todo_path,
        "setup": project.setup_script_path,
        "run": project.run_script_path,
        "config": project.config_path,
    }.items():
        try:
            generated_contents[key] = read_text(__import__("pathlib").Path(path))
        except FileNotFoundError:
            generated_contents[key] = ""
    return ReproProjectResponse(
        id=project.id,
        paper_id=project.paper_id,
        project_name=project.project_name,
        project_dir=project.project_dir,
        plan_path=project.plan_path,
        todo_path=project.todo_path,
        setup_script_path=project.setup_script_path,
        run_script_path=project.run_script_path,
        config_path=project.config_path,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        generated_files={
            "plan": project.plan_path,
            "todo": project.todo_path,
            "setup": project.setup_script_path,
            "run": project.run_script_path,
            "config": project.config_path,
        },
        generated_contents=generated_contents,
        experiment_logs=[
            experiment_log_to_response(log).model_dump() for log in getattr(project, "experiment_logs", [])
        ],
    )


def experiment_log_to_response(log: ExperimentLog) -> ExperimentLogResponse:
    diagnosis_content = None
    if log.diagnosis_path:
        try:
            diagnosis_content = read_text(__import__("pathlib").Path(log.diagnosis_path))
        except FileNotFoundError:
            diagnosis_content = None
    return ExperimentLogResponse(
        id=log.id,
        repro_project_id=log.repro_project_id,
        log_path=log.log_path,
        diagnosis_type=log.diagnosis_type,
        root_cause=log.root_cause,
        suggestion=log.suggestion,
        confidence=log.confidence,
        diagnosis_path=log.diagnosis_path,
        diagnosis_content=diagnosis_content,
        created_at=log.created_at,
        updated_at=log.updated_at,
    )


def report_to_response(report: Report) -> ReportResponse:
    content = None
    if report.report_path:
        try:
            content = read_text(__import__("pathlib").Path(report.report_path))
        except FileNotFoundError:
            content = None
    return ReportResponse(
        id=report.id,
        topic_id=report.topic_id,
        report_type=report.report_type,
        report_path=report.report_path,
        summary_text=report.summary_text,
        content=content,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )
