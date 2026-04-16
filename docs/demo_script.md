# Paper2Lab Demo Script

目标时长：6-8 分钟

## 1. 介绍项目定位（30s）
- 打开 Dashboard，说明它不是普通论文问答助手，而是围绕科研闭环的多 agent 工作台。
- 指出四个 agent：Radar、Reader、Repro、LabOps。

## 2. 新建或查看研究方向（45s）
- 进入 Topic Detail。
- 展示方向描述、关键词、现有论文列表。
- 点击“运行扫描/追踪”，说明可离线读取样例元数据，也可切换在线 arXiv 模式。

## 3. 导入与筛选论文（60s）
- 在 Topic 下使用“导入本地样例”或“手动输入标题/摘要”。
- 回到列表，展示状态、优先级、标签。
- 强调 Radar Agent 会做去重与初筛。

## 4. 评估论文（75s）
- 进入某篇论文详情，点击“评估论文”。
- 展示结构化评估内容：任务定义、创新点、方法、数据集、指标、复现难度、建议和风险。
- 打开生成的 Markdown 报告和 JSON 工件。

## 5. 启动复现（75s）
- 点击“开始复现”。
- 展示 Paper2Lab 在 `backend/generated/repros/...` 下生成的 `repro_plan.md`、`todo.md`、`setup_env.sh`、`run_baseline.sh`、`configs/default.yaml`。
- 说明 Repro Agent 通过受控 exec 做目录和环境检查。

## 6. 日志诊断（60s）
- 进入 Repro Project Detail，选择一份样例错误日志。
- 展示诊断类型、根因、修复建议与置信度。
- 打开 `diagnosis.md`，强调当前先用稳定的规则匹配，后续可接 LLM。

## 7. 周报生成（60s）
- 回到 Topic 页面点击“生成周报”。
- 展示本周新增论文、已评估、已启动复现、阻塞项和下一步建议。
- 同时展示适合发群的短摘要。

## 8. OpenClaw 对接（30s）
- 打开 `docs/openclaw_integration.md`。
- 说明如何通过消息入口、cron、hooks 与 message 能力把本地 fallback 替换成 OpenClaw 运行时。

