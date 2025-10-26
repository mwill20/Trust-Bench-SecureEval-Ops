#!/usr/bin/env python3
"""Test script for weighted scoring functionality."""

import requests
import json
import time

def test_weighted_scoring():
    """Test the weighted scoring with different configurations."""
    print("🧪 Testing weighted scoring functionality...")
    
    test_configs = [
        {
            "name": "Equal Weights (Default)",
            "weights": {"security": 33, "quality": 33, "docs": 34}
        },
        {
            "name": "Security Focus",
            "weights": {"security": 50, "quality": 25, "docs": 25}
        },
        {
            "name": "Quality Focus", 
            "weights": {"security": 25, "quality": 50, "docs": 25}
        },
        {
            "name": "Documentation Focus",
            "weights": {"security": 25, "quality": 25, "docs": 50}
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n📊 Testing: {config['name']}")
        print(f"   Weights: {config['weights']}")
        
        try:
            response = requests.post(
                'http://localhost:5001/analyze',
                json={
                    'repo_url': 'test_repo',
                    'eval_weights': config['weights']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    report = data.get('report', {})
                    summary = report.get('summary', {})
                    
                    result = {
                        'config': config['name'],
                        'overall_score': summary.get('overall_score'),
                        'calculation_method': summary.get('calculation_method'),
                        'individual_scores': summary.get('individual_scores', {}),
                        'weights_used': summary.get('weights_used', {}),
                        'success': True
                    }
                    results.append(result)
                    
                    print(f"   ✅ Overall Score: {result['overall_score']}")
                    print(f"   📈 Method: {result['calculation_method']}")
                    print(f"   🔍 Individual: {result['individual_scores']}")
                else:
                    print(f"   ❌ Analysis failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Summary comparison
    print("\n" + "="*60)
    print("📋 WEIGHTED SCORING TEST RESULTS")
    print("="*60)
    
    for result in results:
        if result.get('success'):
            print(f"\n{result['config']}:")
            print(f"  Overall Score: {result['overall_score']}")
            print(f"  Method: {result['calculation_method']}")
            individual = result['individual_scores']
            print(f"  Security: {individual.get('security', 'N/A')} | Quality: {individual.get('quality', 'N/A')} | Docs: {individual.get('documentation', 'N/A')}")
            
            weights = result['weights_used']
            if isinstance(weights, dict):
                print(f"  Weights: Security({weights.get('security', 'N/A')}%) | Quality({weights.get('quality', 'N/A')}%) | Docs({weights.get('docs', 'N/A')}%)")
    
    print(f"\n✅ Testing complete! Analyzed {len(results)} configurations.")
    return results

if __name__ == "__main__":
    test_weighted_scoring()