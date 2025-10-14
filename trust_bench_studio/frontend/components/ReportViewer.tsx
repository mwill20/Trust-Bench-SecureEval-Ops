import React, { useState, useEffect } from "react";

interface ReportViewerProps {
  reportId: string;
  onClose: () => void;
}

interface ReportMetadata {
  id: string;
  timestamp: string;
  repository: string;
  verdict: "PASS" | "FAIL" | "PARTIAL" | "PENDING";
}

const ReportViewer: React.FC<ReportViewerProps> = ({ reportId, onClose }) => {
  const [html, setHtml] = useState<string>("");
  const [metadata, setMetadata] = useState<ReportMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);

      const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE}/api/reports/view/${reportId}`);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          errorText || `Failed to load report: ${response.statusText}`
        );
      }

      const data = await response.json();
      setHtml(data.html || "");
      setMetadata(data.metadata || null);
    } catch (err) {
      console.error("Error fetching report:", err);
      setError(err instanceof Error ? err.message : "Failed to load report");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!html) return;

    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${reportId}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getVerdictColor = (verdict: string) => {
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

  return (
    <div className="flex-1 flex flex-col bg-gray-900 text-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 bg-gray-800/60 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              ← Back to List
            </button>

            {metadata && (
              <div className="flex items-center gap-4">
                <div>
                  <span className="text-sm text-gray-400">Report ID:</span>
                  <span className="ml-2 text-sm font-medium">
                    {metadata.id}
                  </span>
                </div>
                <div className="h-4 w-px bg-gray-700"></div>
                <div>
                  <span className="text-sm text-gray-400">Repository:</span>
                  <span className="ml-2 text-sm font-medium">
                    {metadata.repository}
                  </span>
                </div>
                <div className="h-4 w-px bg-gray-700"></div>
                <div>
                  <span className="text-sm text-gray-400">Verdict:</span>
                  <span
                    className={`ml-2 text-sm font-bold ${getVerdictColor(
                      metadata.verdict
                    )}`}
                  >
                    {metadata.verdict}
                  </span>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleDownload}
            disabled={!html}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2"
          >
            📥 Download HTML
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-4">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
              <p className="text-gray-400">Loading report...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="max-w-md">
              <div className="bg-red-600/20 border border-red-500 rounded-lg p-6">
                <p className="font-semibold text-red-300 text-lg mb-2">
                  Failed to Load Report
                </p>
                <p className="text-sm text-red-200 mb-4">{error}</p>
                <div className="flex gap-3">
                  <button
                    onClick={fetchReport}
                    className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded text-sm"
                  >
                    Retry
                  </button>
                  <button
                    onClick={onClose}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded text-sm"
                  >
                    Back to List
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && html && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Render HTML content safely using iframe */}
            <iframe
              srcDoc={html}
              className="w-full border-0"
              style={{ minHeight: "800px", height: "calc(100vh - 200px)" }}
              sandbox="allow-same-origin"
              title="Report Viewer"
            />
          </div>
        )}

        {!loading && !error && !html && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400">
              <p className="text-lg mb-2">No report content available</p>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
              >
                Back to List
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportViewer;
