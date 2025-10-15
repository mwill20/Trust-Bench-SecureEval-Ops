import React, { useState, useEffect } from "react";

interface ProviderConfig {
  name: string;
  api_key: string;
  model: string;
  base_url?: string;
  enabled: boolean;
}

interface LLMProviderConfigProps {
  apiBase: string;
}

const LLMProviderConfig: React.FC<LLMProviderConfigProps> = ({ apiBase }) => {
  const [providers, setProviders] = useState<{ [key: string]: ProviderConfig }>(
    {
      openai: {
        name: "OpenAI",
        api_key: "",
        model: "gpt-4o-mini",
        enabled: false,
      },
      groq: {
        name: "Groq",
        api_key: "",
        model: "llama-3.3-70b-versatile",
        enabled: false,
      },
      azure: {
        name: "Azure OpenAI",
        api_key: "",
        model: "gpt-4",
        base_url: "",
        enabled: false,
      },
    }
  );

  const [activeProvider, setActiveProvider] = useState<string>("openai");
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string>("");
  const [showApiKey, setShowApiKey] = useState<{ [key: string]: boolean }>({});

  // Load provider configs from backend
  useEffect(() => {
    loadProviderConfigs();
  }, []);

  const loadProviderConfigs = async () => {
    try {
      const response = await fetch(`${apiBase}/api/settings/llm-providers`);
      if (response.ok) {
        const data = await response.json();
        if (data.providers) {
          setProviders(data.providers);
        }
        if (data.active_provider) {
          setActiveProvider(data.active_provider);
        }
      }
    } catch (error) {
      console.error("Failed to load provider configs:", error);
    }
  };

  const saveProviderConfigs = async () => {
    setIsSaving(true);
    setSaveMessage("");

    try {
      const response = await fetch(`${apiBase}/api/settings/llm-providers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          providers,
          active_provider: activeProvider,
        }),
      });

      if (response.ok) {
        setSaveMessage("✓ Provider settings saved successfully!");
        setTimeout(() => setSaveMessage(""), 3000);
      } else {
        const error = await response.json();
        setSaveMessage(`✗ Failed to save: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Failed to save provider configs:", error);
      setSaveMessage("✗ Error saving provider settings");
    } finally {
      setIsSaving(false);
    }
  };

  const testProvider = async (providerKey: string) => {
    setIsTesting(true);
    setTestResult(null);

    try {
      const response = await fetch(
        `${apiBase}/api/settings/llm-providers/test`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            provider: providerKey,
            config: providers[providerKey],
          }),
        }
      );

      const result = await response.json();

      if (response.ok && result.success) {
        setTestResult({
          success: true,
          message: `✓ Connection successful! Model: ${result.model || "N/A"}`,
        });
      } else {
        setTestResult({
          success: false,
          message: `✗ Test failed: ${
            result.error || result.detail || "Unknown error"
          }`,
        });
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: `✗ Test error: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
      });
    } finally {
      setIsTesting(false);
    }
  };

  const updateProvider = (
    providerKey: string,
    field: keyof ProviderConfig,
    value: any
  ) => {
    setProviders((prev) => ({
      ...prev,
      [providerKey]: {
        ...prev[providerKey],
        [field]: value,
      },
    }));
  };

  const toggleShowApiKey = (providerKey: string) => {
    setShowApiKey((prev) => ({
      ...prev,
      [providerKey]: !prev[providerKey],
    }));
  };

  const providerInfo = {
    openai: {
      icon: "🤖",
      description: "OpenAI GPT models (GPT-4, GPT-4o, GPT-3.5-turbo)",
      models: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
      docs: "https://platform.openai.com/docs",
    },
    groq: {
      icon: "⚡",
      description: "Groq ultra-fast inference (Llama, Mixtral)",
      models: [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
      ],
      docs: "https://console.groq.com/docs",
    },
    azure: {
      icon: "☁️",
      description: "Azure OpenAI Service with enterprise features",
      models: ["gpt-4", "gpt-4-32k", "gpt-35-turbo"],
      docs: "https://learn.microsoft.com/azure/ai-services/openai",
    },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">
            LLM Provider Configuration
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Configure API credentials and models for evaluation judges
          </p>
        </div>
        <button
          onClick={saveProviderConfigs}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isSaving ? (
            <>
              <span className="animate-spin">⟳</span>
              Saving...
            </>
          ) : (
            <>💾 Save Configuration</>
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

      {/* Active Provider Selection */}
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
          🎯 Active Provider
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Select which LLM provider to use for evaluation judges and agent
          responses
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(providerInfo).map(([key, info]) => (
            <label
              key={key}
              className={`flex items-center gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                activeProvider === key
                  ? "bg-blue-900/40 border-2 border-blue-600"
                  : "bg-gray-900/40 border-2 border-gray-700 hover:border-gray-600"
              }`}
            >
              <input
                type="radio"
                name="activeProvider"
                value={key}
                checked={activeProvider === key}
                onChange={(e) => setActiveProvider(e.target.value)}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-2xl">{info.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-gray-100">
                  {providers[key].name}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {info.description}
                </div>
              </div>
            </label>
          ))}
        </div>
      </section>

      {/* Provider Configuration Cards */}
      {(Object.entries(providers) as [string, ProviderConfig][]).map(
        ([providerKey, config]) => {
          const info = providerInfo[providerKey as keyof typeof providerInfo];
          const isActive = activeProvider === providerKey;

          return (
            <section
              key={providerKey}
              className={`bg-gray-800/60 border rounded-lg p-6 transition-all ${
                isActive ? "border-blue-600" : "border-gray-700"
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{info.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-100">
                      {config.name}
                    </h3>
                    <p className="text-xs text-gray-500">{info.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.enabled}
                      onChange={(e) =>
                        updateProvider(providerKey, "enabled", e.target.checked)
                      }
                      className="w-5 h-5 text-green-600 rounded"
                    />
                    <span className="text-sm font-medium text-gray-300">
                      {config.enabled ? "✓ Enabled" : "Disabled"}
                    </span>
                  </label>
                  <a
                    href={info.docs}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm"
                  >
                    📖 Docs
                  </a>
                </div>
              </div>

              <div className="space-y-4">
                {/* API Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    API Key{" "}
                    {config.enabled && <span className="text-red-400">*</span>}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type={showApiKey[providerKey] ? "text" : "password"}
                      value={config.api_key}
                      onChange={(e) =>
                        updateProvider(providerKey, "api_key", e.target.value)
                      }
                      placeholder={`Enter your ${config.name} API key`}
                      className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500"
                    />
                    <button
                      onClick={() => toggleShowApiKey(providerKey)}
                      className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
                    >
                      {showApiKey[providerKey] ? "🙈" : "👁️"}
                    </button>
                  </div>
                </div>

                {/* Model Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Model
                  </label>
                  <select
                    value={config.model}
                    onChange={(e) =>
                      updateProvider(providerKey, "model", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-100"
                  >
                    {info.models.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Current model:{" "}
                    <code className="text-blue-400">{config.model}</code>
                  </p>
                </div>

                {/* Azure-specific: Base URL */}
                {providerKey === "azure" && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Endpoint URL{" "}
                      {config.enabled && (
                        <span className="text-red-400">*</span>
                      )}
                    </label>
                    <input
                      type="url"
                      value={config.base_url || ""}
                      onChange={(e) =>
                        updateProvider(providerKey, "base_url", e.target.value)
                      }
                      placeholder="https://YOUR-RESOURCE.openai.azure.com"
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Your Azure OpenAI resource endpoint URL
                    </p>
                  </div>
                )}

                {/* Test Connection Button */}
                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={() => testProvider(providerKey)}
                    disabled={isTesting || !config.api_key}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                    title={
                      !config.api_key
                        ? "Please enter an API key first"
                        : "Test connection to provider"
                    }
                  >
                    {isTesting ? (
                      <>
                        <span className="animate-spin">⟳</span>
                        Testing...
                      </>
                    ) : (
                      <>🔌 Test Connection</>
                    )}
                  </button>
                  {testResult && (
                    <div
                      className={`flex-1 px-3 py-2 rounded-lg text-sm ${
                        testResult.success
                          ? "bg-green-900/40 border border-green-700 text-green-300"
                          : "bg-red-900/40 border border-red-700 text-red-300"
                      }`}
                    >
                      {testResult.message}
                    </div>
                  )}
                </div>
              </div>
            </section>
          );
        }
      )}

      {/* Usage Notes */}
      <section className="bg-blue-900/20 border border-blue-700 rounded-lg p-5">
        <h4 className="font-semibold text-blue-300 mb-2 flex items-center gap-2">
          💡 Configuration Tips
        </h4>
        <ul className="text-sm text-blue-200 space-y-1 list-disc list-inside">
          <li>API keys are stored securely on the server (not in browser)</li>
          <li>Only one provider can be active at a time for evaluation runs</li>
          <li>Enable providers you want to use and disable unused ones</li>
          <li>
            Test connections before running evaluations to ensure proper setup
          </li>
          <li>
            For Azure: You need both the endpoint URL and deployment name in the
            model field
          </li>
        </ul>
      </section>
    </div>
  );
};

export default LLMProviderConfig;
