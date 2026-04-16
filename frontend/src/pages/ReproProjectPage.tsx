import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { MarkdownCard } from "../components/MarkdownCard";
import { Panel } from "../components/Panel";
import { api } from "../lib/api";

const sampleLogs = [
  "missing_dependency.log",
  "cuda_oom.log",
  "path_not_found.log",
  "checkpoint_failed.log",
  "loss_nan.log",
];

export function ReproProjectPage() {
  const { projectId = "" } = useParams();
  const queryClient = useQueryClient();
  const [sampleLog, setSampleLog] = useState(sampleLogs[0]);
  const [uploadedLog, setUploadedLog] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const projectQuery = useQuery({
    queryKey: ["repro-project", projectId],
    queryFn: () => api.getReproProject(projectId),
    enabled: !!projectId,
  });

  const analyzeMutation = useMutation({
    mutationFn: async (mode: "sample" | "upload") => {
      if (mode === "upload" && uploadedLog) {
        const formData = new FormData();
        formData.append("file", uploadedLog);
        return api.analyzeLogForm(projectId, formData);
      }
      return api.analyzeLogJson(projectId, { sample_log_name: sampleLog });
    },
    onSuccess: () => {
      setMessage("LabOps Agent 已完成日志诊断。");
      queryClient.invalidateQueries({ queryKey: ["repro-project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (uploadedLog) {
      analyzeMutation.mutate("upload");
    }
  }

  const project = projectQuery.data;
  const latestLog = useMemo(() => (project?.experiment_logs ?? [])[0], [project?.experiment_logs]);

  return (
    <div className="space-y-6">
      <Panel title={project?.project_name ?? "Repro Project"} subtitle={project?.project_dir ?? "加载中..."}>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl bg-slate-50 p-4 text-sm">
            <div><span className="font-semibold">状态：</span>{project?.status}</div>
            <div><span className="font-semibold">计划：</span>{project?.plan_path}</div>
            <div><span className="font-semibold">脚本：</span>{project?.run_script_path}</div>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 text-sm">
            <div><span className="font-semibold">配置：</span>{project?.config_path}</div>
            <div><span className="font-semibold">TODO：</span>{project?.todo_path}</div>
            <div><span className="font-semibold">Setup：</span>{project?.setup_script_path}</div>
          </div>
        </div>
        {message ? <div className="mt-4 text-sm text-accent">{message}</div> : null}
      </Panel>

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Panel title="日志诊断" subtitle="支持直接选择样例日志或上传本地日志。">
          <div className="space-y-4">
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="mb-2 text-sm font-semibold">选择样例日志</div>
              <div className="flex gap-3">
                <select value={sampleLog} onChange={(e) => setSampleLog(e.target.value)} className="flex-1">
                  {sampleLogs.map((log) => (
                    <option key={log} value={log}>
                      {log}
                    </option>
                  ))}
                </select>
                <button className="primary" onClick={() => analyzeMutation.mutate("sample")}>
                  诊断样例
                </button>
              </div>
            </div>

            <form className="space-y-3 rounded-2xl bg-slate-50 p-4" onSubmit={handleUpload}>
              <div className="text-sm font-semibold">上传日志文件</div>
              <input type="file" accept=".log,.txt" onChange={(e: ChangeEvent<HTMLInputElement>) => setUploadedLog(e.target.files?.[0] ?? null)} />
              <button className="secondary w-full" type="submit">
                上传并诊断
              </button>
            </form>

            {latestLog ? (
              <div className="rounded-2xl bg-slate-900 p-4 text-sm text-white">
                <div className="font-semibold">{latestLog.diagnosis_type}</div>
                <div className="mt-2 opacity-90">{latestLog.root_cause}</div>
                <div className="mt-2 opacity-80">建议：{latestLog.suggestion}</div>
                <div className="mt-2 text-xs opacity-70">置信度：{latestLog.confidence}</div>
              </div>
            ) : (
              <div className="text-sm text-slate-500">还没有诊断记录。</div>
            )}
          </div>
        </Panel>

        <div className="grid gap-6">
          <MarkdownCard title="repro_plan.md" content={project?.generated_contents?.plan} />
          <MarkdownCard title="todo.md" content={project?.generated_contents?.todo} />
          <MarkdownCard title="diagnosis.md" content={latestLog?.diagnosis_content} />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <MarkdownCard title="setup_env.sh" content={`\`\`\`bash\n${project?.generated_contents?.setup ?? ""}\n\`\`\``} />
        <MarkdownCard title="run_baseline.sh / default.yaml" content={`\`\`\`bash\n${project?.generated_contents?.run ?? ""}\n\`\`\`\n\n\`\`\`yaml\n${project?.generated_contents?.config ?? ""}\n\`\`\``} />
      </section>
    </div>
  );
}

