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
        .metric-slider {
            width: 100%;
            margin: 8px 0;
            -webkit-appearance: none;
            height: 6px;
            border-radius: 3px;
            background: #dfe3ff;
            outline: none;
        }
        .metric-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
        }
        .metric-slider::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            border: none;
        }
        .metric-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            margin-bottom: 4px;
            color: #555d82;
        }
        .metric-value {
            font-weight: 600;
            color: var(--accent);
        }
        .agent-metric-group {
            margin-bottom: 16px;
            padding: 12px;
            background: #f0f2ff;
            border-radius: 8px;
        }
        .agent-metric-title {
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 8px;
            font-size: 13px;
        }
        .eval-preset-btn {
            background: #eef0ff;
            color: var(--accent);
            padding: 6px 12px;
            border: 1px solid #ccd2ff;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin: 2px;
        }
        .eval-preset-btn.active {
            background: var(--primary);
            color: white;
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
        .confidence-meter {
            margin: 12px 0;
        }
        .confidence-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            margin-bottom: 6px;
            color: #555d82;
        }
        .confidence-bar {
            width: 100%;
            height: 8px;
            background: #e5e7fb;
            border-radius: 4px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .confidence-high { background: #28a745; }
        .confidence-medium { background: #ffc107; }
        .confidence-low { background: #dc3545; }
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
        
        /* Agent-specific chat styling */
        .chat-message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 8px;
            background: #f9faff;
        }
        
        .agent-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            gap: 8px;
        }
        
        .agent-avatar {
            font-size: 18px;
        }
        
        .agent-info {
            flex: 1;
        }
        
        .agent-name {
            font-weight: 600;
            color: var(--accent);
            font-size: 14px;
        }
        
        .agent-role {
            font-size: 11px;
            color: #6b7280;
            display: block;
        }
        
        .confidence-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
        }
        
        .confidence-badge.high {
            background: #10b981;
        }
        
        .confidence-badge.medium {
            background: #f59e0b;
        }
        
        .confidence-badge.low {
            background: #ef4444;
        }
        
        .agent-response {
            line-height: 1.5;
        }
        
        .chat-message.agent-security {
            border-left: 4px solid #dc2626;
            background: #fef2f2;
        }
        
        .chat-message.agent-quality {
            border-left: 4px solid #2563eb;
            background: #eff6ff;
        }
        
        .chat-message.agent-docs {
            border-left: 4px solid #16a34a;
            background: #f0fdf4;
        }
        
        .chat-message.agent-orchestrator {
            border-left: 4px solid #7c3aed;
            background: #f3f4f6;
        }
        
        .chat-message.agent-generic {
            border-left: 4px solid #6b7280;
            background: #f9fafb;
        }
        
        .routing-info {
            font-size: 12px;
            color: #6b7280;
            font-style: italic;
            margin-bottom: 8px;
            padding: 4px 8px;
            background: #f3f4f6;
            border-radius: 4px;
        }
        
        /* Phase 3: Advanced Orchestration Styling */
        .orchestration-banner {
            margin: 8px 0;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }
        
        .orchestration-banner.phase3 {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            color: white;
            box-shadow: 0 2px 4px rgba(124, 58, 237, 0.2);
        }
        
        .orchestration-process {
            margin: 8px 0;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            background: #fafafa;
        }
        
        .process-header {
            padding: 8px 12px;
            background: #f3f4f6;
            border-bottom: 1px solid #e5e7eb;
            font-size: 12px;
            font-weight: 500;
            color: #374151;
        }
        
        .process-header:hover {
            background: #e5e7eb;
        }
        
        .process-details {
            padding: 8px 12px;
        }
        
        .process-step {
            font-size: 11px;
            color: #6b7280;
            padding: 2px 0;
            border-left: 2px solid #d1d5db;
            padding-left: 8px;
            margin: 4px 0;
        }
        
        .consensus-status {
            margin: 8px 0;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .consensus-status.achieved {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        
        .consensus-status.partial {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        .chat-message.agent-advanced-orchestrator {
            border-left: 4px solid #7c3aed;
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1);
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
            <div class="sidebar-section">
                <h3>Evaluation Metrics</h3>
                <p style="margin: 0 0 8px; font-weight: 600; color: #2f2f44;">Customize Agent Weights</p>
                
                <div style="margin-bottom: 12px;">
                    <button type="button" class="eval-preset-btn active" id="preset-default">Default</button>
                    <button type="button" class="eval-preset-btn" id="preset-security">Security Focus</button>
                    <button type="button" class="eval-preset-btn" id="preset-quality">Quality Focus</button>
                    <button type="button" class="eval-preset-btn" id="preset-docs">Docs Focus</button>
                </div>

                <div class="agent-metric-group">
                    <div class="agent-metric-title">🛡️ Security Agent</div>
                    <div class="metric-label">
                        <span>Weight</span>
                        <span class="metric-value" id="security-weight-value">33%</span>
                    </div>
                    <input type="range" class="metric-slider" id="security-weight" min="10" max="70" value="33">
                </div>

                <div class="agent-metric-group">
                    <div class="agent-metric-title">🏗️ Quality Agent</div>
                    <div class="metric-label">
                        <span>Weight</span>
                        <span class="metric-value" id="quality-weight-value">33%</span>
                    </div>
                    <input type="range" class="metric-slider" id="quality-weight" min="10" max="70" value="33">
                </div>

                <div class="agent-metric-group">
                    <div class="agent-metric-title">📚 Documentation Agent</div>
                    <div class="metric-label">
                        <span>Weight</span>
                        <span class="metric-value" id="docs-weight-value">34%</span>
                    </div>
                    <input type="range" class="metric-slider" id="docs-weight" min="10" max="70" value="34">
                </div>
                
                <div id="weight-preview" style="margin-top: 15px; padding: 12px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #007acc;">
                    <div style="font-weight: 600; color: #2f2f44; margin-bottom: 8px;">Score Preview</div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 6px;">Based on last analysis results:</div>
                    <div id="score-preview-content">
                        <div style="color: #999; font-style: italic;">Run an analysis to see weighted score preview</div>
                    </div>
                </div>
                
                <span class="privacy-note">Agent weights are automatically balanced and affect overall scoring calculations.</span>
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
                text = text.replace(/[\\0-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]/g, '');
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

            function formatResponse(text) {
                if (!text) return '';
                
                // Basic text formatting for chat responses
                return text
                    .replace(/\\n/g, '<br>')
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                    .replace(/`(.*?)`/g, '<code>$1</code>');
            }

            const auditForm = document.getElementById('auditForm');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const repoUrlInput = document.getElementById('repoUrl');
            const providerSelect = document.getElementById('providerSelect');
            const apiKeyInput = document.getElementById('apiKeyInput');
            const testKeyBtn = document.getElementById('testKeyBtn');
            
            // Debug: Check if elements are found
            console.log('Element check:', {
                auditForm: !!auditForm,
                analyzeBtn: !!analyzeBtn,
                testKeyBtn: !!testKeyBtn,
                repoUrlInput: !!repoUrlInput,
                providerSelect: !!providerSelect,
                apiKeyInput: !!apiKeyInput
            });
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
            
            // Evaluation metrics elements
            const securityWeightSlider = document.getElementById('security-weight');
            const qualityWeightSlider = document.getElementById('quality-weight');
            const docsWeightSlider = document.getElementById('docs-weight');
            const securityWeightValue = document.getElementById('security-weight-value');
            const qualityWeightValue = document.getElementById('quality-weight-value');
            const docsWeightValue = document.getElementById('docs-weight-value');
            const presetDefaultBtn = document.getElementById('preset-default');
            const presetSecurityBtn = document.getElementById('preset-security');
            const presetQualityBtn = document.getElementById('preset-quality');
            const presetDocsBtn = document.getElementById('preset-docs');

            let latestReportPath = null;

            // Evaluation metrics functionality
            let currentEvalWeights = { security: 33, quality: 33, docs: 34 };

            function updateWeightDisplay(agent, value) {
                const displayElement = document.getElementById(`${agent}-weight-value`);
                if (displayElement) {
                    displayElement.textContent = `${value}%`;
                }
                currentEvalWeights[agent] = parseInt(value);
            }

            function balanceWeights(changedAgent, newValue) {
                const total = 100;
                const otherAgents = Object.keys(currentEvalWeights).filter(a => a !== changedAgent);
                const remainingWeight = total - newValue;
                
                // Distribute remaining weight proportionally among other agents
                const currentOthersTotal = otherAgents.reduce((sum, agent) => sum + currentEvalWeights[agent], 0);
                
                otherAgents.forEach(agent => {
                    const proportion = currentEvalWeights[agent] / currentOthersTotal;
                    const newAgentWeight = Math.round(remainingWeight * proportion);
                    currentEvalWeights[agent] = newAgentWeight;
                    
                    const slider = document.getElementById(`${agent}-weight`);
                    if (slider) {
                        slider.value = newAgentWeight;
                        updateWeightDisplay(agent, newAgentWeight);
                    }
                });
                
                currentEvalWeights[changedAgent] = parseInt(newValue);
                updateScorePreview();
            }

            function setEvalPreset(presetName) {
                const presets = {
                    default: { security: 33, quality: 33, docs: 34 },
                    security: { security: 50, quality: 25, docs: 25 },
                    quality: { security: 25, quality: 50, docs: 25 },
                    docs: { security: 25, quality: 25, docs: 50 }
                };

                const preset = presets[presetName];
                if (preset) {
                    Object.keys(preset).forEach(agent => {
                        const slider = document.getElementById(`${agent}-weight`);
                        if (slider) {
                            slider.value = preset[agent];
                            updateWeightDisplay(agent, preset[agent]);
                        }
                    });
                    currentEvalWeights = { ...preset };
                    updateScorePreview();
                }

                // Update active preset button
                document.querySelectorAll('.eval-preset-btn').forEach(btn => btn.classList.remove('active'));
                const activeBtn = document.getElementById(`preset-${presetName}`);
                if (activeBtn) {
                    activeBtn.classList.add('active');
                }
            }

            function getEvalWeights() {
                return { ...currentEvalWeights };
            }

            // Store last analysis results for preview
            let lastAnalysisScores = null;

            function updateScorePreview() {
                const previewContent = document.getElementById('score-preview-content');
                if (!previewContent || !lastAnalysisScores) return;

                const weights = getEvalWeights();
                
                // Calculate weighted score
                const weightedScore = (
                    (lastAnalysisScores.security * weights.security) +
                    (lastAnalysisScores.quality * weights.quality) +
                    (lastAnalysisScores.docs * weights.docs)
                ) / 100;
                
                // Calculate equal-weight score for comparison
                const equalScore = (lastAnalysisScores.security + lastAnalysisScores.quality + lastAnalysisScores.docs) / 3;
                
                const difference = weightedScore - equalScore;
                const diffText = difference > 0 ? 
                    `+${difference.toFixed(1)}` : 
                    difference.toFixed(1);
                
                previewContent.innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>Weighted Score:</span>
                        <span style="font-weight: 600;">${weightedScore.toFixed(1)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>Equal Weight:</span>
                        <span>${equalScore.toFixed(1)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: ${difference >= 0 ? '#28a745' : '#dc3545'};">
                        <span>Difference:</span>
                        <span>${diffText}</span>
                    </div>
                `;
            }

            function setLastAnalysisScores(scores) {
                lastAnalysisScores = scores;
                updateScorePreview();
            }

            function getApiKey(provider) {
                if (!provider) {
                    console.log('DEBUG: getApiKey called with empty provider');
                    return '';
                }
                try {
                    const key = sessionStorage.getItem(`llm_api_key_${provider}`) || '';
                    console.log(`DEBUG: getApiKey(${provider}) = ${key ? '[KEY_EXISTS]' : '[NO_KEY]'}`);
                    return key;
                } catch (err) {
                    console.log('DEBUG: getApiKey error:', err);
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

            function appendChatMessage(author, text, agentData = null) {
                if (!chatHistory) {
                    return;
                }
                if (chatPlaceholder && chatPlaceholder.parentElement) {
                    chatPlaceholder.parentElement.removeChild(chatPlaceholder);
                }
                
                const wrapper = document.createElement('div');
                
                if (agentData && agentData.agent) {
                    // Agent-specific message styling
                    wrapper.className = `chat-message agent-${agentData.agent}`;
                    
                    // Agent header with avatar and info
                    const agentHeader = document.createElement('div');
                    agentHeader.className = 'agent-header';
                    
                    const avatar = document.createElement('span');
                    avatar.className = 'agent-avatar';
                    avatar.textContent = getAgentAvatar(agentData.agent);
                    
                    const agentInfo = document.createElement('div');
                    agentInfo.className = 'agent-info';
                    
                    const agentName = document.createElement('span');
                    agentName.className = 'agent-name';
                    agentName.textContent = getAgentName(agentData.agent);
                    
                    const agentRole = document.createElement('span');
                    agentRole.className = 'agent-role';
                    agentRole.textContent = getAgentRole(agentData.agent);
                    
                    agentInfo.appendChild(agentName);
                    agentInfo.appendChild(agentRole);
                    
                    const confidenceBadge = document.createElement('span');
                    confidenceBadge.className = `confidence-badge ${getConfidenceLevel(agentData.confidence)}`;
                    confidenceBadge.textContent = `${Math.round((agentData.confidence || 0.5) * 100)}%`;
                    
                    agentHeader.appendChild(avatar);
                    agentHeader.appendChild(agentInfo);
                    agentHeader.appendChild(confidenceBadge);
                    wrapper.appendChild(agentHeader);
                    
                    // Show routing reason if available
                    if (agentData.routing_reason) {
                        const routingInfo = document.createElement('div');
                        routingInfo.className = 'routing-info';
                        routingInfo.textContent = `🎯 ${agentData.routing_reason}`;
                        wrapper.appendChild(routingInfo);
                    }
                    
                    // Phase 3: Advanced orchestration indicators
                    if (agentData.orchestration_level === 'phase3') {
                        const orchestrationBanner = document.createElement('div');
                        orchestrationBanner.className = 'orchestration-banner phase3';
                        orchestrationBanner.innerHTML = '🚀 <strong>Phase 3 Advanced Orchestration</strong> - Consensus Building & Conflict Resolution';
                        wrapper.appendChild(orchestrationBanner);
                        
                        // Show orchestration process if available
                        if (agentData.orchestration_log && agentData.orchestration_log.length > 0) {
                            const orchestrationProcess = document.createElement('div');
                            orchestrationProcess.className = 'orchestration-process';
                            
                            const processHeader = document.createElement('div');
                            processHeader.className = 'process-header';
                            processHeader.innerHTML = '🔄 <strong>Orchestration Process</strong>';
                            processHeader.style.cursor = 'pointer';
                            processHeader.onclick = () => {
                                const details = orchestrationProcess.querySelector('.process-details');
                                details.style.display = details.style.display === 'none' ? 'block' : 'none';
                            };
                            orchestrationProcess.appendChild(processHeader);
                            
                            const processDetails = document.createElement('div');
                            processDetails.className = 'process-details';
                            processDetails.style.display = 'none';
                            
                            agentData.orchestration_log.forEach(logEntry => {
                                const logItem = document.createElement('div');
                                logItem.className = 'process-step';
                                logItem.textContent = logEntry;
                                processDetails.appendChild(logItem);
                            });
                            
                            orchestrationProcess.appendChild(processDetails);
                            wrapper.appendChild(orchestrationProcess);
                        }
                        
                        // Show consensus status
                        if (agentData.consensus_achieved !== undefined) {
                            const consensusStatus = document.createElement('div');
                            consensusStatus.className = `consensus-status ${agentData.consensus_achieved ? 'achieved' : 'partial'}`;
                            consensusStatus.innerHTML = agentData.consensus_achieved ? 
                                '✅ <strong>Consensus Achieved</strong>' : 
                                '⚖️ <strong>Partial Consensus</strong> - Some conflicts remain';
                            wrapper.appendChild(consensusStatus);
                        }
                    }
                    
                    const responseDiv = document.createElement('div');
                    responseDiv.className = 'agent-response';
                    responseDiv.innerHTML = formatResponse(text);
                    wrapper.appendChild(responseDiv);
                    
                } else {
                    // Standard message format (user messages)
                    wrapper.className = 'chat-message';
                    
                    const label = document.createElement('strong');
                    label.textContent = author;
                    wrapper.appendChild(label);

                    const body = document.createElement('div');
                    body.textContent = text;
                    wrapper.appendChild(body);
                }

                chatHistory.appendChild(wrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
            
            function getAgentAvatar(agentType) {
                const avatars = {
                    'security': '🛡️',
                    'quality': '🏗️',
                    'docs': '📚',
                    'orchestrator': '🎯',
                    'generic': '🤖'
                };
                return avatars[agentType] || '🤖';
            }
            
            function getAgentName(agentType) {
                const names = {
                    'security': 'Security Agent',
                    'quality': 'Quality Agent', 
                    'docs': 'Documentation Agent',
                    'orchestrator': 'Orchestrator',
                    'generic': 'Assistant'
                };
                return names[agentType] || 'Assistant';
            }
            
            function getAgentRole(agentType) {
                const roles = {
                    'security': 'Vulnerability & Risk Assessment',
                    'quality': 'Code Quality & Architecture',
                    'docs': 'Developer Experience & Documentation',
                    'orchestrator': 'Multi-Agent Coordination',
                    'generic': 'General Assistant'
                };
                return roles[agentType] || 'General Assistant';
            }
            
            function getConfidenceLevel(confidence) {
                if (confidence >= 0.8) return 'high';
                if (confidence >= 0.6) return 'medium';
                return 'low';
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
                let apiKey = provider ? getApiKey(provider) : '';
                
                // Fallback: if no API key in sessionStorage, try to get it from input field
                if (!apiKey && apiKeyInput && apiKeyInput.value) {
                    apiKey = sanitizeInput(apiKeyInput.value, 200);
                    console.log('DEBUG: Using API key from input field as fallback');
                }

                appendChatMessage('You', question);
                chatQuestion.value = '';
                updateChatStatus('Waiting for response...');
                sendChatBtn.disabled = true;

                try {
                    const payload = { question, provider };
                    console.log('DEBUG: Chat request - provider:', provider, 'apiKey exists:', !!apiKey);
                    if (apiKey) {
                        payload.api_key = apiKey;
                        console.log('DEBUG: Added API key to payload');
                    } else {
                        console.log('DEBUG: No API key found - checking sessionStorage...');
                        console.log('DEBUG: sessionStorage keys:', Object.keys(sessionStorage));
                    }

                    console.log('DEBUG: About to send fetch request to /api/chat');
                    console.log('DEBUG: Payload:', payload);
                    
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

                    // Handle agent-specific responses
                    if (data.agent && data.agent !== 'generic') {
                        appendChatMessage('', sanitizeInput(data.answer || '(No answer returned)'), {
                            agent: data.agent,
                            confidence: data.confidence,
                            routing_reason: data.routing_reason
                        });
                        
                        const agentName = getAgentName(data.agent);
                        if (data.context_available) {
                            const sourceNote = data.context_source ? ` (${data.context_source})` : '';
                            updateChatStatus(`${agentName} responded using latest report context${sanitizeInput(sourceNote)}.`);
                        } else {
                            updateChatStatus(`${agentName} responded. Run an analysis for more specific insights.`);
                        }
                    } else {
                        // Generic response
                        const providerLabel = sanitizeInput((data.provider || provider || 'provider').toUpperCase());
                        appendChatMessage(providerLabel, sanitizeInput(data.answer || '(No answer returned)'));

                        if (data.context_available) {
                            const sourceNote = data.context_source ? ` (${data.context_source})` : '';
                            updateChatStatus(`Answered using the latest report context${sanitizeInput(sourceNote)}.`);
                        } else {
                            updateChatStatus('Answered without local report context. Run an analysis for better results.');
                        }
                    }
                } catch (error) {
                    console.error('DEBUG: Chat error details:', error);
                    const errorMsg = `Chat error: ${error.message || error}`;
                    appendChatMessage('System', errorMsg);
                    updateChatStatus(errorMsg, true);
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
                const metrics = report.metrics || {};
                const agents = report.agents || {};

                // Capture individual scores for weight preview
                const individualScores = summary.individual_scores;
                if (individualScores) {
                    setLastAnalysisScores({
                        security: individualScores.security || 0,
                        quality: individualScores.quality || 0,
                        docs: individualScores.documentation || 0
                    });
                }

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

                if (metrics && Object.keys(metrics).length > 0) {
                    const systemLatency = typeof metrics.system_latency_seconds !== 'undefined'
                        ? escapeHtml(metrics.system_latency_seconds)
                        : 'n/a';
                    const faithfulness = typeof metrics.faithfulness !== 'undefined'
                        ? escapeHtml(metrics.faithfulness)
                        : 'n/a';
                    const refusalAccuracy = typeof metrics.refusal_accuracy !== 'undefined'
                        ? escapeHtml(metrics.refusal_accuracy)
                        : 'n/a';
                    const perAgent = metrics.per_agent_latency || {};
                    const perAgentRows = Object.entries(perAgent).map(([agentName, timing]) => {
                        const total = timing && typeof timing.total_seconds !== 'undefined'
                            ? escapeHtml(timing.total_seconds)
                            : 'n/a';
                        const toolBreakdown = timing && timing.tool_breakdown
                            ? Object.entries(timing.tool_breakdown)
                                .map(([tool, value]) => `<li>${escapeHtml(tool)}: ${escapeHtml(value)} s</li>`)
                                .join('')
                            : '';
                        const toolsHtml = toolBreakdown
                            ? `<ul class="metric-breakdown">${toolBreakdown}</ul>`
                            : '';
                        return `
                            <div class="metric-row">
                                <strong>${escapeHtml(agentName)}:</strong> ${total} s
                                ${toolsHtml}
                            </div>
                        `;
                    }).join('');

                    html += `
                        <div class="agent-card metrics-card">
                            <h3>Instrumentation Metrics</h3>
                            <p><strong>System latency:</strong> ${systemLatency} s</p>
                            <p><strong>Faithfulness:</strong> ${faithfulness}</p>
                            <p><strong>Refusal accuracy:</strong> ${refusalAccuracy}</p>
                            ${perAgentRows ? `<div class="metric-section">${perAgentRows}</div>` : ''}
                        </div>
                    `;
                }

                html += '<div class="agent-results">';
                const confidenceScores = report.confidence_scores || {};
                
                Object.entries(agents).forEach(([agentName, agentData]) => {
                    const score = typeof agentData.score !== 'undefined' ? agentData.score : 'N/A';
                    const summaryText = agentData.summary || 'No summary available.';
                    const confidence = confidenceScores[agentName] || 0.0;
                    const confidencePercent = Math.round(confidence * 100);
                    
                    // Determine confidence level and color
                    let confidenceClass, confidenceIcon;
                    if (confidence >= 0.8) {
                        confidenceClass = 'confidence-high';
                        confidenceIcon = '🟢';
                    } else if (confidence >= 0.5) {
                        confidenceClass = 'confidence-medium';
                        confidenceIcon = '🟡';
                    } else {
                        confidenceClass = 'confidence-low';
                        confidenceIcon = '🔴';
                    }
                    
                    html += `<div class="agent-card">
                                <h3>${escapeHtml(agentName)}</h3>
                                <p><strong>Score:</strong> ${escapeHtml(score)}</p>
                                <div class="confidence-meter">
                                    <div class="confidence-label">
                                        <span>Confidence ${confidenceIcon}</span>
                                        <span>${confidencePercent}%</span>
                                    </div>
                                    <div class="confidence-bar">
                                        <div class="confidence-fill ${confidenceClass}" style="width: ${confidencePercent}%"></div>
                                    </div>
                                </div>
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

            // Initialize evaluation metrics controls
            if (securityWeightSlider && qualityWeightSlider && docsWeightSlider) {
                securityWeightSlider.addEventListener('input', (event) => {
                    const newValue = parseInt(event.target.value);
                    balanceWeights('security', newValue);
                    updateWeightDisplay('security', newValue);
                });

                qualityWeightSlider.addEventListener('input', (event) => {
                    const newValue = parseInt(event.target.value);
                    balanceWeights('quality', newValue);
                    updateWeightDisplay('quality', newValue);
                });

                docsWeightSlider.addEventListener('input', (event) => {
                    const newValue = parseInt(event.target.value);
                    balanceWeights('docs', newValue);
                    updateWeightDisplay('docs', newValue);
                });
            }

            // Initialize preset buttons
            if (presetDefaultBtn) {
                presetDefaultBtn.addEventListener('click', () => setEvalPreset('default'));
            }
            if (presetSecurityBtn) {
                presetSecurityBtn.addEventListener('click', () => setEvalPreset('security'));
            }
            if (presetQualityBtn) {
                presetQualityBtn.addEventListener('click', () => setEvalPreset('quality'));
            }
            if (presetDocsBtn) {
                presetDocsBtn.addEventListener('click', () => setEvalPreset('docs'));
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
                            body: JSON.stringify({ 
                                repo_url: repoUrl,
                                eval_weights: getEvalWeights()
                            })
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
        eval_weights = data.get('eval_weights', {'security': 33, 'quality': 33, 'docs': 34})
        
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
        
        # Add evaluation weights if provided
        if eval_weights:
            cmd.extend(['--eval-weights', json.dumps(eval_weights)])
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f"Analysis failed: {result.stderr}"
            })
        
        # Read the generated report
        base_dir = Path(__file__).parent.resolve()
        output_path = (base_dir / output_dir).resolve()
        if not str(output_path).startswith(str(base_dir)):
            return jsonify({
                'success': False,
                'error': "Invalid report path"
            })

        report_path = output_path / 'report.json'
        if not report_path.exists():
            return jsonify({
                'success': False,
                'error': "Report file not generated"
            })

        with report_path.open('r', encoding='utf-8') as f:
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
    
    # Debug logging
    print(f"DEBUG: Chat endpoint - provider: {provider}, api_key present: {api_key is not None}, payload keys: {list(payload.keys())}")

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

    if context and context.get('report'):
        # Use orchestrator routing for agent-specific responses
        try:
            from agent_router import OrchestrationRouter
            
            router = OrchestrationRouter(context['report'])
            result = router.route_and_respond(
                question=question,
                provider_override=provider,
                api_key_override=api_key
            )
            
            return jsonify({
                'success': True,
                'answer': result['response'],
                'agent': result['agent'],
                'routing_reason': result['routing_reason'],
                'confidence': result['confidence'],
                'context_available': True,
                'context_source': context.get('report_path')
            })
            
        except ImportError:
            # Fallback to original behavior if router not available
            pass
        except Exception as exc:
            # Log error but continue with fallback
            print(f"Router error: {exc}")
    
    # Fallback to generic LLM response
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
        'agent': 'generic',
        'confidence': 0.5,
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
    print("🌐 Open your browser to: http://localhost:5001")
    print("✨ Ready to analyze repositories!")
    app.run(debug=True, host='0.0.0.0', port=5001)
