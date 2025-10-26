#!/usr/bin/env python3
"""
Phase 3 Test queries to validate advanced orchestration with consensus building.
These queries should trigger the sophisticated multi-agent processes.
"""

# Phase 3 test queries that should trigger advanced orchestration
PHASE3_TEST_QUERIES = [
    # Consensus building queries
    "What are the conflicting priorities between security and quality in this repository?",
    "Help me resolve the trade-offs between security hardening and code maintainability",
    "What consensus can we reach on the most critical issues to address first?",
    
    # Priority negotiation queries
    "Which security issues should take priority over quality improvements?", 
    "How can we balance documentation needs with security and quality concerns?",
    "What's the unified approach to address all the different agent recommendations?",
    
    # Iterative refinement queries
    "Provide a step-by-step collaborative analysis of this repository",
    "Give me a comprehensive review with iterative agent consultation",
    "I need a thorough analysis with follow-up questions between agents",
    
    # Conflict resolution queries
    "Reconcile the different opinions between security and quality agents",
    "Resolve any contradictions in the agent recommendations", 
    "What agreement can be reached despite conflicting agent assessments?",
    
    # Advanced orchestration queries  
    "Negotiate priorities and provide a unified action plan across all domains",
    "Build consensus on the most important improvements needed",
    "Collaborative decision making for repository improvement strategy"
]

# Phase 2 queries (should NOT trigger Phase 3)
PHASE2_TEST_QUERIES = [
    "Give me a comprehensive analysis of this repository",
    "Provide complete security and quality assessment", 
    "What are the security and quality issues in this codebase?"
]

# Single agent queries (should NOT trigger multi-agent)
SINGLE_AGENT_QUERIES = [
    "What security vulnerabilities exist?",
    "How is the code quality?",
    "Is the documentation adequate?"
]

if __name__ == "__main__":
    print("=== Trust Bench Phase 3 Advanced Orchestration Test Queries ===\n")
    
    print("🚀 PHASE 3 QUERIES (should trigger advanced orchestration):")
    for i, query in enumerate(PHASE3_TEST_QUERIES, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\n🔄 PHASE 2 QUERIES (should trigger basic multi-agent):")
    for i, query in enumerate(PHASE2_TEST_QUERIES, 1):
        print(f"{i:2d}. {query}")
        
    print(f"\n🎯 SINGLE AGENT QUERIES (should trigger single agent):")
    for i, query in enumerate(SINGLE_AGENT_QUERIES, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\n📋 Phase 3 Testing Instructions:")
    print(f"1. Open http://localhost:5000 and analyze a repository first")
    print(f"2. Test Phase 3 queries - should show 'Phase 3 Advanced Orchestration' banner")
    print(f"3. Look for consensus building process and orchestration logs")
    print(f"4. Verify Phase 2 queries show standard multi-agent consultation")
    print(f"5. Confirm single-agent queries route to individual specialists")
    print(f"\n🎯 Expected Phase 3 Indicators:")
    print(f"- 🚀 Phase 3 Advanced Orchestration banner")
    print(f"- 🔄 Orchestration Process (expandable)")
    print(f"- ✅ Consensus Achieved or ⚖️ Partial Consensus status")
    print(f"- Higher confidence scores (90%+)")
    print(f"- Advanced synthesis with conflict resolution")