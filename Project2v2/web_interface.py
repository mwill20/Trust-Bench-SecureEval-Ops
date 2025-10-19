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
except ImportError:
    from llm_utils import LLMError, chat_with_llm, test_provider_credentials

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
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Bench Multi-Agent Auditor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            padding-top: 270px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
        }
        .logo {
            position: absolute;
            top: 20px;
            left: 20px;
            height: 240px;
            width: 240px;
            object-fit: contain;
            z-index: 10;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"], select {
            width: 100%;
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 24px;
            min-height: 60px;
            line-height: 1.4;
        }
        #repoUrl, input[type="url"] {
            width: 150% !important;
            max-width: 600px !important;
            padding: 20px !important;
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            font-size: 24px !important;
            min-height: 60px !important;
            line-height: 1.4 !important;
            box-sizing: border-box !important;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .loading {
            text-align: center;
            color: #667eea;
            display: none;
        }
        .score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .excellent { color: #28a745; }
        .good { color: #17a2b8; }
        .fair { color: #ffc107; }
        .needs_attention { color: #dc3545; }
        .agent-results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .agent-card {
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .progress-workflow {
            margin: 30px 0;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .progress-step {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            background: #f9f9f9;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }
        .progress-single {
            /* Single steps like Input, Orchestrator, Results */
        }
        .progress-agents {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        .progress-agents .progress-step {
            flex: 1;
            margin-bottom: 0;
            font-size: 14px;
        }
        .progress-step.active {
            border-color: #667eea;
            background: #f0f8ff;
            transform: translateY(-2px);
        }
        .progress-step.completed {
            border-color: #28a745;
            background: #f0fff4;
        }
        .progress-step-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }
        .progress-step-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .progress-step-desc {
            font-size: 12px;
            color: #666;
        }
        .agent-details {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            display: none;
            font-size: 11px;
            text-align: left;
        }
        .agent-details.show {
            display: block;
        }
        .agent-details h4 {
            margin: 0 0 8px 0;
            font-size: 12px;
            color: #333;
        }
        .agent-details ul {
            margin: 0;
            padding-left: 15px;
        }
        .agent-details li {
            margin: 3px 0;
        }
        .toggle-details {
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            font-size: 11px;
            margin-top: 5px;
            text-decoration: underline;
        }
        .toggle-details:hover {
            color: #5a6fd8;
        }
        .chat-panel {
            margin-top: 30px;
            background: #f8f9ff;
            border: 1px solid #e0e0ff;
            border-radius: 8px;
            padding: 20px;
        }
        .chat-panel h2 {
            margin-top: 0;
            margin-bottom: 10px;
        }
        .api-key-panel {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-bottom: 12px;
        }
        .api-key-panel label {
            font-weight: 600;
        }
        .api-key-panel input {
            flex: 1;
            min-width: 220px;
            padding: 8px 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 14px;
        }
        .api-key-panel button {
            background: #17a2b8;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            cursor: pointer;
        }
        .api-key-panel button:disabled {
            background: #9bc7d2;
            cursor: not-allowed;
        }
        .api-key-status {
            flex-basis: 100%;
            font-size: 12px;
            min-height: 18px;
        }
        .privacy-note {
            display: block;
            font-size: 12px;
            color: #555;
            margin-top: 4px;
        }
        .provider-select {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        .provider-select select {
            flex: 0 0 180px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        .chat-history {
            border: 1px solid #ddd;
            border-radius: 6px;
            background: white;
            min-height: 160px;
            max-height: 240px;
            overflow-y: auto;
            padding: 12px;
            margin-bottom: 12px;
            font-size: 14px;
        }
        .chat-message {
            margin-bottom: 12px;
        }
        .chat-message strong {
            display: block;
            margin-bottom: 4px;
        }
        .chat-input {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .chat-input textarea {
            flex: 1;
            min-height: 80px;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
            resize: vertical;
        }
        .chat-input button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            cursor: pointer;
        }
        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .chat-status {
            margin-top: 6px;
            font-size: 12px;
            color: #555;
            min-height: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="/assets/images/TrustBench.png" alt="Trust Bench Logo" class="logo">
        <p class="subtitle">AI-powered repository security and quality analysis</p>
        
        <form id="auditForm">
            <div class="form-group">
                <label for="repoUrl">GitHub Repository URL:</label>
                <input type="url" id="repoUrl" name="repoUrl" 
                       placeholder="Enter GitHub repo URL (e.g., https://github.com/owner/repo)" 
                       required>
                <small style="color: #666; display: block; margin-top: 5px;">
                    💡 Paste any public GitHub repository URL to analyze its security, quality, and documentation
                </small>
            </div>
            
            <button type="submit" class="btn" id="analyzeBtn">🔍 Analyze Repository</button>
        </form>
        
        <div class="progress-workflow" id="progressWorkflow" style="display: none;">
            <!-- Input -->
            <div class="progress-step progress-single" id="step-input">
                <div class="progress-step-icon">📥</div>
                <div class="progress-step-title">Input</div>
                <div class="progress-step-desc">GitHub URL received</div>
            </div>
            
            <!-- Orchestrator -->
            <div class="progress-step progress-single" id="step-orchestration">
                <div class="progress-step-icon">🎯</div>
                <div class="progress-step-title">Orchestrator</div>
                <div class="progress-step-desc">Manager assigns tasks to specialized agents</div>
                <button class="toggle-details" onclick="toggleDetails('orchestrator-details')">Show Details ▼</button>
                <div class="agent-details" id="orchestrator-details">
                    <h4>🎯 Orchestrator Capabilities:</h4>
                    <ul>
                        <li><strong>Task Management:</strong> Coordinates all agent activities</li>
                        <li><strong>Workflow Control:</strong> Manages analysis sequence and timing</li>
                        <li><strong>Collaboration Facilitation:</strong> Enables direct agent-to-agent communication</li>
                        <li><strong>Result Compilation:</strong> Combines collaborative findings into final score</li>
                        <li><strong>Quality Assurance:</strong> Tracks collaboration metrics and adjustments</li>
                    </ul>
                </div>
            </div>
            
            <!-- Three Agents Working in Parallel -->
            <div class="progress-agents">
                <div class="progress-step" id="step-security">
                    <div class="progress-step-icon">🔒</div>
                    <div class="progress-step-title">Security Agent</div>
                    <div class="progress-step-desc">Scanning for secrets & vulnerabilities</div>
                    <button class="toggle-details" onclick="toggleDetails('security-details')">Show Details ▼</button>
                    <div class="agent-details" id="security-details">
                        <h4>🔒 Security Scanning & Collaboration:</h4>
                        <ul>
                            <li><strong>Secret Detection:</strong> API keys, tokens, passwords</li>
                            <li><strong>Credential Scanning:</strong> AWS keys, GitHub tokens, DB strings</li>
                            <li><strong>Risk Assessment:</strong> Categorizes findings by risk level</li>
                            <li><strong>Collaborative Alerts:</strong> Notifies other agents about security context</li>
                            <li><strong>Cross-Agent Impact:</strong> Findings influence quality and documentation scores</li>
                        </ul>
                    </div>
                </div>
                <div class="progress-step" id="step-quality">
                    <div class="progress-step-icon">⚡</div>
                    <div class="progress-step-title">Quality Agent</div>
                    <div class="progress-step-desc">Analyzing code & tests</div>
                    <button class="toggle-details" onclick="toggleDetails('quality-details')">Show Details ▼</button>
                    <div class="agent-details" id="quality-details">
                        <h4>⚡ Code Quality & Cross-Analysis:</h4>
                        <ul>
                            <li><strong>Language Detection:</strong> Identifies programming languages</li>
                            <li><strong>Security Integration:</strong> Adjusts scores based on security findings</li>
                            <li><strong>Test Coverage:</strong> Calculates test-to-code ratios</li>
                            <li><strong>Collaborative Metrics:</strong> Shares quality data with documentation agent</li>
                            <li><strong>Dynamic Scoring:</strong> Adapts assessment based on security context</li>
                        </ul>
                    </div>
                </div>
                <div class="progress-step" id="step-documentation">
                    <div class="progress-step-icon">📚</div>
                    <div class="progress-step-title">Documentation Agent</div>
                    <div class="progress-step-desc">Reviewing docs & READMEs</div>
                    <button class="toggle-details" onclick="toggleDetails('documentation-details')">Show Details ▼</button>
                    <div class="agent-details" id="documentation-details">
                        <h4>📚 Documentation & Context Analysis:</h4>
                        <ul>
                            <li><strong>README Evaluation:</strong> Quality, length, structure</li>
                            <li><strong>Quality-Aware Scoring:</strong> Adjusts expectations based on project size/complexity</li>
                            <li><strong>Security Gap Detection:</strong> Identifies missing security documentation</li>
                            <li><strong>Cross-Agent Communication:</strong> Collaborates with quality and security teams</li>
                            <li><strong>Contextual Assessment:</strong> Adapts scoring based on collaborative insights</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Results -->
            <div class="progress-step progress-single" id="step-results">
                <div class="progress-step-icon">📊</div>
                <div class="progress-step-title">Results</div>
                <div class="progress-step-desc">Scores compiled and comprehensive report generated</div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <h3>
                <img src="/assets/images/TrustBench.png" alt="Trust Bench Logo" style="height: 48px; width: 48px; margin-right: 12px; vertical-align: middle;">
                Agents are analyzing your repository...
            </h3>
            <p>📥 Cloning repository...</p>
            <p>🔒 SecurityAgent scanning for vulnerabilities and secrets...</p>
            <p>⚡ QualityAgent checking code quality and test coverage...</p>
            <p>📚 DocumentationAgent reviewing documentation...</p>
            <p><em>This may take 30-60 seconds for large repositories</em></p>
        </div>
        
        <div class="results" id="results">
            <h2>📊 Analysis Results</h2>
            <div id="resultsContent"></div>
        </div>
        <div class="chat-panel" id="chatPanel">
            <div class="api-key-panel">
                <label for="apiKeyInput">API Key:</label>
                <input type="password" id="apiKeyInput" autocomplete="off" placeholder="Paste your key for selected provider">
                <button type="button" id="testKeyBtn">Test Connection</button>
                <span class="api-key-status" id="apiKeyStatus"></span>
                <span class="privacy-note">Your API key is never stored or tracked. It is used only for this session and never leaves your browser except to test or send a chat request.</span>
            </div>
            <h2>Ask the Agents</h2>
            <div class="provider-select">
                <label for="providerSelect">LLM Provider:</label>
                <select id="providerSelect">
                    <option value="openai">OpenAI</option>
                    <option value="groq">Groq</option>
                    <option value="gemini">Gemini</option>
                </select>
            </div>
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

    <script>
        const defaultProvider = "{{ default_provider }}";

        const chatPanel = document.getElementById('chatPanel');
        const providerSelect = document.getElementById('providerSelect');
        const apiKeyInput = document.getElementById('apiKeyInput');
        const testKeyBtn = document.getElementById('testKeyBtn');
        const apiKeyStatus = document.getElementById('apiKeyStatus');
        const chatHistory = document.getElementById('chatHistory');
        const chatQuestion = document.getElementById('chatQuestion');
        const chatStatus = document.getElementById('chatStatus');
        const chatPlaceholder = document.getElementById('chatPlaceholder');
        const sendChatBtn = document.getElementById('sendChatBtn');

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
                // Ignore storage errors (e.g., private browsing restrictions).
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
            chatStatus.textContent = message || '';
            chatStatus.style.color = isError ? '#b00020' : '#555';
        }

        async function sendChatMessage() {
            if (!chatQuestion || !sendChatBtn) {
                return;
            }

            const question = chatQuestion.value.trim();
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
                const payload = {
                    question,
                    provider,
                };
                if (apiKey) {
                    payload.api_key = apiKey;
                }

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();

                if (!data.success) {
                    appendChatMessage('System', data.error || 'The provider did not return a response.');
                    updateChatStatus(data.error || 'The provider did not return a response.', true);
                    return;
                }

                const providerLabel = (data.provider || provider || 'provider').toUpperCase();
                appendChatMessage(providerLabel, data.answer || '(No answer returned)');

                if (data.context_available) {
                    const sourceNote = data.context_source ? ` (${data.context_source})` : '';
                    updateChatStatus(`Answered using the latest report context${sourceNote}.`);
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

        if (chatStatus) {
            chatStatus.textContent = 'Run an analysis to capture the latest context.';
        }
        if (providerSelect && defaultProvider) {
            providerSelect.value = defaultProvider;
        }
        if (providerSelect && apiKeyInput) {
            providerSelect.addEventListener('change', () => updateApiKeyInput());
            apiKeyInput.addEventListener('input', () => {
                setApiKey(providerSelect.value, apiKeyInput.value.trim());
                if (apiKeyStatus) {
                    apiKeyStatus.textContent = '';
                    apiKeyStatus.style.color = '#555';
                }
            });
            updateApiKeyInput(false);
        }
        if (sendChatBtn) {
            sendChatBtn.addEventListener('click', sendChatMessage);
        }
        if (chatQuestion) {
            chatQuestion.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendChatMessage();
                }
            });
        }
        if (testKeyBtn && apiKeyInput && providerSelect) {
            testKeyBtn.addEventListener('click', async function() {
                const provider = providerSelect.value;
                const apiKey = apiKeyInput.value.trim();

                if (!apiKeyStatus) {
                    return;
                }
                if (!provider) {
                    apiKeyStatus.textContent = 'Select a provider first.';
                    apiKeyStatus.style.color = '#b00020';
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
                    const resp = await fetch('/api/test-llm-key', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ provider, api_key: apiKey }),
                    });
                    const data = await resp.json();
                    if (data.success) {
                        apiKeyStatus.textContent = 'Connection successful!';
                        apiKeyStatus.style.color = '#28a745';
                        setApiKey(provider, apiKey);
                    } else {
                        apiKeyStatus.textContent = data.error || 'Connection failed.';
                        apiKeyStatus.style.color = '#b00020';
                    }
                } catch (err) {
                    apiKeyStatus.textContent = 'Unable to reach the server.';
                    apiKeyStatus.style.color = '#b00020';
                } finally {
                    testKeyBtn.disabled = false;
                }
            });
        }

        document.getElementById('auditForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const repoUrl = document.getElementById('repoUrl').value;
            const analyzeBtn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const progressWorkflow = document.getElementById('progressWorkflow');
            
            // Validate GitHub URL
            if (!isValidGitHubUrl(repoUrl)) {
                alert('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
                return;
            }
            
            // Show progress workflow and start analysis
            progressWorkflow.style.display = 'flex';
            results.style.display = 'none';
            
            // Step 1: Input received
            updateProgressStep('step-input', 'active');
            await sleep(500);
            updateProgressStep('step-input', 'completed');
            
            // Step 2: Orchestration
            updateProgressStep('step-orchestration', 'active');
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '🔄 Cloning and Analyzing...';
            loading.style.display = 'block';
            updateChatStatus('Generating a fresh report for your repository...');
            await sleep(1000);
            
            try {
                updateProgressStep('step-orchestration', 'completed');
                
                // Step 3: Agents working in parallel
                updateProgressStep('step-security', 'active');
                updateProgressStep('step-quality', 'active');
                updateProgressStep('step-documentation', 'active');
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ repo_url: repoUrl })
                });
                
                const data = await response.json();
                
                // Complete all agent steps
                updateProgressStep('step-security', 'completed');
                updateProgressStep('step-quality', 'completed');
                updateProgressStep('step-documentation', 'completed');
                
                // Step 4: Results
                updateProgressStep('step-results', 'active');
                await sleep(500);
                
                if (data.success) {
                    displayResults(data.report);
                    updateProgressStep('step-results', 'completed');

                    const repoInfo = data.report && data.report.repository_info;
                    if (repoInfo && repoInfo.owner && repoInfo.name) {
                        updateChatStatus(`Latest context loaded from ${repoInfo.owner}/${repoInfo.name}. Ask a follow-up question anytime.`);
                        if (chatPlaceholder && chatPlaceholder.parentElement) {
                            const placeholderBody = chatPlaceholder.querySelector('span');
                            if (placeholderBody) {
                                placeholderBody.textContent = `Context ready for ${repoInfo.owner}/${repoInfo.name}. Ask a question whenever you're ready.`;
                            }
                        }
                    } else {
                        updateChatStatus('Latest context loaded. Ask a follow-up question anytime.');
                        if (chatPlaceholder && chatPlaceholder.parentElement) {
                            const placeholderBody = chatPlaceholder.querySelector('span');
                            if (placeholderBody) {
                                placeholderBody.textContent = 'Latest context loaded. Ask a follow-up question anytime.';
                            }
                        }
                    }
                } else {
                    document.getElementById('resultsContent').innerHTML = 
                        '<div style="color: red;"><h3>Error:</h3><p>' + data.error + '</p></div>';
                    resetProgressSteps();
                    updateChatStatus(data.error || 'Analysis failed to complete.', true);
                }
                
                results.style.display = 'block';
            } catch (error) {
                document.getElementById('resultsContent').innerHTML = 
                    '<div style="color: red;"><h3>Error:</h3><p>' + error.message + '</p></div>';
                results.style.display = 'block';
                updateChatStatus(error.message || 'Unexpected error during analysis.', true);
                resetProgressSteps();
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🔍 Analyze Repository';
                loading.style.display = 'none';
            }
        });
        function updateProgressStep(stepId, state) {
            const step = document.getElementById(stepId);
            step.className = 'progress-step ' + state;
        }
        
        function resetProgressSteps() {
            ['step-input', 'step-orchestration', 'step-security', 'step-quality', 'step-documentation', 'step-results'].forEach(id => {
                document.getElementById(id).className = 'progress-step';
            });
        }
        
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
        function toggleDetails(detailsId) {
            const details = document.getElementById(detailsId);
            const button = details.previousElementSibling;
            
            if (details.classList.contains('show')) {
                details.classList.remove('show');
                button.innerHTML = 'Show Details ▼';
            } else {
                details.classList.add('show');
                button.innerHTML = 'Hide Details ▲';
            }
        }
        
        function isValidGitHubUrl(url) {
            try {
                const parsed = new URL(url);
                return parsed.hostname === 'github.com' && 
                       parsed.pathname.split('/').length >= 3 &&
                       parsed.pathname.split('/')[1] !== '' &&
                       parsed.pathname.split('/')[2] !== '';
            } catch {
                return false;
            }
        }
        
        function displayResults(report) {
            const summary = report.summary;
            const agents = report.agents;
            const repoInfo = report.repository_info;
            
            let html = `
                <div style="margin-bottom: 20px; padding: 15px; background: #f0f8ff; border-radius: 5px;">
                    <h3>📦 Repository: <a href="${repoInfo.url}" target="_blank">${repoInfo.owner}/${repoInfo.name}</a></h3>
                </div>
                
                <div class="score ${summary.grade}">
                    Overall Score: ${summary.overall_score}/100
                    <br>Grade: ${summary.grade.toUpperCase()}
                </div>
                
                <div class="agent-results">
            `;
            
            for (const [agentName, agentData] of Object.entries(agents)) {
                html += `
                    <div class="agent-card">
                        <h3>${agentName}</h3>
                        <p><strong>Score:</strong> ${agentData.score}/100</p>
                        <p><strong>Summary:</strong> ${agentData.summary}</p>
                    </div>
                `;
            }
            
            html += '</div>';
            
            // Add conversation log
            if (report.conversation && report.conversation.length > 0) {
                html += '<h3>🗣️ Agent Conversation Log</h3><ul>';
                report.conversation.forEach(msg => {
                    html += `<li><strong>${msg.sender} → ${msg.recipient}:</strong> ${msg.content}</li>`;
                });
                html += '</ul>';
            }
            
            document.getElementById('resultsContent').innerHTML = html;
        }
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
        data = request.json
        repo_url = data.get('repo_url', '')
        
        # Validate GitHub URL
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



@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON payload.'
        }), 400

    question = str(payload.get('question', '') or '').strip()
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
    print("🚀 Starting Trust Bench Multi-Agent Auditor Web Interface...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🔍 Ready to analyze repositories!")
    app.run(debug=True, host='0.0.0.0', port=5000)
