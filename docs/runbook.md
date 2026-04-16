# Paper2Lab Runbook

## 当前阶段
- 阶段覆盖：Phase 1 到 Phase 7 的 MVP 闭环版本
- 推荐模式：离线演示模式
- 主要入口：
  - 后端 API: `http://localhost:8000/docs`
  - 前端页面: `http://localhost:5173`

## 启动顺序
1. 安装后端依赖并执行 `python scripts/seed_demo.py`
2. 启动后端 `python scripts/run_backend.py`
3. 启动前端 `npm run dev`
4. 如需本地定时任务，启动 `python scripts/run_scheduler.py`

## 离线演示路径
1. 新建研究方向或使用已导入样例
2. 通过 Topic 页面触发扫描
3. 打开 Paper 页面执行评估
4. 启动复现计划生成
5. 在 Repro 页面选择样例日志进行诊断
6. 返回 Topic 页面生成周报

## 已知限制
- 在线模式依赖 arXiv API 与外部网络可用性
- LLM 评估需要 `.env` 中提供 OpenAI-compatible key
- Docker 交付物已提供，但当前机器未安装 Docker，未在本机实测容器启动

