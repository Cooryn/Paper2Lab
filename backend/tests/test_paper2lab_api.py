from __future__ import annotations

from pathlib import Path


def create_topic(client, name: str = "multimodal agents"):
    response = client.post(
        "/api/topics",
        json={
            "name": name,
            "description": "test topic",
            "keywords": [name, "benchmark"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def import_sample_paper(client, topic_id: int, sample_name: str = "multimodal_agents_survey.json"):
    response = client.post(
        "/api/papers/import",
        json={"import_mode": "sample", "topic_id": topic_id, "sample_name": sample_name},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_topic_and_paper_import(client):
    topic = create_topic(client)
    paper = import_sample_paper(client, topic["id"])

    papers_response = client.get(f"/api/papers?topic_id={topic['id']}")
    assert papers_response.status_code == 200
    papers = papers_response.json()
    assert len(papers) == 1
    assert papers[0]["title"] == paper["title"]

    duplicate_response = client.post(
        "/api/papers/import",
        json={"import_mode": "sample", "topic_id": topic["id"], "sample_name": "multimodal_agents_survey.json"},
    )
    assert duplicate_response.status_code == 200
    papers_response = client.get(f"/api/papers?topic_id={topic['id']}")
    assert len(papers_response.json()) == 1


def test_paper_assessment_generation(client):
    topic = create_topic(client, "RAG evaluation")
    paper = import_sample_paper(client, topic["id"], "rag_eval_guardrails.json")

    assessment_response = client.post(f"/api/papers/{paper['id']}/assess", json={"use_llm": False})
    assert assessment_response.status_code == 200, assessment_response.text
    assessment = assessment_response.json()
    assert assessment["task_definition"]
    assert assessment["structured_json"]["title"] == "RAGBench Guardrails: A Practical Evaluation Pipeline for Retrieval-Augmented Generation"
    assert Path(assessment["json_path"]).exists()
    assert Path(assessment["markdown_path"]).exists()


def test_repro_plan_generation_files(client):
    topic = create_topic(client, "medical image segmentation")
    paper = import_sample_paper(client, topic["id"], "medical_seg_adapter.json")
    client.post(f"/api/papers/{paper['id']}/assess", json={"use_llm": False})

    repro_response = client.post(f"/api/papers/{paper['id']}/start-repro")
    assert repro_response.status_code == 200, repro_response.text
    project = repro_response.json()
    assert Path(project["plan_path"]).exists()
    assert Path(project["todo_path"]).exists()
    assert Path(project["setup_script_path"]).exists()
    assert Path(project["run_script_path"]).exists()
    assert Path(project["config_path"]).exists()


def test_log_diagnosis(client):
    topic = create_topic(client)
    paper = import_sample_paper(client, topic["id"])
    client.post(f"/api/papers/{paper['id']}/assess", json={"use_llm": False})
    repro_response = client.post(f"/api/papers/{paper['id']}/start-repro")
    project = repro_response.json()

    diagnosis_response = client.post(
        f"/api/repro-projects/{project['id']}/analyze-log",
        json={"sample_log_name": "missing_dependency.log"},
    )
    assert diagnosis_response.status_code == 200, diagnosis_response.text
    diagnosis = diagnosis_response.json()
    assert diagnosis["diagnosis_type"] == "missing_dependency"
    assert "依赖包" in diagnosis["root_cause"]
    assert Path(diagnosis["diagnosis_path"]).exists()


def test_weekly_report_generation(client):
    topic = create_topic(client)
    import_sample_paper(client, topic["id"])

    report_response = client.post(f"/api/topics/{topic['id']}/generate-weekly-report")
    assert report_response.status_code == 200, report_response.text
    report = report_response.json()
    assert report["summary_text"]
    assert Path(report["report_path"]).exists()

