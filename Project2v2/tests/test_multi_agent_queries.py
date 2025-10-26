#!/usr/bin/env python3
"""
Test queries to validate multi-agent consultation system in Trust Bench.
Run these through the web interface to verify Phase 2 implementation.
"""

# Test queries that should trigger multiple agents
MULTI_AGENT_TEST_QUERIES = [
    # Comprehensive analysis queries
    "Give me a comprehensive analysis of this repository",
    "Provide a complete security and quality assessment",
    "I need a thorough evaluation covering all aspects",
    
    # Multi-domain queries
    "What are the security and quality issues in this codebase?",
    "How are the security, quality, and documentation practices?", 
    "Analyze both security vulnerabilities and code quality problems",
    
    # Holistic evaluation queries
    "Give me an overall evaluation of this project",
    "Provide a full end-to-end analysis",
    "I want a detailed analysis of every area",
    
    # Explicit multi-agent requests
    "Consult all agents about this repository",
    "Get input from security, quality, and documentation experts",
    "What do all the specialist agents think about this code?"
]

# Test queries that should trigger single agents
SINGLE_AGENT_TEST_QUERIES = [
    # Security-specific
    "Are there any security vulnerabilities in this code?",
    "What security issues should I be worried about?",
    "Check for authentication problems",
    
    # Quality-specific  
    "How is the code quality?",
    "Are there any code smells or maintainability issues?",
    "What about testing coverage and practices?",
    
    # Documentation-specific
    "How good is the documentation?",
    "Are the README and comments adequate?",
    "What documentation improvements are needed?"
]

if __name__ == "__main__":
    print("=== Trust Bench Phase 2 Multi-Agent Test Queries ===\n")
    
    print("🔄 MULTI-AGENT QUERIES (should trigger multiple agents):")
    for i, query in enumerate(MULTI_AGENT_TEST_QUERIES, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\n🎯 SINGLE-AGENT QUERIES (should trigger one agent):")  
    for i, query in enumerate(SINGLE_AGENT_TEST_QUERIES, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\n📋 Instructions:")
    print(f"1. Open http://localhost:5000 in your browser")
    print(f"2. Analyze a GitHub repository first") 
    print(f"3. Test these queries in the chat interface")
    print(f"4. Verify multi-agent queries show collaboration indicators")
    print(f"5. Verify single-agent queries route to appropriate specialist")