export type Topic = {
  id: number;
  name: string;
  description: string | null;
  keywords: string[];
  created_at: string;
  updated_at: string;
  paper_count?: number;
  report_count?: number;
};

export type Assessment = {
  id: number;
  paper_id: number;
  novelty_summary: string;
  task_definition: string;
  method_summary: string;
  datasets: string[];
  metrics: string[];
  dependencies: string[];
  difficulty: string;
  recommendation: string;
  risks: string[];
  applicable_scenarios: string[];
  structured_json: Record<string, unknown>;
  markdown_path: string;
  json_path: string;
  markdown_content?: string | null;
};

export type ExperimentLog = {
  id: number;
  repro_project_id: number;
  log_path: string;
  diagnosis_type: string;
  root_cause: string;
  suggestion: string;
  confidence: number;
  diagnosis_path: string;
  diagnosis_content?: string | null;
};

export type ReproProject = {
  id: number;
  paper_id: number;
  project_name: string;
  project_dir: string;
  plan_path: string;
  todo_path: string;
  setup_script_path: string;
  run_script_path: string;
  config_path: string;
  status: string;
  created_at: string;
  updated_at: string;
  generated_files?: Record<string, string>;
  generated_contents?: Record<string, string>;
  experiment_logs?: ExperimentLog[];
};

export type Paper = {
  id: number;
  topic_id: number;
  title: string;
  authors: string[];
  abstract: string | null;
  source_url: string | null;
  pdf_path: string | null;
  published_at: string | null;
  status: string;
  priority: number;
  tags: string[];
  import_source: string;
  created_at: string;
  updated_at: string;
  assessment_id?: number | null;
  repro_project_ids?: number[];
  assessment?: Assessment | null;
  repro_projects?: ReproProject[];
};

export type Report = {
  id: number;
  topic_id: number;
  report_type: string;
  report_path: string;
  summary_text: string;
  content?: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardStats = {
  topic_count: number;
  new_papers_this_week: number;
  assessed_papers: number;
  repro_active: number;
  blocked_count: number;
  recent_reports: Array<{ id: number; topic_id: number; report_path: string; summary_text: string }>;
};

