
export enum Status {
  IDLE = 'idle',
  RUNNING = 'running',
  COMPLETE = 'complete',
  FAILED = 'failed',
}

export enum Verdict {
  PENDING = 'PENDING',
  PASS = 'PASS',
  WARN = 'WARN',
  FAIL = 'FAIL',
}

export type AgentName = 'Athena' | 'Aegis' | 'Helios' | 'Eidos';

export interface Agent {
  id: number;
  name: AgentName;
  description: string;
  status: Status;
  skills: string[];
  tools: string[];
}

export interface LogEntry {
  id: number;
  timestamp: string;
  source: string;
  message: string;
  status: Status;
}

export type Sender = AgentName | 'Logos' | 'User';

export interface ChatMessage {
  sender: Sender;
  text: string;
  isThinking?: boolean;
}

export interface PillarVerdict {
  status: 'complete' | 'failed';
  score?: number;
  summary?: string;
}

export type PillarVerdictMap = Partial<Record<AgentName, PillarVerdict>>;

export interface LanguageBreakdown {
  name: string;
  files: number;
  lines: number;
  bytes: number;
}

export interface CodeAnalysisSummary {
  languages: LanguageBreakdown[];
  total_files: number;
  total_bytes: number;
  important_files: string[];
  top_directories: [string, number][];
}

export interface SecurityFinding {
  pattern: string;
  file: string;
  snippet: string;
}

export interface SecurityScanSummary {
  findings: SecurityFinding[];
  count: number;
}

export interface AgentMetricSummary {
  name: string;
  score: number;
  status: string;
  details: string;
}

export interface AgentEvaluationSummary {
  composite: number;
  metrics: AgentMetricSummary[];
  started_at: string;
  completed_at: string;
}

export interface ReportSummary {
  summary: {
    generated_at?: string;
    repository?: string;
    branch?: string;
    composite_score?: number;
    primary_languages?: string[];
    security_findings?: number;
    key_insights?: string[];
    [key: string]: unknown;
  };
  markdown?: string;
  html?: string;
  markdown_path?: string;
  html_path?: string;
}

export interface RepositoryArtifacts {
  analysis?: CodeAnalysisSummary;
  security?: SecurityScanSummary;
  evaluation?: AgentEvaluationSummary;
  report?: ReportSummary;
  [key: string]: unknown;
}

export interface RepositoryJob {
  id: string;
  repo_url: string;
  state: string;
  stage: string;
  progress: number;
  message: string;
  profile?: string | null;
  created_at: string;
  updated_at: string;
  error?: string | null;
  artifacts: RepositoryArtifacts;
  metadata: Record<string, unknown>;
}

