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

from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)

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
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
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
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Trust Bench Multi-Agent Auditor</h1>
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
            
            <div class="form-group">
                <label for="presetRepo">Or try a sample repository:</label>
                <select id="presetRepo" name="presetRepo">
                    <option value="">-- Choose a sample --</option>
                    <option value="https://github.com/microsoft/vscode">Microsoft VS Code</option>
                    <option value="https://github.com/facebook/react">Facebook React</option>
                    <option value="https://github.com/tensorflow/tensorflow">TensorFlow</option>
                    <option value="https://github.com/nodejs/node">Node.js</option>
                    <option value="https://github.com/python/cpython">Python</option>
                </select>
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
            <h3>🤖 Agents are analyzing your repository...</h3>
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
    </div>

    <script>
        document.getElementById('presetRepo').addEventListener('change', function() {
            if (this.value) {
                document.getElementById('repoUrl').value = this.value;
            }
        });

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
                } else {
                    document.getElementById('resultsContent').innerHTML = 
                        '<div style="color: red;"><h3>Error:</h3><p>' + data.error + '</p></div>';
                    resetProgressSteps();
                }
                
                results.style.display = 'block';
            } catch (error) {
                document.getElementById('resultsContent').innerHTML = 
                    '<div style="color: red;"><h3>Error:</h3><p>' + error.message + '</p></div>';
                results.style.display = 'block';
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
    return render_template_string(HTML_TEMPLATE)

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

if __name__ == '__main__':
    print("🚀 Starting Trust Bench Multi-Agent Auditor Web Interface...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🔍 Ready to analyze repositories!")
    app.run(debug=True, host='0.0.0.0', port=5000)