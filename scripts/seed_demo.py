from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.agents.labops_agent import LabOpsAgent
from app.agents.radar_agent import RadarAgent
from app.agents.reader_agent import ReaderAgent
from app.agents.repro_agent import ReproAgent
from app.core.database import Base, SessionLocal, engine
from app.models import ResearchTopic
from app.repositories.topic_repository import TopicRepository
from app.utils.json import dumps


SAMPLE_TOPICS = [
    {
        "name": "multimodal agents",
        "description": "跟踪具备视觉、工具和规划能力的多模态智能体论文。",
        "keywords": ["multimodal agents", "tool feedback", "visual planning"],
    },
    {
        "name": "RAG evaluation",
        "description": "聚焦检索增强生成系统的评测、归因和鲁棒性分析。",
        "keywords": ["RAG evaluation", "citation faithfulness", "retrieval benchmark"],
    },
    {
        "name": "medical image segmentation",
        "description": "面向医学影像分割任务，跟踪可复现方法与数据集门槛。",
        "keywords": ["medical image segmentation", "dice", "adapter"],
    },
]


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_minimal_pdf(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    y = 760
    content_lines = ["BT", "/F1 20 Tf", f"72 {y} Td", f"({escape_pdf_text(title)}) Tj", "/F1 11 Tf"]
    for index, line in enumerate(lines, start=1):
        offset = 28 if index == 1 else 18
        y -= offset
        content_lines.append(f"72 {y} Td")
        content_lines.append(f"({escape_pdf_text(line[:110])}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("utf-8")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {len(stream)} >> stream\n".encode("utf-8") + stream + b"\nendstream endobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]
    header = b"%PDF-1.4\n"
    offsets = []
    payload = header
    for obj in objects:
        offsets.append(len(payload))
        payload += obj
    xref_offset = len(payload)
    payload += f"xref\n0 {len(objects) + 1}\n".encode("utf-8")
    payload += b"0000000000 65535 f \n"
    for offset in offsets:
        payload += f"{offset:010d} 00000 n \n".encode("utf-8")
    payload += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("utf-8")
    )
    path.write_bytes(payload)


def ensure_sample_pdfs() -> None:
    specs = [
        (
            ROOT / "samples/papers/mm_scout.pdf",
            "MM-Scout",
            [
                "Abstract: MM-Scout studies multimodal agents with tool feedback and long-horizon planning.",
                "Method: perception encoder + planner + tool trace memory.",
                "Metrics: accuracy, pass@1, task completion rate.",
                "Reproduction risks: missing code details and GPU cost.",
            ],
        ),
        (
            ROOT / "samples/papers/rag_guardrails.pdf",
            "RAGBench Guardrails",
            [
                "Abstract: evaluation pipeline for RAG systems with retrieval and answer quality checks.",
                "Method: retrieval baseline, citation faithfulness scoring, error taxonomy.",
                "Metrics: recall, faithfulness, accuracy.",
                "Dependencies: PyTorch, FAISS, benchmark datasets.",
            ],
        ),
        (
            ROOT / "samples/papers/medseg_adapter.pdf",
            "MedSegAdapter",
            [
                "Abstract: parameter-efficient medical image segmentation with prompt-guided adapters.",
                "Method: adapter-based segmentation architecture for clinical prompts.",
                "Metrics: Dice, IoU, recall.",
                "Risks: data access, checkpoint compatibility, privacy constraints.",
            ],
        ),
    ]
    for path, title, lines in specs:
        write_minimal_pdf(path, title, lines)


def seed_topics() -> list[int]:
    db = SessionLocal()
    try:
        repo = TopicRepository(db)
        ids = []
        for payload in SAMPLE_TOPICS:
            existing = next((topic for topic in repo.list_all() if topic.name == payload["name"]), None)
            if existing:
                ids.append(existing.id)
                continue
            topic = ResearchTopic(
                name=payload["name"],
                description=payload["description"],
                keywords=dumps(payload["keywords"]),
            )
            ids.append(repo.create(topic).id)
        return ids
    finally:
        db.close()


def seed_flow(topic_ids: list[int]) -> None:
    db = SessionLocal()
    try:
        radar = RadarAgent(db)
        reader = ReaderAgent(db)
        repro = ReproAgent(db)
        labops = LabOpsAgent(db)
        topic_repo = TopicRepository(db)

        for topic_id in topic_ids:
            radar.scan_topic(topic_id)

        first_topic = topic_repo.get(topic_ids[0])
        first_paper = first_topic.papers[0]
        if not first_paper.assessment:
            reader.assess(paper=first_paper, topic_name=first_topic.name, use_llm=False, notes="Demo seed assessment")
        if not first_paper.repro_projects:
            project = repro.start_repro(paper=first_paper, topic_name=first_topic.name)
            log_path = ROOT / "samples/logs/missing_dependency.log"
            labops.analyze_log(project=project, paper=first_paper, log_path=log_path)
        if not first_topic.reports:
            labops.generate_weekly_report(topic=first_topic)
    finally:
        db.close()


def write_metadata_index() -> None:
    metadata_dir = ROOT / "samples/metadata"
    index_path = metadata_dir / "index.json"
    payload = {
        "generated_by": "Paper2Lab",
        "files": sorted(path.name for path in metadata_dir.glob("*.json") if path.name != "index.json"),
    }
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sample_pdfs()
    write_metadata_index()
    topic_ids = seed_topics()
    seed_flow(topic_ids)
    print("Paper2Lab demo data seeded.")


if __name__ == "__main__":
    main()

