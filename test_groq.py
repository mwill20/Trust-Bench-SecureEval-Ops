#!/usr/bin/env python3
"""Quick test of Groq API response for task fidelity."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from trustbench_core.providers import GroqProvider

def test_groq_response():
    try:
        # Create provider
        provider = GroqProvider.from_env()
        
        # Test the question from the dataset
        prompt = """You are evaluating TrustBench task fidelity. Answer the question accurately.

Question: What is LangGraph?
Return only the answer without additional commentary."""
        
        result = provider.completion(prompt)
        answer = result['text']
        expected = "LangGraph is a framework for building multi-agent graphs."
        
        print(f"Groq Response: {answer}")
        print(f"Expected: {expected}")
        
        # Test the improved scoring
        answer_lower = answer.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Check for substring match
        if expected_lower in answer_lower or answer_lower in expected_lower:
            score = 0.8
        else:
            # Token overlap
            ans_tokens = set(answer_lower.split())
            exp_tokens = set(expected_lower.split())
            overlap = len(ans_tokens & exp_tokens)
            if overlap > 0:
                base_score = overlap / len(exp_tokens)
                score = min(0.9, max(0.3, base_score))
            else:
                score = 0.0
                
        print(f"Calculated Score: {score}")
        return score
        
    except Exception as e:
        print(f"Error: {e}")
        return 0.0

if __name__ == "__main__":
    test_groq_response()