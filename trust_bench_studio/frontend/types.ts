
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

