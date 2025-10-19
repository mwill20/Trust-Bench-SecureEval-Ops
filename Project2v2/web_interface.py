"""
Simple web interface for the Trust Bench Multi-Agent Repository Auditor.
Run this to get a web UI for submitting repositories for analysis.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)

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
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Trust Bench Multi-Agent Auditor</h1>
        <p class="subtitle">AI-powered repository security and quality analysis</p>
        
        <form id="auditForm">
            <div class="form-group">
                <label for="repoPath">Repository Path:</label>
                <input type="text" id="repoPath" name="repoPath" 
                       placeholder="Enter path to repository (e.g., C:\\path\\to\\repo or . for current)" 
                       value="." required>
            </div>
            
            <div class="form-group">
                <label for="presetRepo">Or choose a preset:</label>
                <select id="presetRepo" name="presetRepo">
                    <option value="">-- Custom path --</option>
                    <option value=".">Current directory (Project2v2)</option>
                    <option value="..">Parent directory (Trust_Bench_Clean)</option>
                    <option value="test_repo">Test repository</option>
                </select>
            </div>
            
            <button type="submit" class="btn" id="analyzeBtn">🔍 Analyze Repository</button>
        </form>
        
        <div class="loading" id="loading">
            <h3>🤖 Agents are analyzing your repository...</h3>
            <p>SecurityAgent, QualityAgent, and DocumentationAgent are working together...</p>
        </div>
        
        <div class="results" id="results">
            <h2>📊 Analysis Results</h2>
            <div id="resultsContent"></div>
        </div>
    </div>

    <script>
        document.getElementById('presetRepo').addEventListener('change', function() {
            if (this.value) {
                document.getElementById('repoPath').value = this.value;
            }
        });

        document.getElementById('auditForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const repoPath = document.getElementById('repoPath').value;
            const analyzeBtn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            // Show loading, hide results
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '🔄 Analyzing...';
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ repo_path: repoPath })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data.report);
                } else {
                    document.getElementById('resultsContent').innerHTML = 
                        '<div style="color: red;"><h3>Error:</h3><p>' + data.error + '</p></div>';
                }
                
                results.style.display = 'block';
            } catch (error) {
                document.getElementById('resultsContent').innerHTML = 
                    '<div style="color: red;"><h3>Error:</h3><p>' + error.message + '</p></div>';
                results.style.display = 'block';
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🔍 Analyze Repository';
                loading.style.display = 'none';
            }
        });
        
        function displayResults(report) {
            const summary = report.summary;
            const agents = report.agents;
            
            let html = `
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
    try:
        data = request.json
        repo_path = data.get('repo_path', '.')
        
        # Create a temporary output directory
        output_dir = f"web_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run the analysis
        cmd = ['python', 'main.py', '--repo', repo_path, '--output', output_dir]
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

if __name__ == '__main__':
    print("🚀 Starting Trust Bench Multi-Agent Auditor Web Interface...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🔍 Ready to analyze repositories!")
    app.run(debug=True, host='0.0.0.0', port=5000)