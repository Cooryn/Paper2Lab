import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { Panel } from "../components/Panel";

const sampleChoices = [
  "multimodal_agents_survey.json",
  "rag_eval_guardrails.json",
  "medical_seg_adapter.json",
];

export function TopicDetailPage() {
  const { topicId = "" } = useParams();
  const queryClient = useQueryClient();
  const [manualTitle, setManualTitle] = useState("");
  const [manualAbstract, setManualAbstract] = useState("");
  const [manualAuthors, setManualAuthors] = useState("");
  const [sampleName, setSampleName] = useState(sampleChoices[0]);
  const [url, setUrl] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const topicQuery = useQuery({ queryKey: ["topic", topicId], queryFn: () => api.getTopic(topicId), enabled: !!topicId });
  const papersQuery = useQuery({ queryKey: ["papers", topicId], queryFn: () => api.listPapers(topicId), enabled: !!topicId });
  const reportsQuery = useQuery({ queryKey: ["reports", topicId], queryFn: () => api.listReports(topicId), enabled: !!topicId });

  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ["topic", topicId] });
    queryClient.invalidateQueries({ queryKey: ["papers", topicId] });
    queryClient.invalidateQueries({ queryKey: ["reports", topicId] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const scanMutation = useMutation({
    mutationFn: () => api.runTopicScan(topicId),
    onSuccess: (result) => {
      setMessage(`Radar Agent 已处理 ${result.count} 篇候选论文。`);
      refreshAll();
    },
  });

  const weeklyReportMutation = useMutation({
    mutationFn: () => api.generateWeeklyReport(topicId),
    onSuccess: (report) => {
      setMessage(`周报已生成：#${report.id}`);
      refreshAll();
    },
  });

  const importMutation = useMutation({
    mutationFn: async (payload: { kind: "sample" | "manual" | "url" | "pdf"; data?: Record<string, unknown>; formData?: FormData }) => {
      if (payload.formData) {
        return api.importPaperForm(payload.formData);
      }
      return api.importPaperJson(payload.data ?? {});
    },
    onSuccess: (paper) => {
      setMessage(`已导入论文：${paper.title}`);
      refreshAll();
    },
  });

  function importSample() {
    importMutation.mutate({
      kind: "sample",
      data: { import_mode: "sample", topic_id: Number(topicId), sample_name: sampleName },
    });
  }

  function importManual(event: FormEvent) {
    event.preventDefault();
    importMutation.mutate({
      kind: "manual",
      data: {
        import_mode: "manual",
        topic_id: Number(topicId),
        title: manualTitle,
        abstract: manualAbstract,
        authors: manualAuthors.split(",").map((item) => item.trim()).filter(Boolean),
      },
    });
  }

  function importUrl(event: FormEvent) {
    event.preventDefault();
    importMutation.mutate({
      kind: "url",
      data: { import_mode: "url", topic_id: Number(topicId), url },
    });
  }

  function importPdf(event: FormEvent) {
    event.preventDefault();
    if (!pdfFile) return;
    const formData = new FormData();
    formData.append("import_mode", "pdf");
    formData.append("topic_id", topicId);
    formData.append("file", pdfFile);
    importMutation.mutate({ kind: "pdf", formData });
  }

  const topic = topicQuery.data;
  const papers = papersQuery.data ?? [];
  const lastReport = useMemo(() => (reportsQuery.data ?? [])[0], [reportsQuery.data]);

  return (
    <div className="space-y-6">
      <Panel title={topic?.name ?? "Topic Detail"} subtitle={topic?.description ?? "加载中..."}>
        <div className="flex flex-wrap items-center gap-3">
          {(topic?.keywords ?? []).map((keyword) => (
            <span key={keyword} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              {keyword}
            </span>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button className="primary" onClick={() => scanMutation.mutate()}>
            运行扫描 / 追踪
          </button>
          <button className="secondary" onClick={() => weeklyReportMutation.mutate()}>
            生成周报
          </button>
          {lastReport ? (
            <Link to={`/reports/${lastReport.id}`} className="secondary inline-flex items-center justify-center">
              查看最新周报
            </Link>
          ) : null}
        </div>
        {message ? <div className="mt-4 text-sm text-accent">{message}</div> : null}
      </Panel>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel title="导入论文" subtitle="支持样例、手工输入、URL 和 PDF 上传。">
          <div className="space-y-6">
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="mb-2 text-sm font-semibold">导入本地样例</div>
              <div className="flex gap-3">
                <select value={sampleName} onChange={(e) => setSampleName(e.target.value)} className="flex-1">
                  {sampleChoices.map((choice) => (
                    <option key={choice} value={choice}>
                      {choice}
                    </option>
                  ))}
                </select>
                <button className="primary" onClick={importSample}>
                  导入样例
                </button>
              </div>
            </div>

            <form className="space-y-3 rounded-2xl bg-slate-50 p-4" onSubmit={importManual}>
              <div className="text-sm font-semibold">手动输入标题 / 摘要</div>
              <input value={manualTitle} onChange={(e) => setManualTitle(e.target.value)} placeholder="论文标题" required />
              <textarea
                className="min-h-28 w-full"
                value={manualAbstract}
                onChange={(e) => setManualAbstract(e.target.value)}
                placeholder="论文摘要"
              />
              <input
                value={manualAuthors}
                onChange={(e) => setManualAuthors(e.target.value)}
                placeholder="作者，逗号分隔"
              />
              <button className="primary w-full" type="submit">
                导入手工论文
              </button>
            </form>

            <form className="space-y-3 rounded-2xl bg-slate-50 p-4" onSubmit={importUrl}>
              <div className="text-sm font-semibold">导入 URL / arXiv 链接</div>
              <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://..." required />
              <button className="secondary w-full" type="submit">
                导入 URL
              </button>
            </form>

            <form className="space-y-3 rounded-2xl bg-slate-50 p-4" onSubmit={importPdf}>
              <div className="text-sm font-semibold">上传 PDF</div>
              <input type="file" accept=".pdf" onChange={(e: ChangeEvent<HTMLInputElement>) => setPdfFile(e.target.files?.[0] ?? null)} />
              <button className="secondary w-full" type="submit">
                导入 PDF
              </button>
            </form>
          </div>
        </Panel>

        <Panel title="论文列表" subtitle="状态、优先级和标签都保存在数据库中。">
          <div className="overflow-auto">
            <table>
              <thead>
                <tr>
                  <th>标题</th>
                  <th>状态</th>
                  <th>优先级</th>
                  <th>标签</th>
                </tr>
              </thead>
              <tbody>
                {papers.map((paper) => (
                  <tr key={paper.id}>
                    <td>
                      <Link to={`/papers/${paper.id}`} className="font-medium text-accent">
                        {paper.title}
                      </Link>
                    </td>
                    <td>{paper.status}</td>
                    <td>{paper.priority}</td>
                    <td>{paper.tags.join(", ") || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </section>
    </div>
  );
}

