# Paper2Lab

Paper2Lab 是一个面向科研团队、研究生和实验室助理的闭环智能体原型，围绕“方向追踪 -> 论文筛选 -> 论文解析 -> 复现计划生成 -> 实验日志诊断 -> 周报输出”推进科研工作，而不是把系统做成一个只能回答问题的论文聊天机器人。

## 为什么它不是普通论文助手
- 它以 `Radar / Reader / Repro / LabOps` 四个 agent 组织工作，而不是单聊天窗口。
- 它会真实生成并消费科研工件：`PDF / JSON / Markdown / YAML / shell / logs`。
- 它支持任务调度、受控 exec、通知抽象层和 OpenClaw 映射，强调平台能力。
- 它的核心输出不是“答案”，而是可继续执行的评估、复现计划、诊断和报告。

## 核心能力
- 研究方向管理：创建 topic、维护关键词、离线或在线扫描候选论文。
- 论文导入：支持样例元数据、手工标题摘要、URL/arXiv、PDF 上传。
- Reader Agent 评估：输出结构化 JSON 与 Markdown 报告，覆盖任务定义、创新点、方法、数据集、指标、依赖、难度、建议和风险。
- Repro Agent 生成：真实写入 `repro_plan.md`、`todo.md`、`setup_env.sh`、`run_baseline.sh`、`configs/default.yaml`。
- LabOps Agent 诊断：对常见训练/推理日志做规则诊断，并生成 `diagnosis.md`。
- 报告与自动化：生成周报全文和群消息摘要，支持 APScheduler fallback，并在文档中映射到 OpenClaw cron / hooks / message / webhooks。

## 系统架构
### 多智能体分工
- `RadarAgent`：方向追踪、候选论文收集、去重、优先级打标。
- `ReaderAgent`：论文解析、结构化评估、JSON/Markdown 落盘。
- `ReproAgent`：复现工程初始化、脚本和配置生成、受控 exec 校验。
- `LabOpsAgent`：日志分析、异常诊断、周报生成、通知摘要输出。

### 数据与工件流
1. Topic 保存关键词与方向描述。
2. Radar Agent 从 `samples/metadata` 或在线源拉取候选论文，存入 SQLite。
3. Reader Agent 读取元数据或 PDF，生成 `assessment.json` 与 `assessment.md`。
4. Repro Agent 生成复现工程目录与 shell/YAML/Markdown 工件。
5. LabOps Agent 分析实验日志，输出 `diagnosis.md` 与 weekly report。

## 技术栈
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2, SQLite, Pydantic v2, APScheduler
- Frontend: React, Vite, TypeScript, Tailwind CSS, React Router, TanStack Query
- Parsing & Diagnostics: pypdf, reportlab, PyYAML, regex rules, optional OpenAI-compatible LLM adapter

## 目录结构
```text
paper2lab/
  .github/
    workflows/ci.yml
    ISSUE_TEMPLATE/
  README.md
  LICENSE
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  .env.example
  docker-compose.yml
  docs/
  scripts/
  samples/
  backend/
  frontend/
```

## GitHub 仓库协作文件
- CI: [`.github/workflows/ci.yml`](/D:/Codex/Paper2Lab/.github/workflows/ci.yml)
- Issue 模板: [`.github/ISSUE_TEMPLATE`](/D:/Codex/Paper2Lab/.github/ISSUE_TEMPLATE)
- PR 模板: [`.github/pull_request_template.md`](/D:/Codex/Paper2Lab/.github/pull_request_template.md)
- 协作规范: [CONTRIBUTING.md](/D:/Codex/Paper2Lab/CONTRIBUTING.md)
- 行为准则: [CODE_OF_CONDUCT.md](/D:/Codex/Paper2Lab/CODE_OF_CONDUCT.md)
- 子项目说明: [backend/README.md](/D:/Codex/Paper2Lab/backend/README.md), [frontend/README.md](/D:/Codex/Paper2Lab/frontend/README.md)

## 本地运行
### 1. 准备配置
- 复制 `.env.example` 为 `.env`
- 默认使用 SQLite、本地离线模式和可选 LLM fallback

### 2. 安装依赖
- 后端：`python -m pip install -r backend/requirements.txt`
- 前端：`cd frontend && npm install`

### 3. 初始化演示数据
- `python scripts/seed_demo.py`
- 该脚本会：
  - 创建 SQLite 表
  - 生成样例 PDF 到 `samples/papers/`
  - 写入样例 topic
  - 扫描样例论文
  - 生成一条评估、一个复现项目、一次日志诊断和一份周报

### 4. 启动服务
- 后端：`python scripts/run_backend.py`
- 前端：`cd frontend && npm run dev`
- 本地调度：`python scripts/run_scheduler.py`

### 5. Docker 说明
- 仓库提供 `docker-compose.yml`、`backend/Dockerfile`、`frontend/Dockerfile`
- 当前开发机未安装 Docker，因此交付物已补齐，但本机验证以非 Docker 模式为准

## 演示流程
- 详细运行路径见 [docs/runbook.md](/D:/Codex/Paper2Lab/docs/runbook.md)
- 6-8 分钟 Demo 流程见 [docs/demo_script.md](/D:/Codex/Paper2Lab/docs/demo_script.md)
- OpenClaw 对接说明见 [docs/openclaw_integration.md](/D:/Codex/Paper2Lab/docs/openclaw_integration.md)

## 前后端页面
- Dashboard：方向数量、本周新增论文、已评估、正在复现、阻塞项。
- Topic Detail：方向信息、关键词、论文列表、扫描按钮、周报按钮、导入入口。
- Paper Detail：论文基础信息、评估结果、开始复现、生成文件入口。
- Repro Project Detail：计划/TODO/脚本/YAML、日志诊断结果。
- Reports：周报列表、详情全文、群消息摘要。

## OpenClaw 集成入口
- 见 [docs/openclaw_integration.md](/D:/Codex/Paper2Lab/docs/openclaw_integration.md)
- 文档包含：
  - agent 角色映射
  - message 入口触发方式
  - exec 在项目中的安全边界
  - cron 与本地 APScheduler 的映射
  - hooks / webhooks 的适配点
  - message 通知对接建议

## 已实现功能
- 研究方向 CRUD 与 Dashboard 指标
- 离线样例扫描与可选在线 arXiv provider
- 论文导入、去重、列表与详情
- 结构化评估 JSON/Markdown 落盘
- 复现计划、Shell、YAML、TODO 文件真实写入
- 实验日志规则诊断与 `diagnosis.md`
- 周报全文与摘要
- 受控 exec 日志记录
- 样例数据、测试、演示脚本与 OpenClaw 文档

## 测试与验证
- 后端测试：`python -m pytest -q backend/tests`
- 前端构建：`cd frontend && npm run build`
- 已在当前环境验证：
  - `seed_demo.py` 成功运行
  - 后端测试 `5 passed`
  - 前端 `vite build` 成功

## 未实现或保留扩展位
- 多用户与权限系统
- 向量检索与长期记忆
- 更丰富的外部论文源
- 真实 Telegram / 飞书消息发送
- 更细粒度的 OpenClaw runtime adapter
