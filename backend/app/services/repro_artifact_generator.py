from __future__ import annotations

from pathlib import Path

import yaml

from app.core.config import get_settings
from app.utils.files import GENERATOR_BANNER, ensure_dir, write_text
from app.utils.markdown import write_markdown
from app.utils.slug import slugify


class ReproArtifactGenerator:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate(self, *, paper_title: str, assessment: dict, topic_name: str) -> dict[str, str]:
        project_slug = slugify(f"{topic_name}-{paper_title}")
        root = ensure_dir(self.settings.generated_dir / "repros" / project_slug)
        config_dir = ensure_dir(root / "configs")

        plan_path = root / "repro_plan.md"
        todo_path = root / "todo.md"
        setup_path = root / "setup_env.sh"
        run_path = root / "run_baseline.sh"
        config_path = config_dir / "default.yaml"

        write_markdown(
            plan_path,
            f"""
# Reproduction Plan

## Paper
- Title: {paper_title}
- Difficulty: {assessment.get('difficulty', 'medium')}
- Recommendation: {assessment.get('recommendation', 'quick_baseline')}

## Environment
- Python: 3.11
- Framework: PyTorch 2.x
- Key dependencies: {", ".join(assessment.get("dependencies", []))}

## Data Preparation
1. 确认数据集访问方式与许可证。
2. 创建 `data/raw` 和 `data/processed` 目录。
3. 补全下载脚本或手工放置数据。

## Baseline Command Template
```bash
bash run_baseline.sh --config configs/default.yaml
```

## Milestones
- D1: 阅读论文与附录，确认数据与评价指标。
- D2: 跑通 baseline，并记录首轮结果。
- D3: 对齐关键超参数与预处理细节。
- D4: 对复现结果做误差分析和日志诊断。

## Risks And Open Questions
- 公开代码与 checkpoint 是否可用待确认。
- 论文中的关键实现细节可能需要人工补完。
- 如需多卡或大模型，请提前确认算力预算。
""",
        )

        write_markdown(
            todo_path,
            """
# TODO

- [ ] 确认代码仓库或补全自建实现骨架
- [ ] 准备数据集与目录结构
- [ ] 配置默认超参数
- [ ] 跑通 baseline 命令
- [ ] 记录实验日志与异常
- [ ] 对照论文指标输出首轮复现实验结论
""",
        )

        write_text(
            setup_path,
            f"""#!/usr/bin/env bash
# {GENERATOR_BANNER}
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
echo "TODO: install project-specific dependencies here"
echo "Baseline dependencies: {' '.join(assessment.get('dependencies', []))}"
""",
        )

        write_text(
            run_path,
            f"""#!/usr/bin/env bash
# {GENERATOR_BANNER}
set -euo pipefail

CONFIG_PATH="${{2:-configs/default.yaml}}"
echo "Running baseline with $CONFIG_PATH"
echo "TODO: replace with the real training/evaluation command"
python -c "print('Paper2Lab baseline placeholder for: {paper_title}')"
""",
        )

        config = {
            "generated_by": "Paper2Lab",
            "paper_title": paper_title,
            "python_version": "3.11",
            "framework": "pytorch-2.x",
            "task_definition": assessment.get("task_definition"),
            "datasets": assessment.get("datasets", []),
            "metrics": assessment.get("metrics", []),
            "hyperparameters": {
                "batch_size": "TODO",
                "learning_rate": "TODO",
                "epochs": "TODO",
            },
            "paths": {
                "data_root": "./data",
                "output_root": "./outputs",
                "checkpoint": "./checkpoints/latest.pt",
            },
        }
        write_text(config_path, yaml.safe_dump(config, sort_keys=False, allow_unicode=True))

        return {
            "project_dir": str(root.resolve()),
            "plan_path": str(plan_path.resolve()),
            "todo_path": str(todo_path.resolve()),
            "setup_script_path": str(setup_path.resolve()),
            "run_script_path": str(run_path.resolve()),
            "config_path": str(config_path.resolve()),
            "project_name": project_slug,
        }

