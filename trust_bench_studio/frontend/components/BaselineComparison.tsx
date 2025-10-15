import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

interface PillarScores {
  security?: number;
  ethics?: number;
  fidelity?: number;
  performance?: number;
}

interface RunData {
  id: string;
  timestamp: string;
  pillars: PillarScores;
  verdict: string;
}

interface ComparisonData {
  current: RunData;
  baseline: RunData | null;
  deltas: {
    [key: string]: number | null;
  };
}

interface BaselineComparisonProps {
  onPromoteToBaseline?: () => void;
}

const BaselineComparison: React.FC<BaselineComparisonProps> = ({
  onPromoteToBaseline,
}) => {
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComparison();
  }, []);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/api/baseline/comparison`);
      if (!response.ok) {
        throw new Error(`Failed to load comparison: ${response.statusText}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    // Handle epoch timestamps
    if (/^\d+(\.\d+)?$/.test(timestamp)) {
      const date = new Date(parseFloat(timestamp) * 1000);
      return date.toLocaleString();
    }

    // Handle "2025:10:15 01:52:20" or "2025-10-15 01-52-20" formats
    const cleaned = timestamp.replace(/:/g, "-");
    const parts = cleaned.match(
      /(\d{4})-(\d{2})-(\d{2})[_\s]?(\d{2})-(\d{2})-(\d{2})/
    );
    if (parts) {
      const [, year, month, day, hour, minute, second] = parts;
      const date = new Date(
        `${year}-${month}-${day}T${hour}:${minute}:${second}`
      );
      if (!isNaN(date.getTime())) {
        return date.toLocaleString();
      }
    }

    // Fallback: just clean it up for display
    return timestamp.replace(/_/g, " ").replace(/:/g, "-");
  };

  const formatScore = (score: number | undefined): string => {
    if (score === undefined) return "N/A";
    return (score * 100).toFixed(1) + "%";
  };

  const getDeltaIndicator = (delta: number | null): React.ReactNode => {
    if (delta === null || delta === 0) {
      return <span className="text-gray-400">→ 0.0%</span>;
    }
    if (delta > 0) {
      return (
        <span className="text-green-400 font-semibold">
          ↑ +{(delta * 100).toFixed(1)}%
        </span>
      );
    }
    return (
      <span className="text-red-400 font-semibold">
        ↓ {(delta * 100).toFixed(1)}%
      </span>
    );
  };

  const getVerdictColor = (verdict: string): string => {
    switch (verdict) {
      case "PASS":
        return "text-green-400";
      case "FAIL":
        return "text-red-400";
      case "PARTIAL":
        return "text-yellow-400";
      default:
        return "text-gray-400";
    }
  };

  const getVerdictIcon = (verdict: string): string => {
    switch (verdict) {
      case "PASS":
        return "✅";
      case "FAIL":
        return "❌";
      case "PARTIAL":
        return "⚠️";
      default:
        return "❓";
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="text-gray-400">Loading comparison...</span>
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
          onClick={fetchComparison}
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

  const pillars = ["security", "ethics", "fidelity", "performance"] as const;

  return (
    <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-100">Baseline Comparison</h3>
        {onPromoteToBaseline && (
          <button
            onClick={onPromoteToBaseline}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm font-medium transition-colors"
            title="⭐ Promote the current evaluation run to become the new baseline. Future evaluations will be compared against this baseline to detect performance improvements or regressions."
          >
            Update Baseline
          </button>
        )}
      </div>

      {/* Overall Verdict Comparison */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900/60 border border-gray-600 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">Current Run</div>
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-2xl">
              {getVerdictIcon(data.current.verdict)}
            </span>
            <span
              className={`text-2xl font-bold ${getVerdictColor(
                data.current.verdict
              )}`}
            >
              {data.current.verdict}
            </span>
          </div>
          <div className="text-xs text-gray-500">
            {formatTimestamp(data.current.timestamp)}
          </div>
        </div>

        <div className="bg-gray-900/60 border border-gray-600 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">Baseline</div>
          {data.baseline ? (
            <>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">
                  {getVerdictIcon(data.baseline.verdict)}
                </span>
                <span
                  className={`text-2xl font-bold ${getVerdictColor(
                    data.baseline.verdict
                  )}`}
                >
                  {data.baseline.verdict}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                {formatTimestamp(data.baseline.timestamp)}
              </div>
            </>
          ) : (
            <div className="text-gray-500 italic">No baseline set</div>
          )}
        </div>
      </div>

      {/* Pillar Metrics Comparison */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
          Pillar Metrics
        </h4>
        {pillars.map((pillar) => {
          const currentScore = data.current.pillars[pillar];
          const baselineScore = data.baseline?.pillars[pillar];
          const delta = data.deltas[pillar];

          const pillarDescriptions: Record<string, string> = {
            security:
              "Measures protection against injection attacks, secret exposure, and code vulnerabilities",
            ethics:
              "Evaluates refusal of harmful requests and adherence to ethical guidelines",
            fidelity:
              "Assesses accuracy and faithfulness of responses to source material",
            performance: "Tracks response latency and system efficiency",
          };

          return (
            <div
              key={pillar}
              className="bg-gray-900/40 border border-gray-600/50 rounded-lg p-4"
              title={pillarDescriptions[pillar]}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-200 capitalize">
                  {pillar}
                </span>
                {delta !== undefined && getDeltaIndicator(delta)}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Current: </span>
                  <span className="font-mono text-gray-100">
                    {formatScore(currentScore)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Baseline: </span>
                  <span className="font-mono text-gray-100">
                    {baselineScore !== undefined
                      ? formatScore(baselineScore)
                      : "N/A"}
                  </span>
                </div>
              </div>

              {/* Progress bar visualization */}
              {currentScore !== undefined && (
                <div className="mt-3">
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        currentScore >= 0.7
                          ? "bg-green-500"
                          : currentScore >= 0.5
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${currentScore * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!data.baseline && (
        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-blue-400 mt-0.5">ℹ️</span>
            <div className="text-sm text-blue-300">
              <strong>No baseline set.</strong> Promote the current run to
              establish a baseline for future comparisons.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BaselineComparison;
