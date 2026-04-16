import type { Assessment, DashboardStats, ExperimentLog, Paper, Report, ReproProject, Topic } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getDashboard: () => request<DashboardStats>("/dashboard"),
  listTopics: () => request<Topic[]>("/topics"),
  getTopic: (id: string | number) => request<Topic>(`/topics/${id}`),
  createTopic: (payload: { name: string; description?: string; keywords: string[] }) =>
    request<Topic>("/topics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  listPapers: (topicId?: string | number) =>
    request<Paper[]>(topicId ? `/papers?topic_id=${topicId}` : "/papers"),
  getPaper: (id: string | number) => request<Paper>(`/papers/${id}`),
  importPaperJson: (payload: Record<string, unknown>) =>
    request<Paper>("/papers/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  importPaperForm: (formData: FormData) =>
    request<Paper>("/papers/import", {
      method: "POST",
      body: formData,
    }),
  assessPaper: (paperId: string | number, payload: { use_llm: boolean; notes?: string }) =>
    request<Assessment>(`/papers/${paperId}/assess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  startRepro: (paperId: string | number) =>
    request<ReproProject>(`/papers/${paperId}/start-repro`, { method: "POST" }),
  getReproProject: (projectId: string | number) => request<ReproProject>(`/repro-projects/${projectId}`),
  analyzeLogJson: (projectId: string | number, payload: { sample_log_name?: string; log_path?: string }) =>
    request<ExperimentLog>(`/repro-projects/${projectId}/analyze-log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  analyzeLogForm: (projectId: string | number, formData: FormData) =>
    request<ExperimentLog>(`/repro-projects/${projectId}/analyze-log`, {
      method: "POST",
      body: formData,
    }),
  listReports: (topicId?: string | number) =>
    request<Report[]>(topicId ? `/reports?topic_id=${topicId}` : "/reports"),
  getReport: (reportId: string | number) => request<Report>(`/reports/${reportId}`),
  generateWeeklyReport: (topicId: string | number) =>
    request<Report>(`/topics/${topicId}/generate-weekly-report`, { method: "POST" }),
  runTopicScan: (topicId: string | number) =>
    request<{ count: number; paper_ids: number[] }>(`/tasks/run-topic-scan/${topicId}`, { method: "POST" }),
};

