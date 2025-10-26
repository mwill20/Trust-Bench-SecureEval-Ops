#!/usr/bin/env python3
"""
Test Agent Confidence Scoring functionality.
Tests confidence calculation algorithms and UI integration.
"""

import io
import json
import os
import sys
import tempfile
import zipfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from main import run_workflow
from multi_agent_system.orchestrator import _calculate_agent_confidence
from multi_agent_system.types import AgentResult


def test_confidence_calculation():
    """Test the confidence calculation algorithm directly."""
    print("=== Testing Confidence Calculation Algorithm ===")
    
    # Test case 1: High confidence result
    high_conf_result = {
        "score": 85.0,
        "summary": "Comprehensive security analysis found 3 vulnerabilities including SQL injection, XSS, and improper authentication. Detailed recommendations provided for each issue with specific code examples and remediation steps.",
        "details": {
            "vulnerabilities": ["sql_injection", "xss", "auth_bypass"],
            "files_analyzed": 25,
            "lines_scanned": 1500,
            "recommendations": ["input_validation", "output_encoding", "auth_framework"],
            "severity_levels": {"high": 1, "medium": 2, "low": 0}
        }
    }
    
    high_confidence = _calculate_agent_confidence(high_conf_result)
    print(f"High confidence result: {high_confidence:.3f} ({int(high_confidence * 100)}%)")
    assert high_confidence >= 0.7, f"Expected high confidence (>=0.7), got {high_confidence}"
    
    # Test case 2: Medium confidence result
    med_conf_result = {
        "score": 60.0,
        "summary": "Basic security scan completed with some findings.",
        "details": {
            "basic_scan": True,
            "issues_found": 2
        }
    }
    
    med_confidence = _calculate_agent_confidence(med_conf_result)
    print(f"Medium confidence result: {med_confidence:.3f} ({int(med_confidence * 100)}%)")
    assert 0.3 <= med_confidence <= 0.8, f"Expected medium confidence (0.3-0.8), got {med_confidence}"
    
    # Test case 3: Low confidence result
    low_conf_result = {
        "score": 30.0,
        "summary": "Scan done.",
        "details": {}
    }
    
    low_confidence = _calculate_agent_confidence(low_conf_result)
    print(f"Low confidence result: {low_confidence:.3f} ({int(low_confidence * 100)}%)")
    assert low_confidence <= 0.5, f"Expected low confidence (<=0.5), got {low_confidence}"
    
    print("Γ£à Confidence calculation tests passed!\n")


def test_workflow_confidence_integration():
    """Test that confidence scores are properly calculated and stored in workflow."""
    print("=== Testing Workflow Confidence Integration ===")
    
    # Create a temporary test repository
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir)
        
        # Create some test files
        (test_repo / "main.py").write_text("""
import os
import sys

def vulnerable_function(user_input):
    # This is intentionally vulnerable
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def main():
    user_data = input("Enter your name: ")
    result = vulnerable_function(user_data)
    print(result)

if __name__ == "__main__":
    main()
""")
def test_report_bundle_download_includes_chat_history(tmp_path):
    """Ensure the report bundle endpoint returns report and chat history."""
    from multi_agent_system.reporting import build_report_payload, write_report_outputs
    from web_interface import app

    test_repo = tmp_path / "bundle_repo"
    test_repo.mkdir()
    (test_repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    (test_repo / "main.py").write_text("print('bundle test')\n", encoding="utf-8")

    final_state = run_workflow(test_repo)
    report = build_report_payload(final_state)

    base_dir = Path(__file__).resolve().parent.parent
    output_dir_name = f"bundle_test_{os.getpid()}"
    output_dir = base_dir / output_dir_name
    output_dir.mkdir(exist_ok=True)

    try:
        write_report_outputs(report, output_dir)

        chat_history = [
            {
                "timestamp": "2025-01-01T00:00:00Z",
                "author": "You",
                "message": "How risky is this repo?"
            },
            {
                "timestamp": "2025-01-01T00:00:02Z",
                "author": "Security Agent",
                "message": "It contains moderate risk.",
                "agent": "security",
                "confidence": 0.82,
                "routing_reason": "Detected security-related keywords"
            },
        ]

        with app.test_client() as client:
            response = client.post(
                "/download-report-bundle",
                json={
                    "output_dir": output_dir_name,
                    "chat_history": chat_history,
                },
            )

        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        bundle = zipfile.ZipFile(io.BytesIO(response.data))
        names = bundle.namelist()
        assert "report.json" in names, "bundle missing report.json"
        assert "chat_history.json" in names, "bundle missing chat_history.json"

        chat_payload = json.loads(bundle.read("chat_history.json"))
        assert "exported_at" in chat_payload
        exported_conversation = chat_payload.get("conversation", [])
        assert exported_conversation, "Chat history conversation should not be empty"
        assert exported_conversation[0]["author"] == "You"
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)




        
        (test_repo / "README.md").write_text("""
# Test Project
This is a test project for confidence scoring validation.

## Features
- Basic user input handling
- Database queries
- Command line interface

## Security Notes
This project has intentional vulnerabilities for testing purposes.
""")
        
        (test_repo / "requirements.txt").write_text("flask==2.0.1\nrequests==2.25.1")
        
        # Run workflow with default weights
        print("Running workflow with equal weights...")
        final_state = run_workflow(test_repo)
        
        # Check that confidence scores were calculated
        confidence_scores = final_state.get("confidence_scores", {})
        print(f"Confidence scores calculated: {confidence_scores}")

        # Validate process visualization payload exists
        process_viz = final_state.get("process_visualization")
        assert process_viz is not None, "process_visualization data should be present in final state"
        rounds = process_viz.get("rounds")
        assert isinstance(rounds, list), "Rounds should be a list"
        assert rounds, "Expected at least one round step in visualization"
        assert isinstance(process_viz.get("agent_moods"), dict), "Agent moods should be a dictionary"
        
        # Validate confidence scores exist for each agent
        expected_agents = ["SecurityAgent", "QualityAgent", "DocumentationAgent"]
        for agent in expected_agents:
            assert agent in confidence_scores, f"Missing confidence score for {agent}"
            confidence = confidence_scores[agent]
            assert 0.0 <= confidence <= 1.0, f"Invalid confidence range for {agent}: {confidence}"
            print(f"  - {agent}: {confidence:.3f} ({int(confidence * 100)}%)")
        
        # Run workflow with weighted configuration
        print("\nRunning workflow with security-focused weights...")
        weighted_state = run_workflow(test_repo, {"security": 60, "quality": 25, "docs": 15})
        
        # Check confidence scores are still calculated
        weighted_confidence = weighted_state.get("confidence_scores", {})
        print(f"Weighted confidence scores: {weighted_confidence}")

        weighted_process_viz = weighted_state.get("process_visualization")
        assert weighted_process_viz is not None, "Weighted run should include process_visualization data"
        weighted_rounds = weighted_process_viz.get("rounds")
        assert isinstance(weighted_rounds, list), "Rounds should be captured for weighted run"
        
        for agent in expected_agents:
            assert agent in weighted_confidence, f"Missing weighted confidence score for {agent}"
            confidence = weighted_confidence[agent]
            assert 0.0 <= confidence <= 1.0, f"Invalid weighted confidence range for {agent}: {confidence}"
            print(f"  - {agent}: {confidence:.3f} ({int(confidence * 100)}%)")
        
        print("Γ£à Workflow confidence integration tests passed!\n")


def test_report_confidence_inclusion():
    """Test that confidence scores are included in generated reports."""
    print("=== Testing Report Confidence Inclusion ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir)
        output_dir = Path(temp_dir) / "output"
        
        # Create minimal test repository
        (test_repo / "test.py").write_text("print('Hello World')")
        (test_repo / "README.md").write_text("# Test\nBasic test project.")
        
        # Run workflow
        final_state = run_workflow(test_repo)
        
        # Import reporting functions
        from multi_agent_system.reporting import build_report_payload, write_report_outputs
        
        # Build report
        report = build_report_payload(final_state)
        
        # Check confidence scores are in report
        assert "confidence_scores" in report, "Report missing confidence_scores field"
        assert "process_visualization" in report, "Report missing process_visualization field"
        confidence_scores = report["confidence_scores"]
        process_viz = report["process_visualization"]
        assert isinstance(process_viz, dict), "process_visualization should be a dictionary in report payload"
        if process_viz:
            assert isinstance(process_viz.get("rounds"), list), "Rounds should be listed in report payload"
        
        print(f"Report confidence scores: {confidence_scores}")
        
        # Validate confidence scores format
        assert isinstance(confidence_scores, dict), "Confidence scores should be a dictionary"
        for agent_name, confidence in confidence_scores.items():
            assert isinstance(confidence, float), f"Confidence for {agent_name} should be float"
            assert 0.0 <= confidence <= 1.0, f"Confidence for {agent_name} out of range: {confidence}"
        
        # Write report outputs
        output_files = write_report_outputs(report, output_dir)
        
        # Check that confidence scores appear in markdown output
        markdown_path = output_files["markdown"]
        markdown_content = markdown_path.read_text()
        
        # Look for confidence indicators in markdown
        assert "Confidence:" in markdown_content, "Markdown report missing confidence information"
        assert "## Negotiation Timeline" in markdown_content, "Markdown report missing negotiation timeline section"
        
        # Check for either emoji indicators or text indicators
        has_emoji = "≡ƒƒó" in markdown_content or "≡ƒƒí" in markdown_content or "≡ƒö┤" in markdown_content
        has_text = "HIGH" in markdown_content or "MEDIUM" in markdown_content or "LOW" in markdown_content
        assert has_emoji or has_text, "Missing confidence visual indicators (emoji or text)"
        
        print("Γ£à Report confidence inclusion tests passed!\n")


def main():
    """Run all confidence scoring tests."""
    print("Running Agent Confidence Scoring Tests...\n")
    
    try:
        test_confidence_calculation()
        test_workflow_confidence_integration() 
        test_report_confidence_inclusion()
        temp_dir = Path(tempfile.mkdtemp())
        try:
            test_report_bundle_download_includes_chat_history(tmp_path=temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        
        print("≡ƒÄë All Agent Confidence Scoring tests passed successfully!")
        print("Feature is ready for production use!")
        return 0
        
    except Exception as e:
        print(f"Γ¥î Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
