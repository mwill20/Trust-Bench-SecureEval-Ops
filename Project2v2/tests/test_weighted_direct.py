#!/usr/bin/env python3
"""Direct test of weighted scoring functionality without web interface."""

import sys
import os
sys.path.append('.')

from main import run_workflow
from pathlib import Path

def test_weighted_scoring_direct():
    """Test weighted scoring by calling the workflow directly."""
    print("🧪 Testing Weighted Scoring Functionality (Direct)")
    print("=" * 55)
    
    repo_root = Path("test_repo")
    
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
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📊 Test {i}/4: {config['name']}")
        print(f"   Weights: {config['weights']}")
        
        try:
            # Run the workflow with specific weights
            final_state = run_workflow(repo_root, config['weights'])
            
            # Extract results
            report = final_state.get("report", {})
            individual_scores = report.get("individual_scores", {})
            weights_used = report.get("weights_used", {})
            
            result = {
                'config': config['name'],
                'overall_score': report.get('overall_score'),
                'calculation_method': report.get('calculation_method'),
                'individual_scores': individual_scores,
                'weights_used': weights_used,
                'success': True
            }
            results.append(result)
            
            print(f"   ✅ Overall Score: {result['overall_score']}")
            print(f"   📈 Method: {result['calculation_method']}")
            print(f"   🔍 Security: {individual_scores.get('security', 'N/A')}")
            print(f"   🔍 Quality: {individual_scores.get('quality', 'N/A')}")  
            print(f"   🔍 Documentation: {individual_scores.get('documentation', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'config': config['name'],
                'error': str(e),
                'success': False
            })
    
    # Summary comparison
    print("\n" + "="*70)
    print("📋 WEIGHTED SCORING TEST RESULTS SUMMARY") 
    print("="*70)
    
    successful_results = [r for r in results if r.get('success')]
    
    if successful_results:
        print(f"\n🎯 Successful Tests: {len(successful_results)}/{len(results)}")
        print("\nScore Comparison:")
        print("Configuration".ljust(25) + "Overall".ljust(10) + "Security".ljust(10) + "Quality".ljust(10) + "Docs".ljust(10) + "Method")
        print("-" * 75)
        
        for result in successful_results:
            name = result['config'][:23]
            overall = f"{result['overall_score']:.1f}" if result.get('overall_score') else "N/A"
            individual = result['individual_scores']
            security = f"{individual.get('security', 0):.0f}" if individual else "N/A"
            quality = f"{individual.get('quality', 0):.0f}" if individual else "N/A"
            docs = f"{individual.get('documentation', 0):.0f}" if individual else "N/A" 
            method = result.get('calculation_method', 'N/A')[:10]
            
            print(f"{name.ljust(25)}{overall.ljust(10)}{security.ljust(10)}{quality.ljust(10)}{docs.ljust(10)}{method}")
        
        # Verify weights actually affect scores
        scores = [r['overall_score'] for r in successful_results if r.get('overall_score') is not None]
        if len(set(scores)) > 1:
            print(f"\n✅ SUCCESS: Weights produce different scores! Range: {min(scores):.1f} - {max(scores):.1f}")
        else:
            print(f"\n⚠️  WARNING: All configurations produced same score ({scores[0] if scores else 'N/A'})")
            
    else:
        print("❌ No successful tests completed!")
    
    print(f"\n🏁 Testing complete!")
    return results

if __name__ == "__main__":
    test_weighted_scoring_direct()