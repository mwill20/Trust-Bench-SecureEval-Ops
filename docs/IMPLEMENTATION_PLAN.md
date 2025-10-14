# Trust Bench Studio - Reports & Settings Enhancement Plan

## 🎯 Project Overview

**Goal**: Transform the Reports and Settings tabs from basic static displays into fully functional, interactive interfaces that provide real value to users.

**Timeline**: 3 phases (Immediate, Short-term, Future)

**Priority**: Focus on Reports Tab first (higher user value), then Settings Tab core features.

---

## 📊 Phase 1: Reports Tab Enhancement (HIGH PRIORITY)

### Milestone 1.1: Report History List

**Estimated Time**: 2-3 hours
**User Value**: ⭐⭐⭐⭐⭐

#### Requirements

- [ ] Read all evaluation runs from `trustbench_core/eval/runs/` directory
- [ ] Parse metrics.json from each run to extract:
  - [ ] Timestamp
  - [ ] Repository name/URL
  - [ ] Overall verdict (PASS/FAIL/PARTIAL)
  - [ ] Individual pillar scores (Security, Ethics, Fidelity, Performance)
- [ ] Sort runs by timestamp (most recent first)
- [ ] Display in a clean, scannable list format

#### UI Components Needed

- [ ] `ReportListItem` component

  - [ ] Icon for verdict (✅/❌/⚠️)
  - [ ] Timestamp (formatted: "Jan 28, 2025 14:30")
  - [ ] Repository name (truncated if long)
  - [ ] Pillar scores (color-coded badges)
  - [ ] "View Report" button
  - [ ] Hover state for clickability

- [ ] `ReportHistorySection` component
  - [ ] Header with "Report History" title
  - [ ] Refresh button
  - [ ] List of ReportListItem components
  - [ ] "Load More" button (if >10 reports)
  - [ ] Empty state message

#### Backend API Needed

```
GET /api/reports/list
Response: {
  reports: [
    {
      id: "run_20250128_143015",
      timestamp: "2025-01-28T14:30:15Z",
      repository: "clean-mini-1",
      verdict: "PASS",
      pillars: {
        security: 1.0,
        ethics: 1.0,
        fidelity: 0.685,
        performance: 0.95
      },
      hasHtmlReport: true
    },
    ...
  ]
}
```

#### Implementation Steps

1. [ ] Create backend endpoint `/api/reports/list`

   - [ ] File: `trust_bench_studio/api/server.py`
   - [ ] Function: `list_evaluation_reports()`
   - [ ] Logic: Scan runs directory, read metrics.json files
   - [ ] Return sorted list with metadata

2. [ ] Create `ReportListItem.tsx` component

   - [ ] File: `trust_bench_studio/frontend/components/ReportListItem.tsx`
   - [ ] Props: report metadata
   - [ ] Render verdict icon, timestamp, repo, pillars
   - [ ] onClick handler to view report

3. [ ] Update `ReportsPanel` in App.tsx

   - [ ] Add state: `reportHistory: Report[]`
   - [ ] Add useEffect to fetch reports on mount
   - [ ] Replace static JSON section with ReportListItem list
   - [ ] Add loading/error states

4. [ ] Test thoroughly
   - [ ] Verify reports load on tab switch
   - [ ] Test with 0 reports (empty state)
   - [ ] Test with many reports (scrolling)
   - [ ] Verify timestamps format correctly

---

### Milestone 1.2: HTML Report Viewer

**Estimated Time**: 2-3 hours
**User Value**: ⭐⭐⭐⭐⭐

#### Requirements

- [ ] Load HTML report content from disk
- [ ] Display in-app (no external browser needed)
- [ ] Preserve CSS styling from report.html
- [ ] Handle missing reports gracefully
- [ ] Provide back button to return to list

#### UI Components Needed

- [ ] `ReportViewer` component
  - [ ] Full-width container
  - [ ] Header with back button and download button
  - [ ] Report metadata bar (timestamp, repo, verdict)
  - [ ] HTML content container (iframe or dangerouslySetInnerHTML)
  - [ ] Loading spinner while fetching
  - [ ] Error message if report not found

#### Backend API Needed

```
GET /api/reports/view/{report_id}
Response: {
  html: "<html>...</html>",
  metadata: {
    timestamp: "...",
    repository: "...",
    verdict: "..."
  }
}
```

OR serve static file:

```
GET /api/reports/html/{report_id}
Response: Raw HTML file content
```

#### Implementation Steps

1. [ ] Create backend endpoint `/api/reports/view/{report_id}`

   - [ ] File: `trust_bench_studio/api/server.py`
   - [ ] Function: `get_report_html(report_id: str)`
   - [ ] Read report.html from disk
   - [ ] Return HTML content (sanitized)

2. [ ] Create `ReportViewer.tsx` component

   - [ ] File: `trust_bench_studio/frontend/components/ReportViewer.tsx`
   - [ ] Fetch HTML content on mount
   - [ ] Render in iframe (safest) or div with dangerouslySetInnerHTML
   - [ ] Add download button (download original HTML)
   - [ ] Add back button to close viewer

3. [ ] Update `ReportsPanel` in App.tsx

   - [ ] Add state: `selectedReportId: string | null`
   - [ ] Add conditional rendering: show viewer or list
   - [ ] Pass report ID to ReportViewer
   - [ ] Handle back button click

4. [ ] Test thoroughly
   - [ ] Verify HTML renders correctly
   - [ ] Test CSS styling preserved
   - [ ] Test download functionality
   - [ ] Test back button navigation
   - [ ] Test with missing report file

---

### Milestone 1.3: Baseline Comparison View

**Estimated Time**: 3-4 hours
**User Value**: ⭐⭐⭐⭐

#### Requirements

- [ ] Load current baseline metrics
- [ ] Compare latest run vs baseline
- [ ] Show delta (improvement/regression)
- [ ] Visual indicators (arrows, colors)
- [ ] Handle missing baseline gracefully

#### UI Components Needed

- [ ] `BaselineComparison` component
  - [ ] Two-column layout: Current | Baseline
  - [ ] Metric rows for each pillar
  - [ ] Delta indicators (↑ ↓ → with colors)
  - [ ] Overall verdict comparison
  - [ ] Last baseline promotion timestamp
  - [ ] "Update Baseline" button

#### Backend API Needed

```
GET /api/baseline/comparison
Response: {
  current: {
    timestamp: "...",
    verdict: "PASS",
    pillars: { security: 1.0, ... }
  },
  baseline: {
    timestamp: "...",
    verdict: "PASS",
    pillars: { security: 0.95, ... }
  },
  deltas: {
    security: +0.05,
    ethics: 0.0,
    ...
  }
}
```

#### Implementation Steps

1. [ ] Create backend endpoint `/api/baseline/comparison`

   - [ ] File: `trust_bench_studio/api/server.py`
   - [ ] Read latest metrics.json
   - [ ] Read baseline metrics.json
   - [ ] Calculate deltas
   - [ ] Return comparison object

2. [ ] Create `BaselineComparison.tsx` component

   - [ ] File: `trust_bench_studio/frontend/components/BaselineComparison.tsx`
   - [ ] Fetch comparison data
   - [ ] Render two-column comparison
   - [ ] Color-code deltas (green=better, red=worse)
   - [ ] Show trend arrows

3. [ ] Update `ReportsPanel` in App.tsx

   - [ ] Add BaselineComparison section
   - [ ] Place above or below report history
   - [ ] Connect "Update Baseline" to existing handler

4. [ ] Test thoroughly
   - [ ] Verify deltas calculate correctly
   - [ ] Test with no baseline (show empty state)
   - [ ] Test improvements vs regressions
   - [ ] Verify color coding is intuitive

---

### Milestone 1.4: MCP Tool Activity Dashboard

**Estimated Time**: 2-3 hours
**User Value**: ⭐⭐⭐

#### Requirements

- [ ] Show usage statistics for each MCP tool
- [ ] Display recent activity log
- [ ] Show success/failure rates
- [ ] Link to detailed logs if needed

#### UI Components Needed

- [ ] `MCPActivityCard` component

  - [ ] Tool name and icon
  - [ ] Total invocations count
  - [ ] Success rate percentage
  - [ ] Last used timestamp
  - [ ] Quick stats (e.g., "0 injections blocked")

- [ ] `MCPActivitySection` component
  - [ ] Grid of activity cards (one per tool)
  - [ ] Recent activity timeline
  - [ ] "View Full Logs" button

#### Backend API Needed

```
GET /api/mcp/activity
Response: {
  tools: {
    prompt_guard: {
      totalCalls: 47,
      successRate: 1.0,
      lastUsed: "2025-01-28T14:30:15Z",
      stats: {
        injectionsBlocked: 0,
        injectionsDetected: 0
      }
    },
    secrets_scan: { ... },
    cleanup_workspace: { ... }
  }
}
```

#### Implementation Steps

1. [ ] Create backend endpoint `/api/mcp/activity`

   - [ ] File: `trust_bench_studio/api/server.py`
   - [ ] Query MCP HTTP server for stats
   - [ ] Or read from local activity log
   - [ ] Return aggregated statistics

2. [ ] Create `MCPActivityCard.tsx` component

   - [ ] File: `trust_bench_studio/frontend/components/MCPActivityCard.tsx`
   - [ ] Display tool icon and name
   - [ ] Show statistics in clean format
   - [ ] Add hover tooltip with details

3. [ ] Update `ReportsPanel` in App.tsx

   - [ ] Add MCP Activity section
   - [ ] Fetch activity data
   - [ ] Render cards in grid layout

4. [ ] Test thoroughly
   - [ ] Verify counts are accurate
   - [ ] Test with zero activity
   - [ ] Test refresh functionality

---

## ⚙️ Phase 2: Settings Tab Enhancement (MEDIUM PRIORITY)

### Milestone 2.1: Evaluation Settings UI

**Estimated Time**: 3-4 hours
**User Value**: ⭐⭐⭐⭐

#### Requirements

- [ ] Editable threshold sliders (4 pillars)
- [ ] Default repository dropdown
- [ ] Evaluation profile selector
- [ ] Save/Reset buttons
- [ ] Persist to eval_config.yaml

#### UI Components Needed

- [ ] `ThresholdSlider` component

  - [ ] Label (e.g., "Security Threshold")
  - [ ] Slider input (0.0 - 1.0)
  - [ ] Numeric display
  - [ ] Color coding (red=low, yellow=medium, green=high)

- [ ] `EvaluationSettings` component
  - [ ] Section header
  - [ ] 4 threshold sliders
  - [ ] Repository dropdown
  - [ ] Profile dropdown
  - [ ] Save/Reset buttons
  - [ ] Unsaved changes indicator

#### Backend API Needed

```
GET /api/settings/evaluation
Response: {
  thresholds: {
    security: 0.9,
    ethics: 0.9,
    fidelity: 0.7,
    performance: 0.8
  },
  defaultRepo: "clean-mini-1",
  profile: "default"
}

POST /api/settings/evaluation
Body: { same as GET response }
Response: { success: true, message: "Settings saved" }
```

#### Implementation Steps

1. [ ] Create GET endpoint `/api/settings/evaluation`

   - [ ] Read from `eval_config.yaml`
   - [ ] Return current settings

2. [ ] Create POST endpoint `/api/settings/evaluation`

   - [ ] Validate settings
   - [ ] Write to `eval_config.yaml`
   - [ ] Return success/error

3. [ ] Create `ThresholdSlider.tsx` component

   - [ ] Range input (0-100, map to 0.0-1.0)
   - [ ] Number display with 2 decimals
   - [ ] onChange handler
   - [ ] Color coding based on value

4. [ ] Create `EvaluationSettings.tsx` component

   - [ ] Load settings on mount
   - [ ] Render 4 sliders + dropdowns
   - [ ] Track dirty state (unsaved changes)
   - [ ] Save button calls API
   - [ ] Reset button restores from server

5. [ ] Update `SettingsPanel` in App.tsx

   - [ ] Replace static text with EvaluationSettings component
   - [ ] Add save confirmation toast

6. [ ] Test thoroughly
   - [ ] Verify sliders update values
   - [ ] Test save functionality
   - [ ] Test reset functionality
   - [ ] Verify yaml file updates correctly
   - [ ] Test validation (reject invalid values)

---

### Milestone 2.2: LLM Provider Configuration

**Estimated Time**: 3-4 hours
**User Value**: ⭐⭐⭐⭐⭐

#### Requirements

- [ ] Provider selector (Groq, OpenAI, etc.)
- [ ] Model dropdown (per provider)
- [ ] API key input (masked)
- [ ] Test connection button
- [ ] Connection status indicator
- [ ] Advanced options (temperature, tokens)

#### UI Components Needed

- [ ] `LLMProviderConfig` component
  - [ ] Provider dropdown
  - [ ] Model dropdown (dynamic based on provider)
  - [ ] API key input (type="password")
  - [ ] "Show/Hide" toggle for key
  - [ ] "Test Connection" button
  - [ ] Status indicator (✅/❌/⏳)
  - [ ] Advanced options collapsible section
  - [ ] Save button

#### Backend API Needed

```
GET /api/settings/llm
Response: {
  provider: "groq",
  model: "llama-3.3-70b-versatile",
  apiKeyConfigured: true,  // Don't send actual key
  temperature: 0.3,
  maxTokens: 4096,
  timeout: 30
}

POST /api/settings/llm
Body: { provider, model, apiKey, temperature, maxTokens, timeout }
Response: { success: true }

POST /api/llm/test
Body: { provider, apiKey }
Response: {
  success: true,
  message: "Connection successful",
  modelInfo: { ... }
}
```

#### Implementation Steps

1. [ ] Create GET endpoint `/api/settings/llm`

   - [ ] Read from environment/config
   - [ ] Return settings (mask API key)

2. [ ] Create POST endpoint `/api/settings/llm`

   - [ ] Validate settings
   - [ ] Write to .env file or config
   - [ ] Restart LLM provider (if needed)

3. [ ] Create POST endpoint `/api/llm/test`

   - [ ] Attempt connection with provided credentials
   - [ ] Make test API call
   - [ ] Return success/failure

4. [ ] Create `LLMProviderConfig.tsx` component

   - [ ] Provider dropdown with logos
   - [ ] Model dropdown (filtered by provider)
   - [ ] Masked password input
   - [ ] Test button with loading state
   - [ ] Status display with icons
   - [ ] Advanced settings accordion

5. [ ] Update `SettingsPanel` in App.tsx

   - [ ] Add LLMProviderConfig section
   - [ ] Handle test results
   - [ ] Show success/error toasts

6. [ ] Test thoroughly
   - [ ] Test with valid credentials
   - [ ] Test with invalid credentials
   - [ ] Test connection timeout
   - [ ] Verify API key masking
   - [ ] Test each provider if possible
   - [ ] Verify settings persist after reload

---

### Milestone 2.3: System Status Dashboard

**Estimated Time**: 2-3 hours
**User Value**: ⭐⭐⭐

#### Requirements

- [ ] Backend API health check
- [ ] MCP server status
- [ ] LLM provider connection status
- [ ] Disk space information
- [ ] Version information
- [ ] Last evaluation timestamp

#### UI Components Needed

- [ ] `SystemStatus` component
  - [ ] Status cards for each service
  - [ ] Green/yellow/red indicators
  - [ ] Version badges
  - [ ] Disk space meter
  - [ ] Auto-refresh every 30s
  - [ ] Manual refresh button

#### Backend API Needed

```
GET /api/system/health
Response: {
  backend: {
    status: "healthy",
    version: "1.0.0",
    uptime: 3600
  },
  mcp: {
    status: "connected",
    url: "http://localhost:8765",
    lastCheck: "2025-01-28T14:30:15Z"
  },
  llm: {
    status: "connected",
    provider: "groq",
    model: "llama-3.3-70b-versatile"
  },
  storage: {
    diskSpaceTotal: "256GB",
    diskSpaceUsed: "210GB",
    diskSpaceAvailable: "46GB",
    percentUsed: 82
  },
  lastEvaluation: "2025-01-28T14:30:15Z"
}
```

#### Implementation Steps

1. [ ] Create endpoint `/api/system/health`

   - [ ] Check backend health
   - [ ] Ping MCP server
   - [ ] Check LLM provider
   - [ ] Get disk space (using psutil)
   - [ ] Read last evaluation timestamp

2. [ ] Create `SystemStatus.tsx` component

   - [ ] Fetch health data
   - [ ] Render status cards
   - [ ] Auto-refresh with setInterval
   - [ ] Manual refresh button
   - [ ] Color-coded indicators

3. [ ] Update `SettingsPanel` in App.tsx

   - [ ] Add SystemStatus section at bottom

4. [ ] Test thoroughly
   - [ ] Verify status updates
   - [ ] Test with services down
   - [ ] Verify auto-refresh works
   - [ ] Test manual refresh

---

## 🚀 Phase 3: Advanced Features (FUTURE)

### Milestone 3.1: Historical Trend Analysis

**Estimated Time**: 4-6 hours
**User Value**: ⭐⭐⭐

- [ ] Line charts showing pillar scores over time
- [ ] Identify regression trends
- [ ] Compare multiple repositories
- [ ] Export trend data to CSV

### Milestone 3.2: Archive Management UI

**Estimated Time**: 3-4 hours
**User Value**: ⭐⭐⭐

- [ ] List archived runs with restore option
- [ ] Delete old archives
- [ ] Bulk operations
- [ ] Archive compression stats

### Milestone 3.3: Custom Evaluation Profiles

**Estimated Time**: 4-5 hours
**User Value**: ⭐⭐⭐⭐

- [ ] Create custom profiles with unique thresholds
- [ ] Save/load profiles
- [ ] Profile templates (strict, balanced, lenient)
- [ ] Profile sharing/export

### Milestone 3.4: Audit Log Viewer

**Estimated Time**: 3-4 hours
**User Value**: ⭐⭐

- [ ] View system audit trail
- [ ] Filter by action type
- [ ] Search logs
- [ ] Export audit logs

---

## 📋 Master Checklist

### Reports Tab

- [ ] **Milestone 1.1**: Report History List (2-3h)
- [ ] **Milestone 1.2**: HTML Report Viewer (2-3h)
- [ ] **Milestone 1.3**: Baseline Comparison View (3-4h)
- [ ] **Milestone 1.4**: MCP Tool Activity Dashboard (2-3h)

**Total Estimated Time**: 9-13 hours

### Settings Tab

- [ ] **Milestone 2.1**: Evaluation Settings UI (3-4h)
- [ ] **Milestone 2.2**: LLM Provider Configuration (3-4h)
- [ ] **Milestone 2.3**: System Status Dashboard (2-3h)

**Total Estimated Time**: 8-11 hours

### Future Enhancements

- [ ] **Milestone 3.1**: Historical Trend Analysis (4-6h)
- [ ] **Milestone 3.2**: Archive Management UI (3-4h)
- [ ] **Milestone 3.3**: Custom Evaluation Profiles (4-5h)
- [ ] **Milestone 3.4**: Audit Log Viewer (3-4h)

**Total Estimated Time**: 14-19 hours

---

## 🎯 Implementation Strategy

### Week 1: Reports Tab MVP

**Goal**: Basic functional Reports tab

1. **Day 1-2**: Milestone 1.1 (Report History List)
2. **Day 2-3**: Milestone 1.2 (HTML Report Viewer)
3. **Day 4**: Milestone 1.3 (Baseline Comparison)
4. **Day 5**: Milestone 1.4 (MCP Activity Dashboard)

### Week 2: Settings Tab MVP

**Goal**: Basic functional Settings tab

1. **Day 1-2**: Milestone 2.1 (Evaluation Settings)
2. **Day 3-4**: Milestone 2.2 (LLM Provider Config)
3. **Day 5**: Milestone 2.3 (System Status)

### Week 3+: Polish & Advanced Features

- Testing and bug fixes
- UI/UX improvements
- Phase 3 features as needed

---

## 🧪 Testing Strategy

### For Each Milestone

1. [ ] Unit test new components
2. [ ] Integration test API endpoints
3. [ ] Manual UI testing
4. [ ] Edge case testing (empty states, errors)
5. [ ] Performance testing (large data sets)
6. [ ] Cross-browser testing

### Test Scenarios Checklist

#### Reports Tab

- [ ] Load with 0 reports
- [ ] Load with 1 report
- [ ] Load with 100+ reports
- [ ] View report with missing HTML file
- [ ] Baseline comparison with no baseline
- [ ] MCP activity with no data
- [ ] Concurrent report generation
- [ ] Download report while viewing
- [ ] Browser back/forward navigation

#### Settings Tab

- [ ] Save settings with valid values
- [ ] Save settings with invalid values
- [ ] Reset to defaults
- [ ] Test LLM connection success
- [ ] Test LLM connection failure
- [ ] Test with invalid API key
- [ ] Unsaved changes warning
- [ ] Multiple rapid saves
- [ ] Settings persistence after refresh

---

## 📊 Success Metrics

### Quantitative

- [ ] All API endpoints respond < 500ms
- [ ] UI interactions complete < 100ms
- [ ] Report viewer loads < 1s
- [ ] Zero console errors
- [ ] 100% test coverage for critical paths

### Qualitative

- [ ] Users can find past reports easily
- [ ] Settings are intuitive to adjust
- [ ] Error messages are helpful
- [ ] UI feels responsive and polished
- [ ] No learning curve for basic operations

---

## 🚨 Risk Management

### Potential Issues & Mitigation

#### Large Report Files

**Risk**: HTML reports >5MB cause slow loading
**Mitigation**:

- Lazy load report content
- Add file size warning
- Implement pagination for large reports

#### Missing Dependencies

**Risk**: psutil not installed for disk space check
**Mitigation**:

- Add to requirements.txt
- Graceful fallback if unavailable

#### API Key Security

**Risk**: Accidentally exposing API keys in logs/UI
**Mitigation**:

- Never log keys
- Always mask in UI
- Validate on backend only
- Use environment variables

#### Concurrent Modifications

**Risk**: Multiple users editing settings simultaneously
**Mitigation**:

- Add file locking for config writes
- Show "Settings changed by another user" warning
- Implement optimistic locking

---

## 📚 Documentation Requirements

### For Each Milestone

- [ ] Update SIDEBAR_TABS_SPEC.md with implementation notes
- [ ] Add API endpoint documentation
- [ ] Update USER_GUIDE with new features
- [ ] Screenshot new UI components
- [ ] Update TESTING_GUIDE with new test cases

---

## 🎉 Definition of Done

### Milestone Complete When:

- [ ] All requirements implemented
- [ ] All tests passing
- [ ] Code reviewed (or self-reviewed)
- [ ] Documentation updated
- [ ] No known bugs
- [ ] Performance acceptable
- [ ] User testing positive (if applicable)

### Phase Complete When:

- [ ] All milestones in phase complete
- [ ] Integration testing passed
- [ ] Acceptance criteria met
- [ ] Stakeholder approval
- [ ] Ready for production deployment

---

**Last Updated**: 2025-01-28 (October 14, 2025)
**Status**: Ready to Begin Implementation
**Next Action**: Start Milestone 1.1 (Report History List)
