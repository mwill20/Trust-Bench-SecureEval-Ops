import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

interface ToolStats {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  last_used: string | null;
}

interface RecentCall {
  tool: string;
  timestamp: string;
  success: boolean;
  response_summary: string | null;
}

interface ActivityData {
  tools: {
    [toolName: string]: ToolStats;
  };
  recent_calls: RecentCall[];
}

const MCPActivityDashboard: React.FC = () => {
  const [data, setData] = useState<ActivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchActivity();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchActivity, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivity = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/api/mcp/activity`);
      if (!response.ok) {
        throw new Error(`Failed to load activity: ${response.statusText}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string | null): string => {
    if (!timestamp) return "Never";
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getToolIcon = (toolName: string): string => {
    const icons: Record<string, string> = {
      cleanup_workspace: "🧹",
      scan_repo_for_secrets: "🔍",
      env_content: "📄",
      prompt_guard: "🛡️",
    };
    return icons[toolName] || "🔧";
  };

  const getToolDescription = (toolName: string): string => {
    const descriptions: Record<string, string> = {
      cleanup_workspace:
        "Archive old evaluation runs and clean temporary files",
      scan_repo_for_secrets:
        "Scan repositories for exposed secrets and credentials",
      env_content: "View environment configuration and settings",
      prompt_guard: "Detect and block prompt injection attempts",
    };
    return descriptions[toolName] || "MCP tool";
  };

  if (loading && !data) {
    return (
      <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="text-gray-400">Loading MCP activity...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800/60 border border-red-700 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-400">
          <span>⚠️</span>
          <span>Error: {error}</span>
        </div>
        <button
          onClick={fetchActivity}
          className="mt-3 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const tools = Object.entries(data.tools);
  const hasActivity = tools.length > 0 || data.recent_calls.length > 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-100">MCP Tool Activity</h3>
        <button
          onClick={fetchActivity}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs font-medium transition-colors"
          disabled={loading}
          title="Refresh activity statistics"
        >
          {loading ? "⏳" : "🔄"} Refresh
        </button>
      </div>

      {/* Tool Statistics Grid */}
      {tools.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools.map(([toolName, statsData]) => {
            const stats = statsData as ToolStats;
            return (
              <div
                key={toolName}
                className="bg-gray-800/60 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition-colors"
                title={getToolDescription(toolName)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-2xl">{getToolIcon(toolName)}</span>
                      <h4 className="text-sm font-semibold text-gray-200">
                        {toolName
                          .replace(/_/g, " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </h4>
                    </div>
                    <p className="text-xs text-gray-400">
                      {getToolDescription(toolName)}
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  {/* Total Calls */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Total Invocations:</span>
                    <span className="font-mono text-gray-100 font-semibold">
                      {stats.total_calls}
                    </span>
                  </div>

                  {/* Success Rate */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Success Rate:</span>
                    <span
                      className={`font-mono font-semibold ${
                        stats.success_rate >= 0.9
                          ? "text-green-400"
                          : stats.success_rate >= 0.7
                          ? "text-yellow-400"
                          : "text-red-400"
                      }`}
                    >
                      {(stats.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>

                  {/* Success/Fail Count */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Success / Fail:</span>
                    <span className="font-mono text-gray-100">
                      <span className="text-green-400">
                        {stats.successful_calls}
                      </span>
                      {" / "}
                      <span className="text-red-400">{stats.failed_calls}</span>
                    </span>
                  </div>

                  {/* Last Used */}
                  <div className="flex justify-between text-xs border-t border-gray-700 pt-2 mt-2">
                    <span className="text-gray-500">Last used:</span>
                    <span className="text-gray-400">
                      {formatTimestamp(stats.last_used)}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-3">
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          stats.success_rate >= 0.9
                            ? "bg-green-500"
                            : stats.success_rate >= 0.7
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                        style={{ width: `${stats.success_rate * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-8 text-center">
          <div className="text-4xl mb-3">🔧</div>
          <p className="text-gray-400 text-lg mb-2">No MCP Tool Activity Yet</p>
          <p className="text-gray-500 text-sm">
            MCP tools will appear here once they've been invoked from the Flow
            tab.
          </p>
        </div>
      )}

      {/* Recent Activity Timeline */}
      {data.recent_calls.length > 0 && (
        <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-5">
          <h4 className="text-lg font-semibold mb-4 text-gray-200">
            Recent Activity
          </h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {data.recent_calls.map((call, index) => (
              <div
                key={`${call.tool}-${call.timestamp}-${index}`}
                className="flex items-start space-x-3 p-3 bg-gray-900/40 rounded border border-gray-700/50 hover:border-gray-600 transition-colors"
              >
                <span className="text-xl flex-shrink-0">
                  {getToolIcon(call.tool)}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-200 truncate">
                      {call.tool.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        call.success
                          ? "bg-green-900/40 text-green-400"
                          : "bg-red-900/40 text-red-400"
                      }`}
                    >
                      {call.success ? "✓ Success" : "✗ Failed"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">
                      {formatTimestamp(call.timestamp)}
                    </span>
                    {call.response_summary && (
                      <span className="text-gray-400 italic truncate ml-2">
                        {call.response_summary}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MCPActivityDashboard;
