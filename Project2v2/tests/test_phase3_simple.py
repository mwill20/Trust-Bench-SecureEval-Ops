#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 Test queries to validate advanced orchestration with consensus building.
"""

# Phase 3 test queries that should trigger advanced orchestration
PHASE3_TEST_QUERIES = [
    "What are the conflicting priorities between security and quality in this repository?",
    "Help me resolve the trade-offs between security hardening and code maintainability",
    "What consensus can we reach on the most critical issues to address first?",
    "Which security issues should take priority over quality improvements?", 
    "How can we balance documentation needs with security and quality concerns?",
    "Provide a step-by-step collaborative analysis of this repository",
    "Reconcile the different opinions between security and quality agents",
    "Negotiate priorities and provide a unified action plan across all domains"
]

if __name__ == "__main__":
    print("=== Trust Bench Phase 3 Advanced Orchestration Test Queries ===\n")
    
    print("Phase 3 Queries (should trigger advanced orchestration):")
    for i, query in enumerate(PHASE3_TEST_QUERIES, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\nPhase 3 Testing Instructions:")
    print(f"1. Open http://localhost:5000 and analyze a repository first")
    print(f"2. Test Phase 3 queries - should show 'Phase 3 Advanced Orchestration' banner")
    print(f"3. Look for consensus building process and orchestration logs")
    
    print(f"\nExpected Phase 3 Indicators:")
    print(f"- Phase 3 Advanced Orchestration banner")
    print(f"- Orchestration Process (expandable)")
    print(f"- Consensus status indicators")
    print(f"- Higher confidence scores (90%+)")