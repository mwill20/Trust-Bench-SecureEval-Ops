import React from "react";

interface PillarScores {
  security?: number;
  ethics?: number;
  fidelity?: number;
  performance?: number;
}

interface ReportListItemProps {
  id: string;
  timestamp: string;
  repository: string;
  verdict: "PASS" | "FAIL" | "PARTIAL" | "PENDING";
  pillars: PillarScores;
  hasHtmlReport: boolean;
  onViewReport: (id: string) => void;
}

const VerdictIcon: React.FC<{ verdict: string }> = ({ verdict }) => {
  switch (verdict) {
    case "PASS":
      return <span className="text-2xl">✅</span>;
    case "FAIL":
      return <span className="text-2xl">❌</span>;
    case "PARTIAL":
      return <span className="text-2xl">⚠️</span>;
    default:
      return <span className="text-2xl">⏳</span>;
  }
};

const PillarBadge: React.FC<{ name: string; score?: number }> = ({
  name,
  score,
}) => {
  if (score === undefined) {
    return null;
  }

  const getColor = (value: number) => {
    if (value >= 0.9) return "bg-green-600/20 text-green-300 border-green-500";
    if (value >= 0.7)
      return "bg-yellow-600/20 text-yellow-300 border-yellow-500";
    if (value >= 0.5)
      return "bg-orange-600/20 text-orange-300 border-orange-500";
    return "bg-red-600/20 text-red-300 border-red-500";
  };

  return (
    <span
      className={`px-2 py-1 rounded text-xs border ${getColor(score)}`}
      title={`${name}: ${score.toFixed(3)}`}
    >
      {name.charAt(0).toUpperCase()}: {score.toFixed(2)}
    </span>
  );
};

const formatTimestamp = (timestamp: string): string => {
  // Handle directory name format (e.g., "run_20250128_143015")
  if (timestamp.startsWith("run_")) {
    const parts = timestamp.split("_");
    if (parts.length >= 3) {
      const date = parts[1]; // "20250128"
      const time = parts[2]; // "143015"

      // Parse date: YYYYMMDD
      const year = date.substring(0, 4);
      const month = date.substring(4, 6);
      const day = date.substring(6, 8);

      // Parse time: HHMMSS
      const hour = time.substring(0, 2);
      const minute = time.substring(2, 4);

      return `${year}-${month}-${day} ${hour}:${minute}`;
    }
  }

  // Handle ISO format
  try {
    const date = new Date(timestamp);
    if (!isNaN(date.getTime())) {
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    }
  } catch {
    // Fall through to default
  }

  // Return as-is if we can't parse
  return timestamp;
};

const truncateRepo = (repo: string, maxLength: number = 40): string => {
  if (repo.length <= maxLength) {
    return repo;
  }

  // Try to show the end of the path (most relevant part)
  const parts = repo.split("/");
  if (parts.length > 1) {
    return "..." + parts.slice(-2).join("/");
  }

  return repo.substring(0, maxLength - 3) + "...";
};

const ReportListItem: React.FC<ReportListItemProps> = ({
  id,
  timestamp,
  repository,
  verdict,
  pillars,
  hasHtmlReport,
  onViewReport,
}) => {
  return (
    <div
      className="bg-gray-800/60 border border-gray-700 rounded-lg p-4 hover:bg-gray-800/80 hover:border-gray-600 transition-all cursor-pointer group"
      onClick={() => onViewReport(id)}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Left side: Icon and metadata */}
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {/* Verdict Icon */}
          <div className="flex-shrink-0 mt-1">
            <VerdictIcon verdict={verdict} />
          </div>

          {/* Report Info */}
          <div className="flex-1 min-w-0">
            {/* Timestamp and Repository */}
            <div className="mb-2">
              <div className="text-sm text-gray-400 mb-1">
                {formatTimestamp(timestamp)}
              </div>
              <div
                className="text-sm font-medium text-gray-200 truncate"
                title={repository}
              >
                {truncateRepo(repository)}
              </div>
            </div>

            {/* Pillar Scores */}
            <div className="flex flex-wrap gap-2">
              <PillarBadge name="Security" score={pillars.security} />
              <PillarBadge name="Ethics" score={pillars.ethics} />
              <PillarBadge name="Fidelity" score={pillars.fidelity} />
              <PillarBadge name="Performance" score={pillars.performance} />
            </div>
          </div>
        </div>

        {/* Right side: View button and status */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          {/* Verdict Badge */}
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              verdict === "PASS"
                ? "bg-green-600/20 text-green-300"
                : verdict === "FAIL"
                ? "bg-red-600/20 text-red-300"
                : verdict === "PARTIAL"
                ? "bg-yellow-600/20 text-yellow-300"
                : "bg-gray-600/20 text-gray-300"
            }`}
          >
            {verdict}
          </span>

          {/* View Report Button */}
          {hasHtmlReport && (
            <button
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium transition-colors group-hover:bg-blue-500"
              onClick={(e) => {
                e.stopPropagation();
                onViewReport(id);
              }}
            >
              View Report →
            </button>
          )}
          {!hasHtmlReport && (
            <span className="text-xs text-gray-500">No HTML report</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportListItem;
