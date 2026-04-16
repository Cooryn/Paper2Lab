# OpenClaw Integration Guide

Paper2Lab 的设计目标是优先体现 OpenClaw 平台能力。当前仓库提供本地 fallback，同时保留清晰的 OpenClaw 适配点。

## Agent 角色映射
- `RadarAgent` -> 负责研究方向扫描、候选论文导入、去重和优先级打标
- `ReaderAgent` -> 负责 PDF/元数据解析、结构化评估与报告生成
- `ReproAgent` -> 负责复现计划、脚本模板、目录初始化和受控 exec
- `LabOpsAgent` -> 负责日志诊断、日报/周报、阻塞项聚合和通知摘要

## 消息入口如何触发任务
- 可以把消息入口映射到 FastAPI task endpoints：
  - `/api/tasks/run-topic-scan/{topic_id}`
  - `/api/papers/{id}/assess`
  - `/api/papers/{id}/start-repro`
  - `/api/topics/{id}/generate-weekly-report`
- 示例触发流：
  1. 用户在 OpenClaw message 中发送“扫描 multimodal agents”
  2. 路由层识别 topic，调用 `RadarAgent`
  3. Agent 通过内部 task service 调用扫描逻辑
  4. Notifier 生成 markdown 摘要并回发 message

## exec 在项目中的用途
- 创建复现项目目录
- 检查 Python / pip / CUDA 可用性
- 列举生成文件
- 做基础存在性验证

所有 exec 都由 `ExecRunner` 统一处理：
- 仅允许工作区内路径
- 仅允许白名单命令
- 写入 `backend/data/logs/exec.log`

## 定时任务如何对接 cron
- 本地 fallback 使用 APScheduler。
- OpenClaw 环境可把以下任务映射到 cron jobs：
  - 每日研究方向扫描
  - 每晚实验状态汇总
  - 每周自动生成周报

示例配置片段：

```yaml
agents:
  radar:
    entry: paper2lab.radar.scan
  labops:
    entry: paper2lab.labops.report

cron:
  - name: daily-topic-scan
    schedule: "0 9 * * *"
    target: radar
    input:
      action: scan_all_topics
  - name: weekly-report
    schedule: "0 18 * * 5"
    target: labops
    input:
      action: weekly_report
```

## 通知如何对接 message
- 当前仓库的 `Notifier` 有三层：
  - ConsoleNotifier
  - MarkdownNotifier
  - Integration stub: Telegram / 飞书 / OpenClaw message
- 在 OpenClaw 中，可把 stub 替换为 message sender，把 `summary_text` 直接发到群组或会话。

## Hooks 审计与生命周期
- 可把以下节点接入 hooks：
  - 论文导入前后
  - 复现计划生成前后
  - exec 执行前后
  - 周报生成完成后
- hooks 可用于：
  - 审计日志
  - 失败重试
  - 任务耗时统计
  - 生命周期事件回调

## Webhooks / HTTP 触发
- 如果 OpenClaw 提供 webhook 或 HTTP entry，可直接调用 FastAPI API，复用本项目服务层。
- 推荐做法：OpenClaw 只负责调度、消息和审计，业务逻辑仍收敛在 `backend/app/services`。

## 本地模式运行
- 当没有完整 OpenClaw runtime 时：
  - APScheduler 负责定时任务
  - FastAPI task endpoints 负责任务入口
  - Notifier 输出控制台和 Markdown
  - `docs/demo_script.md` 覆盖完整演示路径

