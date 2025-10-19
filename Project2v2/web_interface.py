"""
Simple web interface for the Trust Bench Multi-Agent Repository Auditor.
Run this to get a web UI for submitting repositories for analysis.
"""

import json
import os
import subprocess
import tempfile
import shutil
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from flask import Flask, render_template_string, request, jsonify, send_file

try:
    from .llm_utils import LLMError, chat_with_llm, test_provider_credentials
    from .security_utils import (
        ValidationError,
        sanitize_prompt,
        security_filters_enabled,
        validate_repo_url,
    )
except ImportError:
    from llm_utils import LLMError, chat_with_llm, test_provider_credentials
    from security_utils import (
        ValidationError,
        sanitize_prompt,
        security_filters_enabled,
        validate_repo_url,
    )

app = Flask(__name__)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets like logos and images"""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return send_file(os.path.join(assets_dir, filename))

def is_valid_github_url(url):
    """Check if the URL is a valid GitHub repository URL"""
    try:
        parsed = urlparse(url)
        if parsed.netloc != 'github.com':
            return False
        
        # Expected format: /owner/repo or /owner/repo/
        path_parts = [p for p in parsed.path.split('/') if p]
        return len(path_parts) >= 2
    except:
        return False

def extract_repo_info(url):
    """Extract owner and repo name from GitHub URL"""
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    return None, None

def clone_repository(repo_url, target_dir):
    """Clone a GitHub repository to a temporary directory"""
    try:
        # Check if git is available
        git_check = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if git_check.returncode != 0:
            raise Exception("Git is not installed or not available in PATH")
        
        # Use git clone with depth 1 for faster cloning
        cmd = ['git', 'clone', '--depth', '1', repo_url, target_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            if "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower():
                raise Exception(f"Repository not found or not accessible: {repo_url}")
            else:
                raise Exception(f"Git clone failed: {result.stderr}")
        
        return True
    except subprocess.TimeoutExpired:
        raise Exception("Repository cloning timed out (120s limit)")
    except Exception as e:
        raise Exception(f"Failed to clone repository: {str(e)}")


def _find_latest_report_path(base_dir: Optional[Path] = None) -> Optional[Path]:
    """Return the most recently modified report.json if one exists."""
    base = base_dir or Path(__file__).parent
    candidates = []

    for directory in base.glob("github_analysis_*"):
        report_path = directory / "report.json"
        if report_path.exists():
            candidates.append(report_path)

    for static_dir in ("output", "output_self"):
        report_path = base / static_dir / "report.json"
        if report_path.exists():
            candidates.append(report_path)

    if not candidates:
        return None

    return max(candidates, key=lambda path: path.stat().st_mtime)


def _load_latest_context() -> Optional[Dict[str, Any]]:
    """Load the latest audit report and conversation data for LLM context."""
    report_path = _find_latest_report_path()
    if not report_path:
        return None

    with report_path.open("r", encoding="utf-8") as handle:
        report_data = json.load(handle)

    messages = report_data.pop("conversation", [])

    return {
        "report": report_data,
        "messages": messages,
        "report_path": str(report_path),
    }

# HTML template for the web interface
HTML_TEMPLATE = """﻿<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Bench Multi-Agent Auditor</title>
    <style>
        :root {
            --primary: #667eea;
            --accent: #424a75;
            --panel-bg: rgba(255, 255, 255, 0.94);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1f2440;
        }
        .sidebar {
            width: 320px;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 4px 0 24px rgba(0,0,0,0.15);
            padding: 32px 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .sidebar h2 {
            margin: 0 0 12px;
            font-size: 22px;
            color: var(--accent);
        }
        .sidebar-section {
            background: #f5f6ff;
            border: 1px solid #dfe3ff;
            border-radius: 12px;
            padding: 18px;
        }
        .sidebar-section h3 {
            margin: 0 0 10px;
            font-size: 16px;
            color: #2f3669;
        }
        .sidebar label {
            font-weight: 600;
            display: block;
            margin-bottom: 6px;
        }
        .sidebar input[type="url"],
        .sidebar input[type="password"],
        .sidebar select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ccd2ff;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .primary-btn {
            width: 100%;
            background: var(--primary);
            color: white;
            padding: 12px 18px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
        }
        .primary-btn:disabled {
            background: #b8bff6;
            cursor: not-allowed;
        }
        .outline-btn {
            background: #eef0ff;
            color: var(--accent);
            padding: 10px 16px;
            border: 1px solid #ccd2ff;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
        }
        .outline-btn:disabled {
            background: #e5e7fb;
            color: #9aa2cf;
            cursor: not-allowed;
        }
        .privacy-note {
            font-size: 12px;
            color: #555d82;
            line-height: 1.4;
        }
        .main-container {
            flex: 1;
            padding: 48px 48px 64px;
            overflow-y: auto;
        }
        .content-card {
            position: relative;
            background: var(--panel-bg);
            border-radius: 20px;
            padding: 42px 38px 50px;
            box-shadow: 0 18px 46px rgba(0,0,0,0.2);
            max-width: 1080px;
            margin: 0 auto;
        }
        .logo-title-flex {
            display: flex;
            align-items: center;
            gap: 48px;
            margin-bottom: 24px;
        }
        .logo {
            display: block;
            margin: 0;
            height: 360px;
            width: 360px;
            object-fit: contain;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2f3669;
            margin: 0;
        }
        .subtitle {
            margin: 80px 0 28px;
            font-size: 20px;
            color: #3c4366;
        }
        .progress-workflow {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .progress-step {
            background: #f5f6ff;
            border: 1px solid #dfe3ff;
            border-radius: 12px;
            padding: 18px;
            transition: all 0.3s ease;
        }
        .progress-step-icon {
            font-size: 18px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 10px;
        }
        .progress-step-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .progress-step-desc {
            color: #555d82;
            font-size: 14px;
            margin-bottom: 12px;
        }
        .progress-step.active {
            border-color: var(--primary);
            box-shadow: 0 8px 22px rgba(102, 126, 234, 0.2);
        }
        .progress-step.completed {
            border-color: #28a745;
            background: #ecfff3;
        }
        .progress-agents {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
        }
        .toggle-details {
            background: none;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-size: 13px;
            text-decoration: underline;
        }
        .agent-details {
            display: none;
            margin-top: 12px;
            background: white;
            border-radius: 10px;
            padding: 12px;
            border: 1px solid #e1e4ff;
            font-size: 13px;
        }
        .agent-details.show {
            display: block;
        }
        .agent-details ul {
            margin: 0;
            padding-left: 18px;
        }
        .loading {
            margin-top: 28px;
            background: #eef2ff;
            border-radius: 12px;
            padding: 22px;
            display: none;
        }
        .results {
            margin-top: 28px;
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e1e4ff;
            display: none;
        }
        .agent-results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
        }
        .agent-card {
            background: #f6f7ff;
            border: 1px solid #dfe3ff;
            border-radius: 10px;
            padding: 14px;
        }
        .score {
            font-size: 24px;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
        }
        .score.excellent { color: #28a745; }
        .score.good { color: #17a2b8; }
        .score.fair { color: #ffc107; }
        .score.needs_attention { color: #dc3545; }
        .chat-panel {
            margin-top: 28px;
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e1e4ff;
            display: none;
        }
        .chat-history {
            border: 1px solid #d9def7;
            border-radius: 8px;
            background: #f9faff;
            min-height: 160px;
            max-height: 260px;
            overflow-y: auto;
            padding: 14px;
            margin-bottom: 14px;
            font-size: 14px;
        }
        .chat-input {
            display: flex;
            gap: 12px;
        }
        .chat-input textarea {
            flex: 1;
            min-height: 90px;
            border: 1px solid #ccd2ff;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            resize: vertical;
        }
        .chat-input button {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 18px;
            cursor: pointer;
        }
        .chat-status {
            margin-top: 8px;
            font-size: 12px;
            color: #555;
            min-height: 18px;
        }
    </style>
</head>
<body>
    <aside class="sidebar">
        <div>
            <h2>How to Use</h2>
            <div class="sidebar-section">
                <h3>Add a repo of interest</h3>
                <form id="auditForm">
                    <label for="repoUrl">GitHub Repository URL</label>
                    <input type="url" id="repoUrl" name="repoUrl" placeholder="https://github.com/owner/repo" required>
                    <button type="submit" class="primary-btn" id="analyzeBtn">Analyze Repository</button>
                </form>
            </div>
            <div class="sidebar-section optional">
                <h3>Optional</h3>
                <p style="margin: 0 0 8px; font-weight: 600; color: #2f2f44;">Ask the Agents</p>
                <label for="providerSelect">LLM Provider</label>
                <select id="providerSelect">
                    <option value="openai">OpenAI</option>
                    <option value="groq">Groq</option>
                    <option value="gemini">Gemini</option>
                </select>
                <label for="apiKeyInput">Add your API Key</label>
                <input type="password" id="apiKeyInput" autocomplete="off" placeholder="Enter key for selected provider">
                <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                    <button type="button" class="outline-btn" id="testKeyBtn">Test Connection</button>
                    <span class="api-key-status" id="apiKeyStatus"></span>
                </div>
                <span class="privacy-note">Your API key is never stored or tracked. It is used only for this session and never leaves your browser except to test or send a chat request.</span>
            </div>
        </div>
    </aside>

    <main class="main-container">
        <div class="content-card">
            <div class="logo-title-flex">
                <img src="/assets/images/TrustBench.png" alt="Trust Bench Logo" class="logo">
                <span class="main-title">Trust Bench Multi-Agent Auditor</span>
            </div>
            <p class="subtitle">AI-powered repository security and quality analysis</p>

            <div class="progress-workflow" id="progressWorkflow" style="display: none;">
                <div class="progress-step progress-single" id="step-input">
                    <div class="progress-step-icon">Step 1</div>
                    <div class="progress-step-title">Input</div>
                    <div class="progress-step-desc">GitHub URL received</div>
                </div>
                <div class="progress-step progress-single" id="step-orchestration">
                    <div class="progress-step-icon">Step 2</div>
                    <div class="progress-step-title">Orchestrator</div>
                    <div class="progress-step-desc">Manager assigns tasks to specialized agents</div>
                    <button class="toggle-details" onclick="toggleDetails('orchestrator-details')">Show details</button>
                    <div class="agent-details" id="orchestrator-details">
                        <h4>Orchestrator capabilities:</h4>
                        <ul>
                            <li>Coordinates all agent activities</li>
                            <li>Controls workflow sequencing</li>
                            <li>Enables agent-to-agent collaboration</li>
                            <li>Combines findings into final score</li>
                            <li>Tracks collaboration metrics</li>
                        </ul>
                    </div>
                </div>
                <div class="progress-agents">
                    <div class="progress-step" id="step-security">
                        <div class="progress-step-icon">Security</div>
                        <div class="progress-step-title">Security Agent</div>
                        <div class="progress-step-desc">Scanning for secrets & vulnerabilities</div>
                        <button class="toggle-details" onclick="toggleDetails('security-details')">Show details</button>
                        <div class="agent-details" id="security-details">
                            <h4>Security scanning & collaboration:</h4>
                            <ul>
                                <li>Secret detection for keys, tokens, passwords</li>
                                <li>Credential scanning for cloud and CI keys</li>
                                <li>Risk assessment and severity ranking</li>
                                <li>Alerts quality/documentation agents</li>
                                <li>Findings influence shared scoring</li>
                            </ul>
                        </div>
                    </div>
                    <div class="progress-step" id="step-quality">
                        <div class="progress-step-icon">Quality</div>
                        <div class="progress-step-title">Quality Agent</div>
                        <div class="progress-step-desc">Analyzing code & tests</div>
                        <button class="toggle-details" onclick="toggleDetails('quality-details')">Show details</button>
                        <div class="agent-details" id="quality-details">
                            <h4>Code quality & collaboration:</h4>
                            <ul>
                                <li>Identifies languages and structure</li>
                                <li>Integrates security context into scores</li>
                                <li>Calculates test coverage ratios</li>
                                <li>Shares metrics with documentation agent</li>
                                <li>Adapts scoring dynamically</li>
                            </ul>
                        </div>
                    </div>
                    <div class="progress-step" id="step-documentation">
                        <div class="progress-step-icon">Docs</div>
                        <div class="progress-step-title">Documentation Agent</div>
                        <div class="progress-step-desc">Reviewing docs & READMEs</div>
                        <button class="toggle-details" onclick="toggleDetails('documentation-details')">Show details</button>
                        <div class="agent-details" id="documentation-details">
                            <h4>Documentation & context analysis:</h4>
                            <ul>
                                <li>Reviews README structure and depth</li>
                                <li>Adjusts expectations by project size</li>
                                <li>Flags missing security guidance</li>
                                <li>Collaborates with security and quality</li>
                                <li>Adapts scoring using shared context</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="progress-step progress-single" id="step-results">
                    <div class="progress-step-icon">Step 3</div>
                    <div class="progress-step-title">Results</div>
                    <div class="progress-step-desc">Scores compiled and comprehensive report generated</div>
                </div>
            </div>

            <div class="loading" id="loading">
                <h3>Agents are analyzing your repository...</h3>
                <p>Cloning repository...</p>
                <p>Security agent scanning for vulnerabilities and secrets...</p>
                <p>Quality agent checking code quality and test coverage...</p>
                <p>Documentation agent reviewing documentation...</p>
                <p><em>This may take 30-60 seconds for large repositories.</em></p>
            </div>
            <div class="results" id="results">
                <h2>Analysis Results</h2>
                <div id="resultsContent"></div>
                <button type="button" class="outline-btn" id="downloadReportBtn" style="display: none; margin-top: 16px;">Download report</button>
            </div>

            <div class="chat-panel" id="chatPanel">
                <h2>Ask the Agents</h2>
                <div class="chat-history" id="chatHistory">
                    <div class="chat-message" id="chatPlaceholder" data-initial="true">
                        <strong>Status</strong>
                        <span>Run an analysis to generate a fresh report before asking a question.</span>
                    </div>
                </div>
                <div class="chat-input">
                    <textarea id="chatQuestion" placeholder="Ask about the latest Trust Bench report..."></textarea>
                    <button type="button" id="sendChatBtn">Send</button>
                </div>
                <div class="chat-status" id="chatStatus"></div>
            </div>
        </div>
    </main>

        <script>
        (function () {
            const defaultProvider = "{{ default_provider }}";
            const PROMPT_INJECTION_PATTERNS = [
                new RegExp("forget\\s+previous\\s+instructions", "gi"),
                new RegExp("ignore\\s+all\\s+previous", "gi"),
                new RegExp("reset\\s+conversation", "gi"),
                new RegExp("system\\s*prompt", "gi"),
                new RegExp("you\\s+are\\s+now\\s+.*assistant", "gi"),
            ];

            function sanitizeInput(value, maxLength = 4000) {
                if (value === undefined || value === null) {
                    return '';
                }
                let text = String(value);
                text = text.replace(/[\\u0000-\\u0008\\u000B\\u000C\\u000E-\\u001F\\u007F]/g, '');
                PROMPT_INJECTION_PATTERNS.forEach((pattern) => {
                    text = text.replace(pattern, '');
                });
                if (text.length > maxLength) {
                    text = text.slice(0, maxLength);
                }
                return text.trim();
            }

            function maskApiKeyForDisplay(key, prefix = 4, suffix = 2) {
                const normalized = sanitizeInput(key, 200);
                if (!normalized) {
                    return '';
                }
                if (normalized.length <= prefix + suffix) {
                    return '*'.repeat(normalized.length);
                }
                const maskedLength = normalized.length - prefix - suffix;
                return `${normalized.slice(0, prefix)}${'*'.repeat(maskedLength)}${normalized.slice(-suffix)}`;
            }

            function escapeHtml(value) {
                const str = value === null || value === undefined ? '' : String(value);
                return str
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }

            const auditForm = document.getElementById('auditForm');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const repoUrlInput = document.getElementById('repoUrl');
            const providerSelect = document.getElementById('providerSelect');
            const apiKeyInput = document.getElementById('apiKeyInput');
            const testKeyBtn = document.getElementById('testKeyBtn');
            const apiKeyStatus = document.getElementById('apiKeyStatus');
            const chatPanel = document.getElementById('chatPanel');
            const chatHistory = document.getElementById('chatHistory');
            const chatQuestion = document.getElementById('chatQuestion');
            const chatStatus = document.getElementById('chatStatus');
            const chatPlaceholder = document.getElementById('chatPlaceholder');
            const sendChatBtn = document.getElementById('sendChatBtn');
            const downloadReportBtn = document.getElementById('downloadReportBtn');
            const progressWorkflow = document.getElementById('progressWorkflow');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const resultsContent = document.getElementById('resultsContent');

            let latestReportPath = null;

            function getApiKey(provider) {
                if (!provider) {
                    return '';
                }
                try {
                    return sessionStorage.getItem(`llm_api_key_${provider}`) || '';
                } catch (err) {
                    return '';
                }
            }

            function setApiKey(provider, key) {
                if (!provider) {
                    return;
                }
                try {
                    if (key) {
                        sessionStorage.setItem(`llm_api_key_${provider}`, key);
                    } else {
                        sessionStorage.removeItem(`llm_api_key_${provider}`);
                    }
                } catch (err) {
                    /* ignore */
                }
            }

            function updateApiKeyInput(clearStatus = true) {
                if (!providerSelect || !apiKeyInput) {
                    return;
                }
                const provider = providerSelect.value;
                apiKeyInput.value = getApiKey(provider);
                if (clearStatus && apiKeyStatus) {
                    apiKeyStatus.textContent = '';
                    apiKeyStatus.style.color = '#555';
                }
            }

            function appendChatMessage(author, text) {
                if (!chatHistory) {
                    return;
                }
                if (chatPlaceholder && chatPlaceholder.parentElement) {
                    chatPlaceholder.parentElement.removeChild(chatPlaceholder);
                }
                const wrapper = document.createElement('div');
                wrapper.className = 'chat-message';

                const label = document.createElement('strong');
                label.textContent = author;
                wrapper.appendChild(label);

                const body = document.createElement('div');
                body.textContent = text;
                wrapper.appendChild(body);

                chatHistory.appendChild(wrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            function updateChatStatus(message, isError = false) {
                if (!chatStatus) {
                    return;
                }
                chatStatus.textContent = sanitizeInput(message || '');
                chatStatus.style.color = isError ? '#b00020' : '#555';
            }

            async function sendChatMessage() {
                if (!chatQuestion || !sendChatBtn) {
                    return;
                }
                const rawQuestion = chatQuestion.value;
                const question = sanitizeInput(rawQuestion);
                if (!question) {
                    updateChatStatus('Enter a question before sending.', true);
                    return;
                }
                const provider = providerSelect ? providerSelect.value : null;
                const apiKey = provider ? getApiKey(provider) : '';

                appendChatMessage('You', question);
                chatQuestion.value = '';
                updateChatStatus('Waiting for response...');
                sendChatBtn.disabled = true;

                try {
                    const payload = { question, provider };
                    if (apiKey) {
                        payload.api_key = apiKey;
                    }

                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    });

                    const data = await response.json();

                    if (!response.ok || !data.success) {
                        const message = data && data.error ? data.error : `Chat failed (${response.status})`;
                        appendChatMessage('System', sanitizeInput(message));
                        updateChatStatus(message, true);
                        return;
                    }

                    const providerLabel = sanitizeInput((data.provider || provider || 'provider').toUpperCase());
                    appendChatMessage(providerLabel, sanitizeInput(data.answer || '(No answer returned)'));

                    if (data.context_available) {
                        const sourceNote = data.context_source ? ` (${data.context_source})` : '';
                        updateChatStatus(`Answered using the latest report context${sanitizeInput(sourceNote)}.`);
                    } else {
                        updateChatStatus('Answered without local report context. Run an analysis for better results.');
                    }
                } catch (error) {
                    appendChatMessage('System', 'Unable to reach the chat service.');
                    updateChatStatus('Unable to reach the chat service.', true);
                } finally {
                    sendChatBtn.disabled = false;
                }
            }

            function updateProgressStep(stepId, state) {
                const step = document.getElementById(stepId);
                if (!step) {
                    return;
                }
                step.classList.remove('active', 'completed');
                if (state === 'active' || state === 'completed') {
                    step.classList.add(state);
                }
            }

            function resetProgressSteps() {
                ['step-input', 'step-orchestration', 'step-security', 'step-quality', 'step-documentation', 'step-results'].forEach((id) => {
                    const step = document.getElementById(id);
                    if (step) {
                        step.classList.remove('active', 'completed');
                    }
                });
            }

            function sleep(ms) {
                return new Promise((resolve) => setTimeout(resolve, ms));
            }

            window.toggleDetails = function toggleDetails(detailsId) {
                const details = document.getElementById(detailsId);
                if (!details) {
                    return;
                }
                const button = details.previousElementSibling;
                const isVisible = details.classList.toggle('show');
                if (button) {
                    button.textContent = isVisible ? 'Hide details' : 'Show details';
                }
            };

            function isValidGitHubUrl(url) {
                try {
                    const parsed = new URL(url);
                    const segments = parsed.pathname.split('/').filter(Boolean);
                    return parsed.hostname === 'github.com' && segments.length >= 2;
                } catch (err) {
                    return false;
                }
            }

            function displayResults(report) {
                if (!resultsContent) {
                    return;
                }
                if (!report) {
                    resultsContent.innerHTML = '';
                    return;
                }
                const repoInfo = report.repository_info || {};
                const summary = report.summary || {};
                const agents = report.agents || {};

                const safeUrl = escapeHtml(repoInfo.url || '#');
                const safeOwner = escapeHtml(repoInfo.owner || '');
                const safeName = escapeHtml(repoInfo.name || '');

                let html = '';
                if (repoInfo.url && repoInfo.owner && repoInfo.name) {
                    html += `<div style="margin-bottom: 20px; padding: 15px; background: #f0f8ff; border-radius: 8px;">
                                <h3>Repository: <a href="${safeUrl}" target="_blank" rel="noopener">${safeOwner}/${safeName}</a></h3>
                             </div>`;
                }

                if (typeof summary.overall_score !== 'undefined' && summary.grade) {
                    const safeGrade = escapeHtml(summary.grade);
                    const safeScore = escapeHtml(summary.overall_score);
                    html += `<div class="score ${safeGrade}">
                                Overall Score: ${safeScore}/100
                                <br>Grade: ${safeGrade.toUpperCase()}
                             </div>`;
                }

                html += '<div class="agent-results">';
                Object.entries(agents).forEach(([agentName, agentData]) => {
                    const score = typeof agentData.score !== 'undefined' ? agentData.score : 'N/A';
                    const summaryText = agentData.summary || 'No summary available.';
                    html += `<div class="agent-card">
                                <h3>${escapeHtml(agentName)}</h3>
                                <p><strong>Score:</strong> ${escapeHtml(score)}</p>
                                <p><strong>Summary:</strong> ${escapeHtml(summaryText)}</p>
                             </div>`;
                });
                html += '</div>';

                if (Array.isArray(report.conversation) && report.conversation.length > 0) {
                    html += '<h3>Agent Conversation Log</h3><ul>';
                    report.conversation.forEach((msg) => {
                        const sender = escapeHtml(msg.sender || 'Unknown');
                        const recipient = escapeHtml(msg.recipient || 'Unknown');
                        const content = escapeHtml(msg.content || '');
                        html += `<li><strong>${sender} &rarr; ${recipient}:</strong> ${content}</li>`;
                    });
                    html += '</ul>';
                }

                resultsContent.innerHTML = html;
            }

            if (chatStatus) {
                updateChatStatus('Run an analysis to capture the latest context.');
            }
            if (providerSelect && defaultProvider) {
                providerSelect.value = defaultProvider;
            }
            if (providerSelect && apiKeyInput) {
                providerSelect.addEventListener('change', () => updateApiKeyInput());
                apiKeyInput.addEventListener('input', () => {
                    const sanitizedKey = sanitizeInput(apiKeyInput.value, 200);
                    apiKeyInput.value = sanitizedKey;
                    setApiKey(providerSelect.value, sanitizedKey);
                    if (apiKeyStatus) {
                        apiKeyStatus.textContent = '';
                        apiKeyStatus.style.color = '#555';
                    }
                });
                updateApiKeyInput(false);
            }
            if (sendChatBtn) {
                sendChatBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    sendChatMessage();
                });
            }
            if (chatQuestion) {
                chatQuestion.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();
                        sendChatMessage();
                    }
                });
            }
            if (testKeyBtn && apiKeyInput && providerSelect && apiKeyStatus) {
                testKeyBtn.addEventListener('click', async () => {
                    const provider = providerSelect.value;
                    let apiKey = sanitizeInput(apiKeyInput.value, 200);
                    apiKeyInput.value = apiKey;

                    if (!provider) {
                        updateChatStatus('Select an LLM provider before testing.', true);
                        if (apiKeyStatus) {
                            apiKeyStatus.textContent = 'Select a provider first.';
                            apiKeyStatus.style.color = '#b00020';
                        }
                        return;
                    }
                    if (!apiKey) {
                        apiKeyStatus.textContent = 'Enter an API key first.';
                        apiKeyStatus.style.color = '#b00020';
                        return;
                    }

                    apiKeyStatus.textContent = 'Testing...';
                    apiKeyStatus.style.color = '#555';
                    testKeyBtn.disabled = true;

                    try {
                        const response = await fetch('/api/test-llm-key', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ provider, api_key: apiKey }),
                        });

                        const data = await response.json();

                        if (!response.ok || !data.success) {
                            const message = data && data.error ? data.error : `Connection failed (${response.status})`;
                            apiKeyStatus.textContent = sanitizeInput(message);
                            apiKeyStatus.style.color = '#b00020';
                            return;
                        }

                        apiKeyStatus.textContent = 'Connection successful!';
                        apiKeyStatus.style.color = '#28a745';
                        setApiKey(provider, apiKey);
                    } catch (err) {
                        apiKeyStatus.textContent = 'Unable to reach the server.';
                        apiKeyStatus.style.color = '#b00020';
                    } finally {
                        testKeyBtn.disabled = false;
                    }
                });
            }

            if (downloadReportBtn) {
                downloadReportBtn.addEventListener('click', () => {
                    if (!latestReportPath) {
                        return;
                    }
                    const url = new URL('/download-report', window.location.origin);
                    url.searchParams.append('output_dir', latestReportPath);
                    window.location.href = url.toString();
                });
            }

            if (auditForm) {
                auditForm.addEventListener('submit', async (event) => {
                    event.preventDefault();

                    const rawRepoUrl = repoUrlInput ? repoUrlInput.value : '';
                    const repoUrl = sanitizeInput(rawRepoUrl, 2048);
                    if (repoUrlInput) {
                        repoUrlInput.value = repoUrl;
                    }

                    if (!isValidGitHubUrl(repoUrl)) {
                        alert('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
                        return;
                    }

                    if (progressWorkflow) {
                        progressWorkflow.style.display = 'flex';
                    }
                    if (results) {
                        results.style.display = 'none';
                    }
                    if (chatPanel) {
                        chatPanel.style.display = 'none';
                    }
                    if (downloadReportBtn) {
                        downloadReportBtn.style.display = 'none';
                    }
                    latestReportPath = null;

                    updateProgressStep('step-input', 'active');
                    await sleep(300);
                    updateProgressStep('step-input', 'completed');

                    updateProgressStep('step-orchestration', 'active');
                    if (analyzeBtn) {
                        analyzeBtn.disabled = true;
                        analyzeBtn.textContent = 'Analyzing...';
                    }
                    if (loading) {
                        loading.style.display = 'block';
                    }
                    updateChatStatus('Generating a fresh report for your repository...');
                    await sleep(600);

                    try {
                        updateProgressStep('step-orchestration', 'completed');

                        updateProgressStep('step-security', 'active');
                        updateProgressStep('step-quality', 'active');
                        updateProgressStep('step-documentation', 'active');

                        const response = await fetch('/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ repo_url: repoUrl })
                        });

                        const data = await response.json();

                        updateProgressStep('step-security', 'completed');
                        updateProgressStep('step-quality', 'completed');
                        updateProgressStep('step-documentation', 'completed');

                        updateProgressStep('step-results', 'active');
                        await sleep(400);

                        if (response.ok && data.success) {
                            displayResults(data.report);
                            updateProgressStep('step-results', 'completed');

                            latestReportPath = data.output_dir;
                            if (downloadReportBtn && latestReportPath) {
                                downloadReportBtn.style.display = 'inline-block';
                            }

                            const repoInfo = data.report && data.report.repository_info;
                            if (repoInfo && repoInfo.owner && repoInfo.name) {
                                const statusMessage = sanitizeInput(`Latest context loaded from ${repoInfo.owner}/${repoInfo.name}. Ask a follow-up question anytime.`);
                                updateChatStatus(statusMessage);
                                if (chatPlaceholder && chatPlaceholder.parentElement) {
                                    const placeholderBody = chatPlaceholder.querySelector('span');
                                    if (placeholderBody) {
                                        placeholderBody.textContent = sanitizeInput(`Context ready for ${repoInfo.owner}/${repoInfo.name}. Ask a question whenever you're ready.`);
                                    }
                                }
                            } else {
                                updateChatStatus('Latest context loaded. Ask a follow-up question anytime.');
                            }

                            if (results) {
                                results.style.display = 'block';
                            }
                            if (chatPanel) {
                                chatPanel.style.display = 'block';
                            }
                        } else {
                            const message = data && data.error ? data.error : `Analysis failed (${response.status})`;
                            if (resultsContent) {
                                resultsContent.innerHTML = `<div style="color: #c62828;"><h3>Error</h3><p>${escapeHtml(message)}</p></div>`;
                            }
                            resetProgressSteps();
                            updateChatStatus(message, true);
                            if (results) {
                                results.style.display = 'block';
                            }
                        }
                    } catch (error) {
                        if (resultsContent) {
                            resultsContent.innerHTML = `<div style="color: #c62828;"><h3>Error</h3><p>${escapeHtml(error.message)}</p></div>`;
                        }
                        if (results) {
                            results.style.display = 'block';
                        }
                        updateChatStatus(error.message || 'Unexpected error during analysis.', true);
                        resetProgressSteps();
                    } finally {
                        if (analyzeBtn) {
                            analyzeBtn.disabled = false;
                            analyzeBtn.textContent = 'Analyze Repository';
                        }
                        if (loading) {
                            loading.style.display = 'none';
                        }
                    }
                });
            } else {
                console.warn('Audit form element not found; analysis submission will not work.');
            }
        })();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    default_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    return render_template_string(HTML_TEMPLATE, default_provider=default_provider)

@app.route('/analyze', methods=['POST'])
def analyze():
    temp_dir = None
    try:
        data = request.json or {}
        repo_url = (data.get('repo_url') or '').strip()
        
        if security_filters_enabled():
            try:
                repo_url = validate_repo_url(repo_url)
            except ValidationError as exc:
                return jsonify({
                    'success': False,
                    'error': str(exc)
                })
        else:
            if not is_valid_github_url(repo_url):
                return jsonify({
                    'success': False,
                    'error': 'Please provide a valid GitHub repository URL (e.g., https://github.com/owner/repo)'
                })
        
        # Extract repo information for naming
        owner, repo_name = extract_repo_info(repo_url)
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix=f'trustbench_{owner}_{repo_name}_')
        
        # Clone the repository
        clone_repository(repo_url, temp_dir)
        
        # Create output directory
        output_dir = f"github_analysis_{owner}_{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run the analysis on the cloned repository
        cmd = ['python', 'main.py', '--repo', temp_dir, '--output', output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f"Analysis failed: {result.stderr}"
            })
        
        # Read the generated report
        report_path = Path(output_dir) / 'report.json'
        if not report_path.exists():
            return jsonify({
                'success': False,
                'error': "Report file not generated"
            })
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        # Add repository information to the report
        report['repository_info'] = {
            'url': repo_url,
            'owner': owner,
            'name': repo_name
        }
        
        return jsonify({
            'success': True,
            'report': report,
            'output_dir': output_dir
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Best effort cleanup


@app.route('/download-report')
def download_report():
    output_dir = request.args.get('output_dir', '')
    if not output_dir:
        return jsonify({
            'success': False,
            'error': 'Missing output directory.'
        }), 400

    base_dir = Path(__file__).parent.resolve()
    candidate_dir = (base_dir / output_dir).resolve()

    if not str(candidate_dir).startswith(str(base_dir)):
        return jsonify({
            'success': False,
            'error': 'Invalid output directory.'
        }), 400

    report_path = candidate_dir / 'report.json'
    if not report_path.exists():
        return jsonify({
            'success': False,
            'error': 'Report not found.'
        }), 404

    download_name = f"{candidate_dir.name}_report.json"
    return send_file(report_path, as_attachment=True, download_name=download_name)


@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON payload.'
        }), 400

    raw_question = payload.get('question', '')
    if security_filters_enabled():
        question = sanitize_prompt(raw_question)
    else:
        question = str(raw_question or '').strip()
    provider_raw = payload.get('provider')
    provider = str(provider_raw).strip().lower() if provider_raw else None
    api_key_raw = payload.get('api_key')
    api_key = None
    if isinstance(api_key_raw, str):
        trimmed = api_key_raw.strip()
        api_key = trimmed or None

    if not question:
        return jsonify({
            'success': False,
            'error': 'Question is required.'
        }), 400

    try:
        context = _load_latest_context()
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': f'Failed to load context: {exc}'
        }), 500

    try:
        llm_response = chat_with_llm(
            question=question,
            context=context,
            provider_override=provider,
            api_key_override=api_key,
        )
    except LLMError as exc:
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {exc}'
        }), 500

    return jsonify({
        'success': True,
        'answer': llm_response.get('answer', ''),
        'provider': llm_response.get('provider'),
        'context_available': bool(context),
        'context_source': context.get('report_path') if context else None,
    })

@app.route('/api/test-llm-key', methods=['POST'])
def api_test_llm_key():
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON payload.'
        }), 400

    provider_raw = payload.get('provider')
    api_key_raw = payload.get('api_key')
    provider = str(provider_raw).strip().lower() if provider_raw else ''
    api_key = api_key_raw.strip() if isinstance(api_key_raw, str) else ''

    if not provider:
        return jsonify({
            'success': False,
            'error': 'Provider is required.'
        }), 400
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API key is required.'
        }), 400

    try:
        test_provider_credentials(provider, api_key)
    except LLMError as exc:
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {exc}'
        }), 500

    return jsonify({
        'success': True,
        'provider': provider,
    })

if __name__ == '__main__':
    print("≡ƒÜÇ Starting Trust Bench Multi-Agent Auditor Web Interface...")
    print("≡ƒôì Open your browser to: http://localhost:5000")
    print("≡ƒöì Ready to analyze repositories!")
    app.run(debug=True, host='0.0.0.0', port=5000)
