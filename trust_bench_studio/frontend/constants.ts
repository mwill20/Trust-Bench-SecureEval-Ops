// FIX: Import the 'Verdict' enum from './types' to resolve 'Cannot find name' errors.
import { Agent, Status, Verdict, AgentName, ChatMessage } from "./types";

export const ORCHESTRATOR_DATA = {
  name: "Logos",
  skills: [
    "Agent Coordination",
    "Task Delegation",
    "Result Synthesis",
    "Workflow Management",
  ],
  tools: ["DAG Runner", "State Machine", "API Gateway", "Job Queue"],
};

export const INITIAL_AGENTS: Agent[] = [
  {
    id: 1,
    name: "Athena",
    description: "🎯 Task Fidelity",
    status: Status.IDLE,
    skills: ["Accuracy & Faithfulness", "Response Quality", "Task Completion"],
    tools: ["RAGAS", "Retrieval Accuracy", "Logic Validation"],
  },
  {
    id: 2,
    name: "Aegis",
    description: "🛡️ Security Evaluation",
    status: Status.IDLE,
    skills: [
      "Vulnerability Scanning",
      "Injection Detection",
      "Secrets Exposure",
    ],
    tools: ["PromptGuard", "Semgrep", "Gitleaks"],
  },
  {
    id: 3,
    name: "Helios",
    description: "⚡ System Performance",
    status: Status.IDLE,
    skills: ["Latency Tracking", "Throughput Analysis", "Resource Usage"],
    tools: ["Prometheus", "Performance Metrics", "Profiler"],
  },
  {
    id: 4,
    name: "Eidos",
    description: "⚖️ Ethics & Refusal",
    status: Status.IDLE,
    skills: ["Harmful Request Handling", "Refusal Accuracy", "Bias Detection"],
    tools: ["LLM Judge", "Refusal Rubric", "Safety Checks"],
  },
];

export const INITIAL_CHAT_HISTORY: { [key in AgentName]: ChatMessage[] } = {
  Athena: [],
  Aegis: [],
  Helios: [],
  Eidos: [],
};

export const AGENT_COLORS: { [key: string]: string } = {
  Athena: "brand-athena",
  Aegis: "brand-aegis",
  Helios: "brand-helios",
  Eidos: "brand-eidos",
  Logos: "brand-logos",
};

export const STATUS_STYLES: {
  [key in Status]: { color: string; ring: string; text: string };
} = {
  [Status.IDLE]: {
    color: "bg-status-idle",
    ring: "ring-status-idle",
    text: "text-gray-300",
  },
  [Status.RUNNING]: {
    color: "bg-status-running",
    ring: "ring-status-running animate-pulse",
    text: "text-blue-300",
  },
  [Status.COMPLETE]: {
    color: "bg-status-complete",
    ring: "ring-status-complete",
    text: "text-green-300",
  },
  [Status.FAILED]: {
    color: "bg-status-failed",
    ring: "ring-status-failed",
    text: "text-red-400",
  },
};

export const VERDICT_STYLES: {
  [key in Verdict]: { bg: string; text: string; border: string };
} = {
  [Verdict.PENDING]: {
    bg: "bg-gray-700",
    text: "text-gray-300",
    border: "border-gray-600",
  },
  [Verdict.PASS]: {
    bg: "bg-verdict-pass/20",
    text: "text-verdict-pass",
    border: "border-verdict-pass",
  },
  [Verdict.WARN]: {
    bg: "bg-verdict-warn/20",
    text: "text-verdict-warn",
    border: "border-verdict-warn",
  },
  [Verdict.FAIL]: {
    bg: "bg-verdict-fail/20",
    text: "text-verdict-fail",
    border: "border-verdict-fail",
  },
};
