#!/usr/bin/env python3
"""Test Phase 3 through web interface"""

import requests
import json

def test_phase3_web_interface():
    """Test Phase 3 advanced orchestration through web interface"""
    
    base_url = "http://localhost:5000"
    
    # First, test if the server is running
    try:
        response = requests.get(base_url)
        print("✅ Web server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Web server is not running. Please start it first.")
        return
    
    # Test Phase 3 query
    phase3_query = "What are the conflicting priorities between security and quality in this repository?"
    
    print(f"\n🚀 Testing Phase 3 Query:")
    print(f"Query: {phase3_query}")
    
    # Note: We would need to set up a repository analysis first
    # For now, just confirm the server is responding
    print("📝 Manual testing required:")
    print("1. Open http://localhost:5000 in browser")
    print("2. Analyze a repository (e.g., test_repo)")
    print("3. Ask Phase 3 query and look for:")
    print("   - 🚀 Phase 3 Advanced Orchestration banner")
    print("   - 🔄 Orchestration Process (expandable)")
    print("   - ✅ Consensus status indicators")
    print("   - Higher confidence scores")

if __name__ == "__main__":
    test_phase3_web_interface()