import React, { useState, useEffect } from "react";

interface SystemStatusProps {
  apiBase: string;
}

interface HealthStatus {
  status: string;
  timestamp: string;
  uptime_seconds: number;
  version: string;
}

interface EnvironmentStatus {
  python_version: string;
  python_path: string;
  working_directory: string;
  platform: string;
  env_vars: {
    [key: string]: string | boolean;
  };
}

interface ServiceStatus {
  name: string;
  status: "running" | "stopped" | "error";
  description: string;
  icon: string;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ apiBase }) => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [environment, setEnvironment] = useState<EnvironmentStatus | null>(
    null
  );
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadSystemStatus();

    if (autoRefresh) {
      const interval = setInterval(() => {
        loadSystemStatus();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadSystemStatus = async () => {
    try {
      // Load health status
      const healthResponse = await fetch(`${apiBase}/api/health`);
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setHealth(healthData);
      }

      // Load environment status
      const envResponse = await fetch(`${apiBase}/api/system/environment`);
      if (envResponse.ok) {
        const envData = await envResponse.json();
        setEnvironment(envData);
      }

      // Load service status
      const servicesResponse = await fetch(`${apiBase}/api/system/services`);
      if (servicesResponse.ok) {
        const servicesData = await servicesResponse.json();
        setServices(servicesData.services || []);
      }

      setLastRefresh(new Date());
    } catch (error) {
      console.error("Failed to load system status:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case "running":
      case "ok":
      case "healthy":
        return "text-green-400 bg-green-900/40 border-green-700";
      case "stopped":
      case "warning":
        return "text-yellow-400 bg-yellow-900/40 border-yellow-700";
      case "error":
      case "unhealthy":
        return "text-red-400 bg-red-900/40 border-red-700";
      default:
        return "text-gray-400 bg-gray-900/40 border-gray-700";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⟳</div>
          <div className="text-gray-400">Loading system status...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">System Status</h2>
          <p className="text-sm text-gray-400 mt-1">
            Monitor backend health, services, and environment
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            Auto-refresh (30s)
          </label>
          <button
            onClick={loadSystemStatus}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-xs text-gray-500">
        Last updated: {formatTimestamp(lastRefresh)}
      </div>

      {/* Health Status Card */}
      {health && (
        <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
            💚 Backend Health
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Status</div>
              <div
                className={`text-lg font-semibold capitalize ${getStatusColor(
                  health.status
                )}`}
              >
                {health.status === "ok" ? "✓ Healthy" : health.status}
              </div>
            </div>
            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Uptime</div>
              <div className="text-lg font-semibold text-blue-400">
                {formatUptime(health.uptime_seconds)}
              </div>
            </div>
            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Version</div>
              <div className="text-lg font-semibold text-gray-300">
                {health.version || "N/A"}
              </div>
            </div>
            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Last Check</div>
              <div className="text-lg font-semibold text-gray-300">
                {new Date(health.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Services Status */}
      {services.length > 0 && (
        <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
            ⚙️ Services
          </h3>
          <div className="space-y-3">
            {services.map((service, index) => (
              <div
                key={index}
                className={`flex items-center justify-between p-4 rounded-lg border ${getStatusColor(
                  service.status
                )}`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{service.icon}</span>
                  <div>
                    <div className="font-semibold text-gray-100">
                      {service.name}
                    </div>
                    <div className="text-xs text-gray-400">
                      {service.description}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${
                      service.status === "running"
                        ? "bg-green-900/60 text-green-300"
                        : service.status === "stopped"
                        ? "bg-yellow-900/60 text-yellow-300"
                        : "bg-red-900/60 text-red-300"
                    }`}
                  >
                    {service.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Environment Status */}
      {environment && (
        <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
            🌍 Environment
          </h3>
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-900/40 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-2">Python Version</div>
                <div className="text-sm font-mono text-gray-300">
                  {environment.python_version}
                </div>
              </div>
              <div className="bg-gray-900/40 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-2">Platform</div>
                <div className="text-sm font-mono text-gray-300">
                  {environment.platform}
                </div>
              </div>
            </div>

            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-2">
                Working Directory
              </div>
              <div className="text-sm font-mono text-gray-300 break-all">
                {environment.working_directory}
              </div>
            </div>

            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-2">Python Path</div>
              <div className="text-sm font-mono text-gray-300 break-all">
                {environment.python_path}
              </div>
            </div>

            <div className="bg-gray-900/40 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-3">
                Environment Variables
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(environment.env_vars).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-400">
                      {key}:
                    </span>
                    <span className="text-sm text-gray-300 ml-2">
                      {typeof value === "boolean" ? (
                        <span
                          className={value ? "text-green-400" : "text-red-400"}
                        >
                          {value ? "✓ Set" : "✗ Not Set"}
                        </span>
                      ) : (
                        <code className="text-blue-400">{String(value)}</code>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* System Info Panel */}
      <section className="bg-blue-900/20 border border-blue-700 rounded-lg p-5">
        <h4 className="font-semibold text-blue-300 mb-2 flex items-center gap-2">
          ℹ️ System Information
        </h4>
        <ul className="text-sm text-blue-200 space-y-1 list-disc list-inside">
          <li>Backend API is accessible at {apiBase}</li>
          <li>
            Health checks run automatically every 30 seconds (when enabled)
          </li>
          <li>Green status indicates all systems operational</li>
          <li>Yellow status indicates warnings or degraded performance</li>
          <li>Red status indicates errors requiring attention</li>
        </ul>
      </section>
    </div>
  );
};

export default SystemStatus;
