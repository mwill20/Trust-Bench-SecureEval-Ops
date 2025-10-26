#!/usr/bin/env python3
"""Test Phase 3 consensus building detection"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_router import OrchestrationRouter

def test_phase3_detection():
    # Mock report data for testing
    mock_report = {
        "security_issues": ["Test security issue"],
        "quality_issues": ["Test quality issue"], 
        "documentation_issues": ["Test doc issue"]
    }
    router = OrchestrationRouter(mock_report)
    
    # Test Phase 3 queries
    phase3_queries = [
        "What are the conflicting priorities between security and quality?",
        "Help me resolve the trade-offs between security and quality",
        "What consensus can we reach on the most critical issues?",
        "Reconcile the different opinions between agents"
    ]
    
    # Test Phase 2 queries  
    phase2_queries = [
        "Give me a comprehensive analysis",
        "Provide complete security and quality assessment"
    ]
    
    # Test single agent queries
    single_queries = [
        "What security vulnerabilities exist?",
        "How is the code quality?"
    ]
    
    print("=== Testing Phase 3 Consensus Detection ===\n")
    
    print("🚀 Phase 3 Queries (should return True):")
    for query in phase3_queries:
        result = router._requires_consensus_building(query)
        status = "✅ DETECTED" if result else "❌ MISSED"
        print(f"  {status}: {query}")
    
    print("\n🔄 Phase 2 Queries (should return False):")
    for query in phase2_queries:
        result = router._requires_consensus_building(query)
        status = "❌ FALSE POSITIVE" if result else "✅ CORRECT"
        print(f"  {status}: {query}")
        
    print("\n🎯 Single Agent Queries (should return False):")
    for query in single_queries:
        result = router._requires_consensus_building(query)
        status = "❌ FALSE POSITIVE" if result else "✅ CORRECT"
        print(f"  {status}: {query}")

if __name__ == "__main__":
    test_phase3_detection()