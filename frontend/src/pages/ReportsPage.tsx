import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { MarkdownCard } from "../components/MarkdownCard";
import { Panel } from "../components/Panel";
import { api } from "../lib/api";

export function ReportsPage() {
  const { reportId } = useParams();
  const reportsQuery = useQuery({ queryKey: ["reports"], queryFn: () => api.listReports() });
  const selectedId = reportId ? Number(reportId) : reportsQuery.data?.[0]?.id;
  const reportQuery = useQuery({
    queryKey: ["report", selectedId],
    queryFn: () => api.getReport(selectedId!),
    enabled: !!selectedId,
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
      <Panel title="周报列表" subtitle="可查看完整 Markdown 和适合群消息发送的短摘要。">
        <div className="space-y-3">
          {(reportsQuery.data ?? []).map((report) => (
            <Link
              key={report.id}
              to={`/reports/${report.id}`}
              className={`block rounded-2xl p-4 ${selectedId === report.id ? "bg-accent text-white" : "bg-slate-50"}`}
            >
              <div className="font-semibold">Report #{report.id}</div>
              <div className="mt-2 text-sm opacity-90">{report.summary_text}</div>
            </Link>
          ))}
        </div>
      </Panel>

      <div className="grid gap-6">
        <Panel title="适合群消息发送的摘要" subtitle="可直接复制到群聊或消息入口。">
          <div className="rounded-2xl bg-slate-900 p-5 text-sm text-white">
            {reportQuery.data?.summary_text ?? "暂无摘要"}
          </div>
        </Panel>
        <MarkdownCard title="weekly_report.md" content={reportQuery.data?.content} />
      </div>
    </div>
  );
}

