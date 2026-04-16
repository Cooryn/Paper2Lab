import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FormEvent, useState } from "react";
import { api } from "../lib/api";
import { Panel } from "../components/Panel";
import { StatCard } from "../components/StatCard";

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [keywords, setKeywords] = useState("");

  const dashboardQuery = useQuery({ queryKey: ["dashboard"], queryFn: api.getDashboard });
  const topicsQuery = useQuery({ queryKey: ["topics"], queryFn: api.listTopics });
  const reportsQuery = useQuery({ queryKey: ["reports"], queryFn: () => api.listReports() });

  const createTopicMutation = useMutation({
    mutationFn: api.createTopic,
    onSuccess: () => {
      setName("");
      setDescription("");
      setKeywords("");
      queryClient.invalidateQueries({ queryKey: ["topics"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  function handleCreateTopic(event: FormEvent) {
    event.preventDefault();
    createTopicMutation.mutate({
      name,
      description,
      keywords: keywords.split(",").map((item) => item.trim()).filter(Boolean),
    });
  }

  const stats = dashboardQuery.data;

  return (
    <div className="space-y-8">
      <section className="grid gap-4 md:grid-cols-5">
        <StatCard label="研究方向" value={stats?.topic_count ?? 0} />
        <StatCard label="本周新增论文" value={stats?.new_papers_this_week ?? 0} tone="accent" />
        <StatCard label="已评估论文" value={stats?.assessed_papers ?? 0} />
        <StatCard label="正在复现" value={stats?.repro_active ?? 0} />
        <StatCard label="当前阻塞" value={stats?.blocked_count ?? 0} tone="coral" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Panel title="研究方向" subtitle="进入方向页后可扫描论文、导入样例、生成周报。">
          <div className="space-y-3">
            {(topicsQuery.data ?? []).map((topic) => (
              <Link
                key={topic.id}
                to={`/topics/${topic.id}`}
                className="block rounded-2xl border border-slate-100 p-4 transition hover:border-accent/30 hover:bg-slate-50"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="text-lg font-semibold">{topic.name}</div>
                    <div className="mt-1 text-sm text-slate-500">{topic.description}</div>
                  </div>
                  <div className="text-right text-xs text-slate-500">
                    <div>关键词</div>
                    <div>{topic.keywords.join(", ") || "-"}</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </Panel>

        <Panel title="新建研究方向" subtitle="支持输入方向描述和关键词集合。">
          <form className="space-y-3" onSubmit={handleCreateTopic}>
            <input placeholder="方向名称，例如 multimodal agents" value={name} onChange={(e) => setName(e.target.value)} required />
            <textarea
              placeholder="方向描述"
              className="min-h-28 w-full"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <input
              placeholder="关键词，使用英文逗号分隔"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
            <button className="primary w-full" type="submit">
              新建方向
            </button>
          </form>
        </Panel>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel title="最近周报" subtitle="可直接进入报告详情查看全文和摘要。">
          <div className="space-y-3">
            {(reportsQuery.data ?? []).slice(0, 5).map((report) => (
              <Link key={report.id} to={`/reports/${report.id}`} className="block rounded-2xl bg-slate-50 p-4">
                <div className="text-sm font-semibold">Report #{report.id}</div>
                <div className="mt-2 text-sm text-slate-600">{report.summary_text}</div>
              </Link>
            ))}
          </div>
        </Panel>

        <Panel title="演示提示" subtitle="推荐的 MVP 演示顺序。">
          <ol className="space-y-3 text-sm text-slate-700">
            <li>1. 进入某个 Topic，运行扫描或导入样例论文。</li>
            <li>2. 打开论文详情页执行评估，查看结构化结果和 Markdown 报告。</li>
            <li>3. 启动复现，检查生成的 repro plan、todo、shell 和 YAML。</li>
            <li>4. 在复现项目页选择样例日志，演示 LabOps Agent 的诊断输出。</li>
            <li>5. 返回 Topic 或 Reports 页面生成并查看周报。</li>
          </ol>
        </Panel>
      </section>
    </div>
  );
}

