import React, { useState, useEffect, useCallback } from "react";
import Sidebar from "./Sidebar";
import FlowLines from "./FlowLines";
import { OrchestratorNode, AgentNode } from "./NodeComponents";
import ReportListItem from "./ReportListItem";
import ReportViewer from "./ReportViewer";
import {
  INITIAL_AGENTS,
  VERDICT_STYLES,
  STATUS_STYLES,
  INITIAL_CHAT_HISTORY,
  AGENT_COLORS,
  ORCHESTRATOR_DATA,
} from "../constants";
import {
  Agent,
  Status,
  Verdict,
  LogEntry,
  AgentName,
  ChatMessage,
  PillarVerdictMap,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

type ActiveTab = "flow" | "reports" | "settings";

type ChatHistories = { [key in AgentName]: ChatMessage[] };

type MCPResponse = { tool: string; response: unknown };

type ReportSnapshot = {
  verdict: unknown;
  run: unknown;
  metrics: unknown;
};

interface ChatWindowProps {
  agent: Agent;
  chatHistory: ChatMessage[];
  onSendMessage: (agentName: AgentName, message: string) => void;
  onClose: (agentName: AgentName) => void;
  initialPosition: { x: number; y: number };
  isThinking: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  agent,
  chatHistory,
  onSendMessage,
  onClose,
  initialPosition,
  isThinking,
}) => {
  const [message, setMessage] = useState("");
  const [position, setPosition] = useState(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = React.useRef({ x: 0, y: 0 });
  const chatContainerRef = React.useRef<HTMLDivElement>(null);
  const headerRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleMouseDown = (event: React.MouseEvent<HTMLDivElement>) => {
    if (headerRef.current && event.target === headerRef.current) {
      setIsDragging(true);
      dragStartPos.current = {
        x: event.clientX - position.x,
        y: event.clientY - position.y,
      };
    }
  };

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (isDragging) {
        setPosition({
          x: event.clientX - dragStartPos.current.x,
          y: event.clientY - dragStartPos.current.y,
        });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging]);

  const getSenderStyles = (sender: AgentName | "Logos" | "User") => {
    const isUser = sender === "User";
    const colorName = AGENT_COLORS[sender] || "gray-400";
    const textColorClass = `text-${colorName}`;

    return {
      wrapper: isUser ? "items-end" : "items-start",
      bubble: isUser ? "bg-blue-600" : "bg-gray-700",
      text: isUser ? "text-white" : "text-gray-200",
      name: isUser ? "font-bold text-blue-300" : `font-bold ${textColorClass}`,
    };
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isThinking) return;
    onSendMessage(agent.name, trimmed);
    setMessage("");
  };

  return (
    <div
      className="absolute bg-gray-900/95 border border-gray-700 rounded-lg w-72 shadow-xl cursor-default z-50 pointer-events-auto"
      style={{ left: position.x, top: position.y }}
    >
      <div
        ref={headerRef}
        onMouseDown={handleMouseDown}
        className="px-4 py-2 bg-gray-800 text-gray-100 font-semibold rounded-t-lg flex justify-between items-center"
      >
        <span>{agent.name} Chat</span>
        <button
          type="button"
          onClick={() => onClose(agent.name)}
          className="text-gray-400 hover:text-gray-200"
        >
          �
        </button>
      </div>
      <div
        ref={chatContainerRef}
        className="h-56 overflow-y-auto px-3 py-2 space-y-3 bg-gray-900/80"
      >
        {chatHistory.map((entry, index) => {
          const styles = getSenderStyles(entry.sender);
          return (
            <div key={index} className={`flex flex-col ${styles.wrapper}`}>
              <span className={styles.name}>{entry.sender}</span>
              <span
                className={`mt-1 px-3 py-2 rounded-lg text-sm ${styles.bubble} ${styles.text}`}
              >
                {entry.isThinking ? "�" : entry.text}
              </span>
            </div>
          );
        })}
      </div>
      <form
        onSubmit={handleSubmit}
        className="p-3 border-t border-gray-700 bg-gray-900"
      >
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          placeholder="Ask a question�"
        />
        <button
          type="submit"
          disabled={isThinking || !message.trim()}
          className="mt-2 w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-sm font-semibold text-white py-1.5 rounded-md transition-colors"
        >
          {isThinking ? "Thinking�" : "Send"}
        </button>
      </form>
    </div>
  );
};

const RightPanel: React.FC<{
  logs: LogEntry[];
  verdict: Verdict;
  pillars: PillarVerdictMap;
}> = ({ logs, verdict, pillars }) => (
  <div className="w-[28rem] h-full bg-gray-800/50 backdrop-blur-sm border-l border-gray-700/50 flex flex-col text-gray-200">
    <div className="flex-grow min-h-0">
      <div className="p-4 border-b border-gray-700 flex-shrink-0">
        <h3 className="font-bold text-lg text-gray-200">System Logs</h3>
      </div>
      <div className="flex-grow p-4 overflow-y-auto">
        <ul className="space-y-2 text-sm">
          {logs
            .slice()
            .reverse()
            .map((log) => (
              <li key={log.id} className="flex items-start">
                <span className="text-gray-500 mr-3 w-16 text-right tabular-nums">
                  {log.timestamp}
                </span>
                <span
                  className={`w-3 h-3 rounded-full mt-1 mr-3 flex-shrink-0 ${
                    STATUS_STYLES[log.status].color
                  }`}
                ></span>
                <span className="text-gray-300">
                  <span
                    className={`font-semibold text-${
                      AGENT_COLORS[log.source] || "gray-400"
                    }`}
                  >
                    {log.source}:{" "}
                  </span>
                  {log.message}
                </span>
              </li>
            ))}
        </ul>
      </div>
    </div>
    <div
      className={`p-4 border-t border-gray-700 ${VERDICT_STYLES[verdict].bg}`}
    >
      <h3 className="font-bold text-lg mb-2">Composite Verdict</h3>
      <div
        className={`px-4 py-2 rounded-lg border-2 ${VERDICT_STYLES[verdict].border} flex items-center justify-center`}
      >
        <span
          className={`text-2xl font-black tracking-widest ${VERDICT_STYLES[verdict].text}`}
        >
          {verdict}
        </span>
      </div>
      <div className="mt-4 space-y-2 text-sm text-gray-300">
        {(Object.entries(pillars || {}) as [string, any][]).map(
          ([name, pillar]) => (
            <div
              key={name}
              className="flex justify-between bg-gray-900/60 rounded-md px-3 py-2"
            >
              <span
                className={`font-semibold text-${
                  AGENT_COLORS[name] || "gray-300"
                }`}
              >
                {name}
              </span>
              <span
                className={
                  pillar?.status === "failed"
                    ? "text-red-400"
                    : "text-green-400"
                }
              >
                {pillar?.status ?? "complete"}
              </span>
            </div>
          )
        )}
      </div>
    </div>
  </div>
);

const ReportsPanel: React.FC<{
  lastReport: ReportSnapshot | null;
  lastCleanup: MCPResponse | null;
}> = ({ lastReport, lastCleanup }) => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/api/reports/list`);
      if (!response.ok) {
        throw new Error(`Failed to fetch reports: ${response.statusText}`);
      }
      const data = await response.json();
      setReports(data.reports || []);
    } catch (err) {
      console.error("Error fetching reports:", err);
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = (reportId: string) => {
    setSelectedReportId(reportId);
  };

  const handleCloseViewer = () => {
    setSelectedReportId(null);
  };

  // Show report viewer if a report is selected
  if (selectedReportId) {
    return (
      <ReportViewer reportId={selectedReportId} onClose={handleCloseViewer} />
    );
  }

  // Otherwise show the report list
  return (
    <div className="flex-1 bg-gray-900 text-gray-200 p-8 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Reports & History</h2>
        <button
          onClick={fetchReports}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors"
          disabled={loading}
        >
          {loading ? "Loading..." : "🔄 Refresh"}
        </button>
      </div>

      <div className="space-y-6">
        {/* Report History Section */}
        <section>
          <h3 className="text-lg font-semibold mb-4">Evaluation History</h3>

          {loading && (
            <div className="text-center py-8 text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <p className="mt-2">Loading reports...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-600/20 border border-red-500 rounded-lg p-4 text-red-300">
              <p className="font-semibold">Error loading reports</p>
              <p className="text-sm mt-1">{error}</p>
              <button
                onClick={fetchReports}
                className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-500 rounded text-sm"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && reports.length === 0 && (
            <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-8 text-center">
              <p className="text-gray-400 text-lg mb-2">
                No evaluation reports found
              </p>
              <p className="text-gray-500 text-sm">
                Run an evaluation from the Flow tab to generate reports.
              </p>
            </div>
          )}

          {!loading && !error && reports.length > 0 && (
            <div className="space-y-3">
              {reports.map((report) => (
                <ReportListItem
                  key={report.id}
                  id={report.id}
                  timestamp={report.timestamp}
                  repository={report.repository}
                  verdict={report.verdict}
                  pillars={report.pillars}
                  hasHtmlReport={report.hasHtmlReport}
                  onViewReport={handleViewReport}
                />
              ))}
            </div>
          )}
        </section>

        {/* MCP Activity Section */}
        <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-2">Last MCP Cleanup</h3>
          {lastCleanup ? (
            <pre className="bg-gray-900/80 border border-gray-700 rounded-md p-4 text-sm overflow-x-auto">
              {JSON.stringify(lastCleanup, null, 2)}
            </pre>
          ) : (
            <p className="text-gray-400">
              No cleanup actions have been executed yet.
            </p>
          )}
        </section>
      </div>
    </div>
  );
};

const SettingsPanel: React.FC = () => (
  <div className="flex-1 bg-gray-900 text-gray-200 p-8 overflow-y-auto space-y-6">
    <h2 className="text-2xl font-bold">Settings</h2>
    <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-5">
      <h3 className="text-lg font-semibold mb-2">Environment</h3>
      <p className="text-sm text-gray-300">
        The frontend expects{" "}
        <code className="text-blue-300">VITE_API_BASE</code> (defaulting to
        http://127.0.0.1:8000) for API communication. LLM providers are
        configured server-side via{" "}
        <code className="text-blue-300">TRUST_BENCH_LLM_PROVIDER</code>,
        <code className="text-blue-300">GROQ_API_KEY</code>, and{" "}
        <code className="text-blue-300">OPENAI_API_KEY</code>.
      </p>
    </section>
    <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-5">
      <h3 className="text-lg font-semibold mb-2">Security Guardrails</h3>
      <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
        <li>
          User inputs are length-capped and sanitized before being forwarded.
        </li>
        <li>
          Agent transcripts and findings are rendered in escaped blocks to
          prevent HTML injection.
        </li>
        <li>MCP endpoints are allow-listed and enforce argument caps.</li>
      </ul>
    </section>
  </div>
);

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>("flow");
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [orchestratorStatus, setOrchestratorStatus] = useState<Status>(
    Status.IDLE
  );
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [verdict, setVerdict] = useState<Verdict>(Verdict.PENDING);
  const [pillars, setPillars] = useState<PillarVerdictMap>({});
  const [openChats, setOpenChats] = useState<AgentName[]>([]);
  const [chatHistories, setChatHistories] =
    useState<ChatHistories>(INITIAL_CHAT_HISTORY);
  const [thinkingAgents, setThinkingAgents] = useState<AgentName[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [flowInput, setFlowInput] = useState("");
  const [lastReport, setLastReport] = useState<ReportSnapshot | null>(null);
  const [lastCleanup, setLastCleanup] = useState<MCPResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const addLog = useCallback(
    (source: string, message: string, status: Status) => {
      setLogs((prev) => [
        ...prev,
        {
          id: Date.now() + Math.random(),
          timestamp: new Date().toISOString().slice(11, 19),
          source,
          message,
          status,
        },
      ]);
    },
    []
  );

  const addChatMessage = useCallback(
    (agentName: AgentName, message: ChatMessage) => {
      setChatHistories((prev) => ({
        ...prev,
        [agentName]: [...(prev[agentName] || []), message],
      }));
    },
    []
  );

  const replaceLastChatMessage = useCallback(
    (agentName: AgentName, message: ChatMessage) => {
      setChatHistories((prev) => {
        const history = prev[agentName] || [];
        if (history.length === 0) {
          return { ...prev, [agentName]: [message] };
        }
        const nextHistory = [...history];
        nextHistory[nextHistory.length - 1] = message;
        return { ...prev, [agentName]: nextHistory };
      });
    },
    []
  );

  const sanitizeInput = useCallback(async (text: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/input/sanitize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        return text.trim();
      }
      const data = await response.json();
      return data.text || text.trim();
    } catch {
      return text.trim();
    }
  }, []);

  const loadManifest = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents`);
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      const manifestAgents = data.agents || [];
      setAgents((prev) =>
        prev.map((agent) => {
          const manifestEntry = manifestAgents.find(
            (entry: any) => entry.name === agent.name
          );
          if (!manifestEntry) return agent;
          return {
            ...agent,
            description: manifestEntry.description || agent.description,
            skills: manifestEntry.skills || agent.skills,
            tools: manifestEntry.tools || agent.tools,
          };
        })
      );
    } catch {
      // Ignore manifest errors for now
    }
  }, []);

  const loadInitialVerdict = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/verdict`);
      if (!response.ok) return;
      const data = await response.json();
      const payload = data.verdict || {};
      setVerdict((payload.decision || "PENDING").toUpperCase() as Verdict);
      setPillars(payload.pillars || {});
    } catch {
      // Best-effort
    }
  }, []);

  useEffect(() => {
    loadManifest();
    loadInitialVerdict();
  }, [loadManifest, loadInitialVerdict]);

  const applyPillarsToState = useCallback((pillarMap: PillarVerdictMap) => {
    setAgents((prev) =>
      prev.map((agent) => {
        const pillar = pillarMap[agent.name];
        if (!pillar) return agent;
        return {
          ...agent,
          status: pillar.status === "failed" ? Status.FAILED : Status.COMPLETE,
        };
      })
    );

    setLogs(
      Object.entries(pillarMap || {}).map(([name, pillar], index) => ({
        id: Date.now() + index,
        timestamp: new Date().toISOString().slice(11, 19),
        source: name,
        message: pillar?.summary || "Analysis complete.",
        status: pillar?.status === "failed" ? Status.FAILED : Status.COMPLETE,
      }))
    );

    setChatHistories((prev) => {
      const next = { ...prev } as ChatHistories;
      (Object.keys(pillarMap) as AgentName[]).forEach((agentName) => {
        const pillar = pillarMap[agentName];
        if (!pillar) return;
        next[agentName] = [
          ...(next[agentName] || []),
          {
            sender: agentName,
            text: pillar.summary || "Analysis summary not available.",
          },
        ];
      });
      return next;
    });
  }, []);

  const handleStartAnalysis = useCallback(async () => {
    setErrorMessage(null);
    setIsProcessing(true);
    setOpenChats([]);
    setOrchestratorStatus(Status.RUNNING);
    setAgents((prev) =>
      prev.map((agent) => ({ ...agent, status: Status.RUNNING }))
    );
    addLog("Logos", "Dispatching agents for latest run.", Status.RUNNING);

    try {
      const sanitizedInput = await sanitizeInput(flowInput);
      if (sanitizedInput) {
        addLog("User", `Input queued: ${sanitizedInput}`, Status.RUNNING);
      }

      const [runRes, verdictRes] = await Promise.all([
        fetch(`${API_BASE}/api/run/latest`),
        fetch(`${API_BASE}/api/verdict`),
      ]);

      if (!runRes.ok) {
        throw new Error(await runRes.text());
      }
      if (!verdictRes.ok) {
        throw new Error(await verdictRes.text());
      }

      const runPayload = await runRes.json();
      const verdictPayload = await verdictRes.json();
      const verdictData = verdictPayload.verdict || {};

      setVerdict((verdictData.decision || "PENDING").toUpperCase() as Verdict);
      setPillars(verdictData.pillars || {});
      setLastReport({
        verdict: verdictData,
        run: runPayload.run,
        metrics: runPayload.summary?.metrics,
      });

      applyPillarsToState(verdictData.pillars || {});
      setOrchestratorStatus(Status.COMPLETE);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unexpected error while loading run data.";
      setErrorMessage(message);
      addLog("Logos", `Analysis failed: ${message}`, Status.FAILED);
      setOrchestratorStatus(Status.FAILED);
    } finally {
      setIsProcessing(false);
    }
  }, [addLog, applyPillarsToState, flowInput, sanitizeInput]);

  const handleOpenChat = (agent: Agent) => {
    if (agent.status === Status.IDLE || agent.status === Status.RUNNING) return;
    setOpenChats((prev) => [...new Set([...prev, agent.name])]);
  };

  const handleCloseChat = (agentName: AgentName) => {
    setOpenChats((prev) => prev.filter((name) => name !== agentName));
  };

  const handleSendMessage = async (agentName: AgentName, text: string) => {
    addChatMessage(agentName, { sender: "User", text });
    setThinkingAgents((prev) => [...prev, agentName]);
    addChatMessage(agentName, {
      sender: agentName,
      text: "",
      isThinking: true,
    });

    try {
      const response = await fetch(`${API_BASE}/api/chat/agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent: agentName, question: text }),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      replaceLastChatMessage(agentName, {
        sender: agentName,
        text: data.answer || "Response unavailable.",
      });
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unable to process chat request.";
      replaceLastChatMessage(agentName, {
        sender: agentName,
        text: message,
      });
    } finally {
      setThinkingAgents((prev) => prev.filter((name) => name !== agentName));
    }
  };

  const handleCleanupWorkspace = async () => {
    if (
      !confirm(
        "Archive old evaluation runs and clean up temporary files?\n\nThis will keep the 10 most recent runs and the baseline."
      )
    ) {
      return;
    }

    try {
      addLog("Aegis", "Starting workspace cleanup...", Status.RUNNING);

      const response = await fetch(`${API_BASE}/api/workspace/cleanup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const payload = await response.json();
      setLastCleanup(payload);
      addLog(
        "Aegis",
        `Workspace cleanup complete! ${payload.message || ""}`,
        Status.COMPLETE
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Cleanup failed.";
      addLog("Aegis", `Cleanup failed: ${message}`, Status.FAILED);
    }
  };

  const handlePromoteBaseline = async () => {
    if (
      !confirm(
        "Save the current evaluation as the golden standard baseline?\n\nFuture runs will compare against this baseline."
      )
    ) {
      return;
    }

    try {
      addLog(
        "Logos",
        "Promoting current evaluation to baseline...",
        Status.RUNNING
      );

      const note = `auto | decision=${verdict}`;
      const response = await fetch(`${API_BASE}/api/baseline/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ note }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const payload = await response.json();
      addLog("Logos", "✅ Baseline promoted successfully!", Status.COMPLETE);
      setLastReport((prev) => ({ ...(prev || {}), baseline: payload }));
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Baseline promotion failed.";
      addLog("Logos", `Baseline promotion failed: ${message}`, Status.FAILED);
    }
  };

  const handleGenerateReport = async () => {
    try {
      addLog("Logos", "Generating evaluation report...", Status.RUNNING);

      const response = await fetch(`${API_BASE}/api/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const payload = await response.json();

      const report = {
        createdAt: new Date().toISOString(),
        verdict,
        pillars,
        reportData: payload,
      };
      setLastReport(report);

      addLog(
        "Logos",
        `✅ Report generated successfully! ${
          payload.message || "Check trustbench_core/eval/runs/latest/report.md"
        }`,
        Status.COMPLETE
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Report generation failed.";
      addLog("Logos", `Report generation failed: ${message}`, Status.FAILED);
    }
  };

  return (
    <div className="dark">
      <div className="h-screen w-screen flex bg-gray-900 text-gray-100 font-sans overflow-hidden">
        <Sidebar activeTab={activeTab} onSelect={setActiveTab} />
        <main className="flex-1 flex flex-col min-w-0 relative">
          {activeTab === "flow" && (
            <>
              <header className="p-4 border-b border-gray-800 flex justify-between items-center flex-shrink-0 z-10">
                <div className="flex-1">
                  <input
                    id="task-input-field"
                    type="text"
                    placeholder="Enter task instructions or repository URL�"
                    className="w-full max-w-lg bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    value={flowInput}
                    onChange={(event) => setFlowInput(event.target.value)}
                    disabled={isProcessing}
                  />
                </div>
                <button
                  onClick={handleStartAnalysis}
                  disabled={isProcessing}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center"
                >
                  {isProcessing && (
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  )}
                  {isProcessing ? "Analyzing�" : "Start Analysis"}
                </button>
              </header>

              {errorMessage && (
                <div className="px-4 py-2 bg-red-900/60 border-b border-red-700 text-sm">
                  {errorMessage}
                </div>
              )}

              <div className="flex-1 flex overflow-hidden">
                <div
                  id="flow-container"
                  className="flex-1 relative p-8 flex flex-col items-center justify-start"
                >
                  <FlowLines
                    orchestratorStatus={orchestratorStatus}
                    agentStatuses={agents.map((agent) => agent.status)}
                  />
                  <div className="mt-8">
                    <OrchestratorNode
                      status={orchestratorStatus}
                      data={ORCHESTRATOR_DATA}
                    />
                  </div>
                  <div className="flex justify-around w-full max-w-5xl mt-24">
                    {agents.map((agent) => (
                      <AgentNode
                        key={agent.id}
                        agent={agent}
                        onSelect={handleOpenChat}
                      />
                    ))}
                  </div>
                  <div className="flex-grow"></div>
                </div>

                <RightPanel logs={logs} verdict={verdict} pillars={pillars} />
              </div>

              <footer className="p-3 border-t border-gray-800 bg-gray-900/50 flex justify-end items-center space-x-4 flex-shrink-0 z-10">
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
                  onClick={handleGenerateReport}
                  title="📊 Generate a comprehensive PDF/HTML report with all metrics, charts, and recommendations from the latest evaluation run. Perfect for sharing with stakeholders or documenting system performance."
                >
                  Generate Report
                </button>
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-green-600 hover:bg-green-500 rounded-md transition-colors"
                  onClick={handleCleanupWorkspace}
                  title="🧹 Archive old evaluation runs and clean up temporary files to free disk space. Keeps the 10 most recent runs and the current baseline. Safe operation with confirmation dialog."
                >
                  Cleanup Workspace
                </button>
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 rounded-md transition-colors"
                  onClick={handlePromoteBaseline}
                  title="⭐ Save the current evaluation as the golden standard baseline. Future runs will compare against this baseline to detect performance regressions or improvements. Use this after a successful evaluation."
                >
                  Promote to Baseline
                </button>
              </footer>

              <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-50">
                {openChats.map((agentName, index) => {
                  const agent = agents.find(
                    (entry) => entry.name === agentName
                  );
                  if (!agent) return null;

                  // Position chat window relative to the specific agent card
                  const calculateInitialPosition = () => {
                    const agentElement = document.getElementById(
                      `agent-${agent.id}`
                    );
                    if (agentElement) {
                      const rect = agentElement.getBoundingClientRect();
                      const flowContainer =
                        document.getElementById("flow-container");
                      const containerRect =
                        flowContainer?.getBoundingClientRect() || {
                          left: 0,
                          top: 0,
                        };
                      // Position relative to the flow container
                      return {
                        x: rect.left - containerRect.left,
                        y: rect.bottom - containerRect.top + 10, // 10px below the card
                      };
                    }
                    // Fallback positioning
                    return { x: 50 + index * 60, y: 400 + index * 40 };
                  };

                  return (
                    <ChatWindow
                      key={agent.id}
                      agent={agent}
                      chatHistory={chatHistories[agent.name] || []}
                      onSendMessage={handleSendMessage}
                      onClose={handleCloseChat}
                      initialPosition={calculateInitialPosition()}
                      isThinking={thinkingAgents.includes(agent.name)}
                    />
                  );
                })}
              </div>
            </>
          )}

          {activeTab === "reports" && (
            <ReportsPanel lastReport={lastReport} lastCleanup={lastCleanup} />
          )}
          {activeTab === "settings" && <SettingsPanel />}
        </main>
      </div>
    </div>
  );
};

export default App;
