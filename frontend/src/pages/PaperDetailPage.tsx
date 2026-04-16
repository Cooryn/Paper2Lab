import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { useState } from "react";
import { api } from "../lib/api";
import { MarkdownCard } from "../components/MarkdownCard";
import { Panel } from "../components/Panel";

export function PaperDetailPage() {
  const { paperId = "" } = useParams();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const paperQuery = useQuery({ queryKey: ["paper", paperId], queryFn: () => api.getPaper(paperId), enabled: !!paperId });

  const assessMutation = useMutation({
    mutationFn: () => api.assessPaper(paperId, { use_llm: false, notes: "Frontend trigger" }),
    onSuccess: () => {
      setMessage("Reader Agent 已完成结构化评估。");
      queryClient.invalidateQueries({ queryKey: ["paper", paperId] });
      queryClient.invalidateQueries({ queryKey: ["papers"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const reproMutation = useMutation({
    mutationFn: () => api.startRepro(paperId),
    onSuccess: () => {
      setMessage("Repro Agent 已生成复现计划。");
      queryClient.invalidateQueries({ queryKey: ["paper", paperId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const paper = paperQuery.data;
  const assessment = paper?.assessment;

  return (
    <div className="space-y-6">
      <Panel title={paper?.title ?? "Paper Detail"} subtitle={paper?.abstract ?? "加载中..."}>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl bg-slate-50 p-4 text-sm">
            <div><span className="font-semibold">状态：</span>{paper?.status}</div>
            <div><span className="font-semibold">优先级：</span>{paper?.priority}</div>
            <div><span className="font-semibold">来源：</span>{paper?.import_source}</div>
            <div><span className="font-semibold">作者：</span>{paper?.authors.join(", ") || "-"}</div>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 text-sm">
            <div><span className="font-semibold">PDF：</span>{paper?.pdf_path ?? "-"}</div>
            <div><span className="font-semibold">URL：</span>{paper?.source_url ?? "-"}</div>
            <div><span className="font-semibold">标签：</span>{paper?.tags.join(", ") || "-"}</div>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button className="primary" onClick={() => assessMutation.mutate()}>
            评估论文
          </button>
          <button className="secondary" onClick={() => reproMutation.mutate()}>
            开始复现
          </button>
        </div>
        {message ? <div className="mt-4 text-sm text-accent">{message}</div> : null}
      </Panel>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <Panel title="结构化评估" subtitle="JSON 结果已同步落盘为 assessment.json 与 assessment.md。">
          {assessment ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">任务定义</div>
                <div className="mt-2">{assessment.task_definition}</div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">核心创新点</div>
                <div className="mt-2">{assessment.novelty_summary}</div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">方法概要</div>
                <div className="mt-2">{assessment.method_summary}</div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">复现判断</div>
                <div className="mt-2">难度：{assessment.difficulty}</div>
                <div>建议：{assessment.recommendation}</div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">数据集 / 指标</div>
                <div className="mt-2">{assessment.datasets.join(", ")}</div>
                <div>{assessment.metrics.join(", ")}</div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 text-sm">
                <div className="font-semibold">依赖 / 风险</div>
                <div className="mt-2">{assessment.dependencies.join(", ")}</div>
                <div className="mt-2">{assessment.risks.join("；")}</div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">尚未评估，点击上方按钮触发 Reader Agent。</div>
          )}
        </Panel>

        <MarkdownCard title="评估报告 Markdown" content={assessment?.markdown_content} />
      </section>

      <Panel title="复现项目" subtitle="启动复现后可进入项目详情查看所有生成文件。">
        <div className="space-y-3">
          {(paper?.repro_projects ?? []).map((project) => (
            <Link key={project.id} to={`/repro-projects/${project.id}`} className="block rounded-2xl bg-slate-50 p-4">
              <div className="font-semibold">{project.project_name}</div>
              <div className="mt-1 text-sm text-slate-500">{project.project_dir}</div>
            </Link>
          ))}
          {!(paper?.repro_projects ?? []).length ? (
            <div className="text-sm text-slate-500">尚未创建复现项目。</div>
          ) : null}
        </div>
      </Panel>
    </div>
  );
}

