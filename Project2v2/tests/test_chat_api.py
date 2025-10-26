#!/usr/bin/env python3
"""Test script to diagnose chat API issues"""

import requests
import json
import sys

def test_chat_api():
    """Test the chat API endpoint"""
    
    # Test basic connectivity first
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        print(f"✅ Server connectivity: {response.status_code}")
    except Exception as e:
        print(f"❌ Server unreachable: {e}")
        return False
    
    # Test chat endpoint without repository analysis
    try:
        chat_data = {
            'question': 'Hello, can you help me?',
            'provider': 'openai',
            'api_key': 'test-key'
        }
        
        response = requests.post(
            'http://localhost:5000/api/chat', 
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Chat API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat API successful")
            print(f"Response keys: {list(data.keys())}")
            if data.get('success'):
                print("✅ Chat response successful")
            else:
                print(f"❌ Chat error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat API Exception: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Testing Trust Bench Chat API...")
    success = test_chat_api()
    sys.exit(0 if success else 1)