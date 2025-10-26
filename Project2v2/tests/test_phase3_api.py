#!/usr/bin/env python3
"""Test Phase 3 functionality through API"""

import requests
import json

def test_phase3_api():
    """Test Phase 3 consensus building query"""
    
    # Test Phase 3 query
    chat_data = {
        'question': 'What are the conflicting priorities between security and quality?',
        'provider': 'openai'
    }

    try:
        print("🚀 Testing Phase 3 consensus building query...")
        response = requests.post(
            'http://localhost:5000/api/chat', 
            json=chat_data,
            timeout=30  # Phase 3 may take longer
        )
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Phase 3 API call successful')
            print(f'Agent: {data.get("agent", "unknown")}')
            print(f'Confidence: {data.get("confidence", 0)}%')
            print(f'Success: {data.get("success", False)}')
            print(f'Context Available: {data.get("context_available", False)}')
            
            if 'answer' in data:
                answer = data["answer"]
                print(f'Answer length: {len(answer)} characters')
                
                # Check for Phase 3 indicators in response
                if "Phase 3" in answer or "consensus" in answer.lower():
                    print('🚀 Phase 3 indicators detected in response!')
                else:
                    print('⚠️  No explicit Phase 3 indicators found')
                    
                # Show first 200 chars of response
                preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f'Response preview: {preview}')
            else:
                print('❌ No answer in response')
                print(f'Full response: {data}')
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            print(response.text)
            
    except Exception as e:
        print(f'❌ Exception: {e}')

if __name__ == "__main__":
    test_phase3_api()