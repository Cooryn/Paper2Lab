from __future__ import annotations

import json
import re

import httpx

from app.core.config import get_settings
from app.core.enums import DifficultyLevel, RecommendationType
from app.schemas.assessment import AssessmentPayload


class AssessmentEngine:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, *, title: str, abstract: str, raw_text: str, use_llm: bool, notes: str | None) -> AssessmentPayload:
        if use_llm and self.settings.openai_api_key:
            llm_payload = self._try_llm(title=title, abstract=abstract, raw_text=raw_text, notes=notes)
            if llm_payload:
                return llm_payload
        return self._fallback(title=title, abstract=abstract, raw_text=raw_text, notes=notes)

    def _try_llm(self, *, title: str, abstract: str, raw_text: str, notes: str | None) -> AssessmentPayload | None:
        prompt = (
            "You are assessing a research paper for reproducibility.\n"
            "Return strict JSON with keys: title, task_definition, novelty_summary, method_summary, "
            "datasets, metrics, dependencies, difficulty, recommendation, risks, applicable_scenarios.\n"
            f"Title: {title}\nAbstract: {abstract}\nNotes: {notes or ''}\nContent: {raw_text[:5000]}"
        )
        try:
            response = httpx.post(
                f"{self.settings.openai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.openai_model,
                    "messages": [
                        {"role": "system", "content": "Output only valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return AssessmentPayload(**data)
        except Exception:
            return None

    def _fallback(self, *, title: str, abstract: str, raw_text: str, notes: str | None) -> AssessmentPayload:
        lowered = f"{title}\n{abstract}\n{raw_text}".lower()
        datasets = self._extract_items(
            lowered,
            ["dataset", "benchmarks", "data"],
            ["mimic", "coco", "imagenet", "msrvtt", "hotpotqa", "pubmed", "mmmu"],
        )
        metrics = self._extract_items(
            lowered,
            ["metric", "evaluate"],
            ["f1", "accuracy", "bleu", "rouge", "dice", "iou", "recall", "pass@1"],
        )
        dependencies = self._extract_items(
            lowered,
            ["code", "gpu", "framework"],
            ["pytorch", "cuda", "transformers", "faiss", "opencv", "mmcv", "deepspeed"],
        )
        task_definition = self._extract_sentence(abstract or raw_text, ["task", "we study", "we propose", "this paper"])
        novelty_summary = self._extract_sentence(raw_text, ["novel", "contribution", "we introduce", "our key idea"])
        method_summary = self._extract_sentence(raw_text, ["method", "framework", "architecture", "pipeline"])
        risks = []
        if "code will be released" in lowered or "not released" in lowered:
            risks.append("公开代码状态不稳定，复现前需确认仓库是否可用。")
        if "large language model" in lowered or "70b" in lowered or "8x" in lowered:
            risks.append("模型规模较大，算力成本可能偏高。")
        if "medical" in lowered:
            risks.append("数据合规与隐私访问门槛可能较高。")
        if notes:
            risks.append(f"补充备注：{notes}")

        difficulty = DifficultyLevel.MEDIUM.value
        if len(dependencies) >= 3 or "multi-stage" in lowered or "distributed" in lowered:
            difficulty = DifficultyLevel.HIGH.value
        elif "baseline" in lowered or "simple" in lowered:
            difficulty = DifficultyLevel.LOW.value

        recommendation = RecommendationType.QUICK_BASELINE.value
        if difficulty == DifficultyLevel.HIGH.value:
            recommendation = RecommendationType.HOLD.value
        elif datasets and dependencies:
            recommendation = RecommendationType.FULL_REPRO.value

        applicable = []
        if "rag" in lowered:
            applicable.append("检索增强生成系统评测与对照实验。")
        if "agent" in lowered:
            applicable.append("多智能体系统与任务分解流程设计。")
        if "medical" in lowered:
            applicable.append("医学影像研究与分割实验设计。")
        if not applicable:
            applicable.append("适合做方向跟踪、基线复现和实验设计参考。")

        return AssessmentPayload(
            title=title,
            task_definition=task_definition or "围绕论文核心任务定义进行问题建模，并给出实验设置。",
            novelty_summary=novelty_summary or "论文主要贡献集中在方法设计、实验协议和任务拆解方式。",
            method_summary=method_summary or "采用模块化 pipeline，将检索、建模与评估过程进行串联。",
            datasets=datasets or ["待人工确认数据集"],
            metrics=metrics or ["待人工确认评价指标"],
            dependencies=dependencies or ["Python", "PyTorch", "CUDA（如需 GPU）"],
            difficulty=difficulty,
            recommendation=recommendation,
            risks=risks or ["论文细节可能不足，需补充阅读附录与代码实现。"],
            applicable_scenarios=applicable,
        )

    @staticmethod
    def _extract_sentence(text: str, keywords: list[str]) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
        for sentence in sentences:
            lowered = sentence.lower()
            if any(keyword in lowered for keyword in keywords):
                return sentence.strip()[:280]
        return text.replace("\n", " ").strip()[:280]

    @staticmethod
    def _extract_items(text: str, anchors: list[str], candidates: list[str]) -> list[str]:
        items = [candidate for candidate in candidates if candidate in text]
        if items:
            formatted = []
            for item in sorted(set(items)):
                formatted.append(item.upper() if len(item) <= 4 or item.startswith("pass") else item.title())
            return formatted
        for anchor in anchors:
            if anchor in text:
                return [f"从论文中围绕 {anchor} 进一步确认"]
        return []

