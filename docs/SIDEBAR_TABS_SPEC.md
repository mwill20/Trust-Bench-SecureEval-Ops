# Trust Bench Studio - Sidebar Tabs Specification

## Overview
The Trust Bench Studio interface has three main tabs in the sidebar:
1. **Flow** - Main evaluation workflow interface (✅ Complete)
2. **Reports** - View evaluation reports and MCP tool results (⚠️ Basic implementation)
3. **Settings** - Configure environment and view security settings (⚠️ Basic implementation)

---

## 1. Flow Tab ✅

### Current Status
**Fully functional and working as expected**

### Features
- Real-time agent orchestration visualization
- Interactive agent nodes (Aegis, Athena, Hermes, Logos)
- Task input field for repository URLs or instructions
- Live execution logs panel
- Agent chat windows for interactive debugging
- Three action buttons:
  - 🧹 Cleanup Workspace
  - 📊 Generate Report  
  - ⭐ Promote to Baseline

### Use Cases
- Run security evaluations on code repositories
- Monitor agent execution in real-time
- Debug agent reasoning via chat interfaces
- View evaluation results (4 pillars: Security, Ethics, Fidelity, Performance)
- Take actions on evaluation results (cleanup, report, baseline)

---

## 2. Reports Tab ⚠️

### Current Status
**Basic implementation - displays JSON snapshots**

### Current Implementation
Located in `App.tsx` (lines 268-302):
```tsx
const ReportsPanel: React.FC<{
  lastReport: ReportSnapshot | null;
  lastCleanup: MCPResponse | null;
}> = ({ lastReport, lastCleanup }) => (
  <div className="flex-1 bg-gray-900 text-gray-200 p-8 overflow-y-auto">
    <h2 className="text-2xl font-bold mb-4">Reports &amp; MCP</h2>
    <div className="space-y-6">
      <section className="bg-gray-800/60 border border-gray-700 rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-2">Latest Report Snapshot</h3>
        {lastReport ? (
          <pre className="bg-gray-900/80 border border-gray-700 rounded-md p-4 text-sm overflow-x-auto">
            {JSON.stringify(lastReport, null, 2)}
          </pre>
        ) : (
          <p className="text-gray-400">
            Run an analysis to generate a report snapshot.
          </p>
        )}
      </section>
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
```

### What It Should Do

#### Primary Purpose
**View and manage evaluation reports and historical results**

#### Proposed Features

##### 1. Report History List
- Show list of all generated reports (most recent first)
- Display metadata for each report:
  - Timestamp
  - Repository evaluated
  - Overall verdict (PASS/FAIL/PARTIAL)
  - Pillar scores (Security, Ethics, Fidelity, Performance)
- Click to view full report details

##### 2. Report Viewer
- Render HTML reports inline (from `report.html`)
- Display formatted evaluation results:
  - Executive Summary
  - Detailed metrics for each pillar
  - Performance charts/graphs
  - Recommendations
- Export options:
  - Download HTML
  - Download PDF (future)
  - Copy shareable link

##### 3. Baseline Comparison
- Show current baseline metrics
- Compare latest run vs baseline
- Highlight regressions/improvements
- Trend analysis over time

##### 4. MCP Tool Activity
- History of MCP tool invocations:
  - Prompt Guard (injection detection)
  - Secrets Scanner
  - Workspace Cleanup
- Tool results and statistics
- Success/failure rates

##### 5. Archive Management
- List archived evaluation runs
- Restore archived runs for analysis
- Delete old archives
- Disk space usage summary

#### Mockup Layout
```
┌─────────────────────────────────────────────────────────┐
│ Reports & Analytics                          [Refresh]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─── Latest Report ─────────────────────────────────┐  │
│ │ ✅ PASS - Clean Repository Evaluation             │  │
│ │ 📅 2025-01-28 14:30:15                           │  │
│ │ 📊 Security: ✅  Ethics: ✅  Fidelity: ✅  Perf: ✅│  │
│ │ [View Full Report] [Download HTML] [Compare]      │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌─── Report History ────────────────────────────────┐  │
│ │ 📄 2025-01-28 12:15:30 - vuln-mini-1 - ❌ FAIL   │  │
│ │ 📄 2025-01-27 18:45:22 - rl-project - ⚠️ PARTIAL │  │
│ │ 📄 2025-01-27 16:20:10 - clean-mini-1 - ✅ PASS  │  │
│ │ [Load More...]                                    │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌─── Baseline ──────────────────────────────────────┐  │
│ │ ⭐ Current Baseline: clean-mini-1                 │  │
│ │ 📅 Promoted: 2025-01-28 14:30:15                  │  │
│ │ 📊 Security: 1.0  Ethics: 1.0  Fidelity: 0.685    │  │
│ │ [View Details] [Update Baseline]                  │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌─── MCP Tool Activity ─────────────────────────────┐  │
│ │ 🛡️ Prompt Guard: 47 scans, 0 injections blocked  │  │
│ │ 🔐 Secrets Scanner: 3 scans, 0 secrets found      │  │
│ │ 🧹 Workspace Cleanup: Last run freed 9.49 MB      │  │
│ │ [View Details]                                     │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Settings Tab ⚠️

### Current Status
**Basic implementation - displays static information**

### Current Implementation
Located in `App.tsx` (lines 303-333):
```tsx
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
```

### What It Should Do

#### Primary Purpose
**Configure evaluation parameters, environment settings, and system preferences**

#### Proposed Features

##### 1. Evaluation Settings
- **Default Repository**: Set default repo for quick testing
  - Dropdown: clean-mini-1, vuln-mini-1, rl-project, custom URL
- **Evaluation Profile**: Select quality standards
  - Default Profile (balanced)
  - High Stakes Profile (strict, zero tolerance)
  - Custom Profile
- **Thresholds**: Adjust pass/fail criteria
  - Security threshold (default: 0.9)
  - Ethics threshold (default: 0.9)
  - Fidelity threshold (default: 0.7)
  - Performance threshold (default: 0.8)

##### 2. LLM Provider Configuration
- **Provider Selection**: 
  - Groq (default)
  - OpenAI
  - Azure OpenAI (future)
  - Anthropic (future)
- **API Key Management**:
  - Masked input fields
  - Test connection button
  - Status indicator (✅ Connected / ❌ Not configured)
- **Model Selection**:
  - Groq: llama-3.3-70b-versatile (default), mixtral-8x7b-32768
  - OpenAI: gpt-4, gpt-3.5-turbo
- **Advanced Options**:
  - Temperature (0.0 - 1.0)
  - Max tokens
  - Timeout settings

##### 3. MCP Server Configuration
- **HTTP Server Settings**:
  - Port (default: 8765)
  - Host (default: localhost)
  - Enable/disable MCP tools
- **Tool Configuration**:
  - Prompt Guard sensitivity
  - Secrets scanner patterns
  - Cleanup retention policy
- **Connection Status**:
  - MCP server health check
  - Last successful connection timestamp
  - Error messages if unavailable

##### 4. Report Settings
- **Template**: Choose report format
  - Standard (default)
  - Detailed (verbose)
  - Executive Summary (brief)
- **Auto-generate**: Generate report after each evaluation
- **Output Format**: HTML, Markdown, PDF (future)

##### 5. Workspace Settings
- **Auto-cleanup**: Enable/disable automatic cleanup
- **Retention Policy**: Number of runs to keep (default: 10)
- **Archive Location**: Path to archive directory
- **Baseline Settings**: Auto-promote on passing evaluations

##### 6. System Information
- **Environment Variables**: Display current configuration
  - VITE_API_BASE
  - TRUST_BENCH_LLM_PROVIDER
  - API key status (configured/not configured)
- **Version Information**: 
  - Frontend version
  - Backend version
  - Python version
  - Node version
- **System Health**:
  - Backend API status
  - MCP server status
  - Disk space available
  - Last evaluation timestamp

##### 7. Security & Privacy
- **Data Retention**: How long to keep evaluation data
- **Logging Level**: Info, Debug, Warning, Error
- **Sensitive Data Handling**: Redaction settings
- **Audit Log**: View system audit trail

#### Mockup Layout
```
┌─────────────────────────────────────────────────────────┐
│ Settings                                   [Save] [Reset]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─── Evaluation Settings ──────────────────────────┐   │
│ │ Default Repository: [clean-mini-1        ▼]      │   │
│ │ Evaluation Profile: [Default             ▼]      │   │
│ │                                                   │   │
│ │ Pass/Fail Thresholds:                             │   │
│ │   Security:    [0.9] ━━━━━━━━●━━ 1.0            │   │
│ │   Ethics:      [0.9] ━━━━━━━━●━━ 1.0            │   │
│ │   Fidelity:    [0.7] ━━━━●━━━━━━ 1.0            │   │
│ │   Performance: [0.8] ━━━━━●━━━━━ 1.0            │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── LLM Provider ─────────────────────────────────┐   │
│ │ Provider: [Groq                         ▼]       │   │
│ │ Model:    [llama-3.3-70b-versatile      ▼]       │   │
│ │ API Key:  [••••••••••••••••••••] ✅ Connected    │   │
│ │           [Test Connection]                       │   │
│ │                                                   │   │
│ │ Advanced:                                         │   │
│ │   Temperature: [0.3] ━━●━━━━━━━━ 1.0            │   │
│ │   Max Tokens:  [4096]                            │   │
│ │   Timeout:     [30s]                             │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── MCP Server ───────────────────────────────────┐   │
│ │ Status: ✅ Connected (http://localhost:8765)     │   │
│ │                                                   │   │
│ │ Enabled Tools:                                    │   │
│ │   ☑️ Prompt Guard                                │   │
│ │   ☑️ Secrets Scanner                             │   │
│ │   ☑️ Workspace Cleanup                           │   │
│ │                                                   │   │
│ │ [Configure Tools]                                 │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── Report Settings ──────────────────────────────┐   │
│ │ ☑️ Auto-generate after evaluation                │   │
│ │ Template: [Standard                ▼]            │   │
│ │ Format:   [HTML                    ▼]            │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── Workspace ────────────────────────────────────┐   │
│ │ ☑️ Auto-cleanup enabled                          │   │
│ │ Keep last: [10] runs                             │   │
│ │ Archive location: [trustbench_core/eval/runs/... │   │
│ │ ☐ Auto-promote baseline on pass                  │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── System Information ───────────────────────────┐   │
│ │ Frontend:      v1.0.0                            │   │
│ │ Backend:       ✅ Connected (v1.0.0)             │   │
│ │ Python:        3.13                              │   │
│ │ Disk Space:    45.3 GB available                 │   │
│ │ Last Eval:     2025-01-28 14:30:15               │   │
│ └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1 (Current - MVP)
- ✅ Flow tab fully functional
- ⚠️ Reports tab shows JSON snapshots
- ⚠️ Settings tab shows static info

### Phase 2 (Recommended Next)
**Reports Tab Enhancements**:
1. List recent evaluation reports
2. Inline HTML report viewer
3. Download report button
4. Baseline comparison view

**Settings Tab Core Features**:
1. LLM provider configuration UI
2. API key input with test connection
3. System status indicators
4. Basic threshold controls

### Phase 3 (Future)
**Reports Tab Advanced**:
- Historical trend analysis
- MCP tool activity dashboard
- Archive management UI

**Settings Tab Advanced**:
- Full evaluation profile editor
- Advanced MCP tool configuration
- Audit log viewer
- Export/import settings

---

## Technical Notes

### Reports Tab Data Sources
- **Report History**: Read from `trustbench_core/eval/runs/`
- **HTML Reports**: Load from `trustbench_core/eval/runs/*/report.html`
- **Baseline Metrics**: Read from `trustbench_core/eval/runs/baseline/`
- **MCP Activity**: Backend API endpoint `/api/mcp/activity` (needs creation)

### Settings Tab Backend Integration
- **Save Settings**: `POST /api/settings/update`
- **Test Connection**: `POST /api/llm/test`
- **Get System Info**: `GET /api/system/info`
- **MCP Status**: `GET /api/mcp/status`

All settings should persist to:
- Frontend: `localStorage` for UI preferences
- Backend: `trustbench_core/eval/eval_config.yaml` for evaluation settings
- Environment: `.env` file for secrets (API keys)

---

## Recommendations

### Immediate Next Steps
1. **Reports Tab**: Add report history list (read from runs directory)
2. **Reports Tab**: Add HTML report viewer (iframe or div with innerHTML)
3. **Settings Tab**: Add editable threshold sliders
4. **Settings Tab**: Add LLM provider selector with connection test

### User Experience
- Keep Flow tab as default landing page
- Add breadcrumbs showing current tab path
- Add keyboard shortcuts (Alt+1=Flow, Alt+2=Reports, Alt+3=Settings)
- Add unsaved changes warning in Settings tab

### Security Considerations
- **API Keys**: Never log or display in plain text
- **Settings Validation**: Server-side validation for all settings
- **CORS**: Restrict API access to frontend origin only
- **Rate Limiting**: Prevent abuse of test connection endpoints

---

**Last Updated**: 2025-01-28 (October 14, 2025)
**Status**: Specification Complete - Implementation Pending
**Related Docs**: 
- [Button Implementation Summary](./BUTTON_IMPLEMENTATION_SUMMARY.md)
- [User Guide - Buttons](./USER_GUIDE_BUTTONS.md)
- [Phase 1 Handover](./PHASE_1_HANDOVER.md)
