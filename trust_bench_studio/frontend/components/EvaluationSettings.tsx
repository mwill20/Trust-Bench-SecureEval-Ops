import React, { useState, useEffect } from "react";

interface Profile {
  name: string;
  description: string;
  thresholds: {
    task_fidelity: number;
    security_eval: number;
    system_perf: number;
    ethics_refusal: number;
  };
}

interface EvaluationSettingsProps {
  apiBase: string;
}

const EvaluationSettings: React.FC<EvaluationSettingsProps> = ({ apiBase }) => {
  const [activeProfile, setActiveProfile] = useState<string>("default");
  const [profiles, setProfiles] = useState<Profile[]>([
    {
      name: "default",
      description: "Standard evaluation thresholds for general use",
      thresholds: {
        task_fidelity: 0.7,
        security_eval: 0.8,
        system_perf: 0.75,
        ethics_refusal: 0.85,
      },
    },
    {
      name: "highstakes",
      description: "Strict thresholds for production/sensitive environments",
      thresholds: {
        task_fidelity: 0.85,
        security_eval: 0.95,
        system_perf: 0.85,
        ethics_refusal: 0.95,
      },
    },
  ]);

  const [customThresholds, setCustomThresholds] = useState({
    task_fidelity: 0.7,
    security_eval: 0.8,
    system_perf: 0.75,
    ethics_refusal: 0.85,
  });

  const [enabledAgents, setEnabledAgents] = useState({
    task_fidelity: true,
    security_eval: true,
    system_perf: true,
    ethics_refusal: true,
  });

  const [runOptions, setRunOptions] = useState({
    max_samples: 100,
    timeout_seconds: 300,
    parallel_agents: true,
    save_artifacts: true,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string>("");

  // Load settings from backend
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch(`${apiBase}/api/settings/evaluation`);
      if (response.ok) {
        const data = await response.json();
        if (data.active_profile) setActiveProfile(data.active_profile);
        if (data.custom_thresholds) setCustomThresholds(data.custom_thresholds);
        if (data.enabled_agents) setEnabledAgents(data.enabled_agents);
        if (data.run_options) setRunOptions(data.run_options);
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    setSaveMessage("");

    try {
      const response = await fetch(`${apiBase}/api/settings/evaluation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          active_profile: activeProfile,
          custom_thresholds: customThresholds,
          enabled_agents: enabledAgents,
          run_options: runOptions,
        }),
      });

      if (response.ok) {
        setSaveMessage("✓ Settings saved successfully!");
        setTimeout(() => setSaveMessage(""), 3000);
      } else {
        setSaveMessage("✗ Failed to save settings");
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
      setSaveMessage("✗ Error saving settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleProfileChange = (profileName: string) => {
    setActiveProfile(profileName);
    const profile = profiles.find((p) => p.name === profileName);
    if (profile && profileName !== "custom") {
      setCustomThresholds(profile.thresholds);
    }
  };

  const handleThresholdChange = (
    agent: keyof typeof customThresholds,
    value: number
  ) => {
    setCustomThresholds((prev) => ({
      ...prev,
      [agent]: Math.max(0, Math.min(1, value)),
    }));
    if (activeProfile !== "custom") {
      setActiveProfile("custom");
    }
  };

  const handleAgentToggle = (agent: keyof typeof enabledAgents) => {
    setEnabledAgents((prev) => ({
      ...prev,
      [agent]: !prev[agent],
    }));
  };

  const getCurrentThresholds = () => {
    if (activeProfile === "custom") {
      return customThresholds;
    }
    const profile = profiles.find((p) => p.name === activeProfile);
    return profile?.thresholds || customThresholds;
  };

  const thresholds = getCurrentThresholds();

  const agentInfo = {
    task_fidelity: {
      label: "Task Fidelity",
      description: "Measures accuracy and faithfulness of agent responses",
      icon: "🎯",
    },
    security_eval: {
      label: "Security Evaluation",
      description:
        "Checks for vulnerabilities, injection attacks, and secrets exposure",
      icon: "🛡️",
    },
    system_perf: {
      label: "System Performance",
      description: "Monitors latency, throughput, and resource usage",
      icon: "⚡",
    },
    ethics_refusal: {
      label: "Ethics & Refusal",
      description:
        "Validates proper handling of harmful or inappropriate requests",
      icon: "⚖️",
    },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">
            Evaluation Settings
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Configure thresholds, agents, and run parameters for evaluations
          </p>
        </div>
        <button
          onClick={saveSettings}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isSaving ? (
            <>
              <span className="animate-spin">⟳</span>
              Saving...
            </>
          ) : (
            <>💾 Save Settings</>
          )}
        </button>
      </div>

      {/* Save Message */}
      {saveMessage && (
        <div
          className={`px-4 py-3 rounded-lg ${
            saveMessage.includes("✓")
              ? "bg-green-900/40 border border-green-700 text-green-300"
              : "bg-red-900/40 border border-red-700 text-red-300"
          }`}
        >
          {saveMessage}
        </div>
      )}

      {/* Profile Selection */}
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
          📋 Evaluation Profile
        </h3>
        <div className="space-y-3">
          {profiles.map((profile) => (
            <label
              key={profile.name}
              className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                activeProfile === profile.name
                  ? "bg-blue-900/40 border-2 border-blue-600"
                  : "bg-gray-900/40 border-2 border-gray-700 hover:border-gray-600"
              }`}
            >
              <input
                type="radio"
                name="profile"
                value={profile.name}
                checked={activeProfile === profile.name}
                onChange={(e) => handleProfileChange(e.target.value)}
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div className="flex-1">
                <div className="font-semibold text-gray-100 capitalize">
                  {profile.name}
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  {profile.description}
                </div>
                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                  {Object.entries(profile.thresholds).map(([key, value]) => (
                    <span key={key}>
                      {key
                        .split("_")
                        .map((w) => w[0]?.toUpperCase() || "")
                        .join("")}
                      : {((value as number) * 100).toFixed(0)}%
                    </span>
                  ))}
                </div>
              </div>
            </label>
          ))}
          <label
            className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-all ${
              activeProfile === "custom"
                ? "bg-blue-900/40 border-2 border-blue-600"
                : "bg-gray-900/40 border-2 border-gray-700 hover:border-gray-600"
            }`}
          >
            <input
              type="radio"
              name="profile"
              value="custom"
              checked={activeProfile === "custom"}
              onChange={(e) => handleProfileChange(e.target.value)}
              className="mt-1 w-4 h-4 text-blue-600"
            />
            <div className="flex-1">
              <div className="font-semibold text-gray-100">Custom</div>
              <div className="text-sm text-gray-400 mt-1">
                Define your own threshold values below
              </div>
            </div>
          </label>
        </div>
      </section>

      {/* Threshold Configuration */}
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
          🎚️ Pillar Thresholds
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Set minimum passing scores (0-100%) for each evaluation pillar. Agents
          must meet or exceed these thresholds.
        </p>
        <div className="space-y-4">
          {Object.entries(agentInfo).map(([key, info]) => {
            const agentKey = key as keyof typeof customThresholds;
            const value = thresholds[agentKey];
            const percentage = (value * 100).toFixed(0);

            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{info.icon}</span>
                    <div>
                      <div className="font-medium text-gray-100">
                        {info.label}
                      </div>
                      <div className="text-xs text-gray-500">
                        {info.description}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-blue-400">
                      {percentage}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={value * 100}
                    onChange={(e) =>
                      handleThresholdChange(
                        agentKey,
                        parseInt(e.target.value) / 100
                      )
                    }
                    className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    disabled={activeProfile !== "custom"}
                  />
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={percentage}
                    onChange={(e) =>
                      handleThresholdChange(
                        agentKey,
                        parseInt(e.target.value) / 100
                      )
                    }
                    className="w-16 px-2 py-1 bg-gray-900 border border-gray-700 rounded text-center text-sm"
                    disabled={activeProfile !== "custom"}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Agent Selection */}
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
          🤖 Agent Selection
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Choose which agents to include in the evaluation run. Disabled agents
          will be skipped.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(agentInfo).map(([key, info]) => {
            const agentKey = key as keyof typeof enabledAgents;
            const isEnabled = enabledAgents[agentKey];

            return (
              <label
                key={key}
                className={`flex items-center gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                  isEnabled
                    ? "bg-green-900/20 border-2 border-green-700"
                    : "bg-gray-900/40 border-2 border-gray-700 hover:border-gray-600"
                }`}
              >
                <input
                  type="checkbox"
                  checked={isEnabled}
                  onChange={() => handleAgentToggle(agentKey)}
                  className="w-5 h-5 text-green-600 rounded"
                />
                <span className="text-xl">{info.icon}</span>
                <div className="flex-1">
                  <div className="font-medium text-gray-100">{info.label}</div>
                  <div className="text-xs text-gray-500">
                    {info.description}
                  </div>
                </div>
                {isEnabled && (
                  <span className="text-green-400 text-sm font-medium">
                    ✓ Enabled
                  </span>
                )}
              </label>
            );
          })}
        </div>
      </section>

      {/* Run Options */}
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
          ⚙️ Run Options
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Samples per Agent
            </label>
            <input
              type="number"
              min="1"
              max="1000"
              value={runOptions.max_samples}
              onChange={(e) =>
                setRunOptions((prev) => ({
                  ...prev,
                  max_samples: parseInt(e.target.value),
                }))
              }
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-100"
            />
            <p className="text-xs text-gray-500 mt-1">
              Number of test samples to evaluate per agent
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Timeout (seconds)
            </label>
            <input
              type="number"
              min="30"
              max="3600"
              value={runOptions.timeout_seconds}
              onChange={(e) =>
                setRunOptions((prev) => ({
                  ...prev,
                  timeout_seconds: parseInt(e.target.value),
                }))
              }
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-100"
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum time allowed for evaluation run
            </p>
          </div>

          <label className="flex items-center gap-3 p-4 bg-gray-900/40 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={runOptions.parallel_agents}
              onChange={(e) =>
                setRunOptions((prev) => ({
                  ...prev,
                  parallel_agents: e.target.checked,
                }))
              }
              className="w-5 h-5 text-blue-600 rounded"
            />
            <div>
              <div className="font-medium text-gray-100">
                Parallel Execution
              </div>
              <div className="text-xs text-gray-500">
                Run multiple agents simultaneously
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3 p-4 bg-gray-900/40 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={runOptions.save_artifacts}
              onChange={(e) =>
                setRunOptions((prev) => ({
                  ...prev,
                  save_artifacts: e.target.checked,
                }))
              }
              className="w-5 h-5 text-blue-600 rounded"
            />
            <div>
              <div className="font-medium text-gray-100">Save Artifacts</div>
              <div className="text-xs text-gray-500">
                Preserve detailed logs and outputs
              </div>
            </div>
          </label>
        </div>
      </section>
    </div>
  );
};

export default EvaluationSettings;
