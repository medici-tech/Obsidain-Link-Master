#!/usr/bin/env python3
"""
Model Performance Test for MacBook Air 2025 16GB
Compare Qwen3:8b vs Qwen2.5:3b performance
"""

import time
import requests
import json
from typing import Dict, Any

def test_model_performance(model_name: str, test_content: str, iterations: int = 3) -> Dict[str, Any]:
    """Test model performance with multiple iterations"""
    print(f"🧪 Testing {model_name}...")
    
    url = "http://localhost:11434/api/generate"
    
    # Model-specific settings
    if "8b" in model_name:
        settings = {
            "model": model_name,
            "temperature": 0.1,
            "max_tokens": 1024,
            "context_window": 8192,
            "timeout": 60
        }
    else:  # 3b model
        settings = {
            "model": model_name,
            "temperature": 0.1,
            "max_tokens": 512,
            "context_window": 4096,
            "timeout": 30
        }
    
    times = []
    successes = 0
    
    for i in range(iterations):
        start_time = time.time()
        
        try:
            payload = {
                "model": settings["model"],
                "prompt": f"Categorize this content: {test_content[:500]}",
                "stream": False,
                "options": {
                    "temperature": settings["temperature"],
                    "num_ctx": settings["context_window"],
                    "num_predict": settings["max_tokens"]
                }
            }
            
            response = requests.post(url, json=payload, timeout=settings["timeout"])
            response.raise_for_status()
            
            result = response.json()
            if result.get('response'):
                successes += 1
            
            end_time = time.time()
            times.append(end_time - start_time)
            
            print(f"  Iteration {i+1}: {times[-1]:.2f}s")
            
        except Exception as e:
            print(f"  Iteration {i+1}: Failed - {e}")
            times.append(float('inf'))
    
    # Calculate statistics
    valid_times = [t for t in times if t != float('inf')]
    
    return {
        "model": model_name,
        "iterations": iterations,
        "successes": successes,
        "success_rate": successes / iterations * 100,
        "avg_time": sum(valid_times) / len(valid_times) if valid_times else float('inf'),
        "min_time": min(valid_times) if valid_times else float('inf'),
        "max_time": max(valid_times) if valid_times else float('inf'),
        "total_time": sum(valid_times) if valid_times else float('inf')
    }

def main():
    """Run performance comparison"""
    print("🚀 Model Performance Test for MacBook Air 2025 16GB")
    print("=" * 60)
    
    # Test content samples
    test_contents = [
        "Simple personal note about daily activities",
        "Technical analysis of business strategy and revenue optimization",
        "Complex financial investment analysis with market trends",
        "Short ChatGPT conversation about weather",
        "Long business document with multiple sections and analysis"
    ]
    
    models = ["qwen2.5:3b", "qwen3:8b"]
    results = {}
    
    for model in models:
        print(f"\n📊 Testing {model}")
        print("-" * 40)
        
        model_results = []
        for i, content in enumerate(test_contents):
            print(f"\nTest {i+1}: {content[:50]}...")
            result = test_model_performance(model, content, iterations=2)
            model_results.append(result)
        
        results[model] = model_results
    
    # Generate comparison report
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE COMPARISON REPORT")
    print("=" * 60)
    
    for model, model_results in results.items():
        print(f"\n🤖 {model.upper()}")
        print("-" * 30)
        
        avg_times = [r['avg_time'] for r in model_results if r['avg_time'] != float('inf')]
        success_rates = [r['success_rate'] for r in model_results]
        
        if avg_times:
            print(f"⚡ Average Response Time: {sum(avg_times)/len(avg_times):.2f}s")
            print(f"🏆 Best Time: {min(avg_times):.2f}s")
            print(f"🐌 Worst Time: {max(avg_times):.2f}s")
        
        if success_rates:
            print(f"✅ Success Rate: {sum(success_rates)/len(success_rates):.1f}%")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    qwen3_results = results.get("qwen3:8b", [])
    qwen2_5_results = results.get("qwen2.5:3b", [])
    
    qwen3_avg = sum([r['avg_time'] for r in qwen3_results if r['avg_time'] != float('inf')]) / len([r for r in qwen3_results if r['avg_time'] != float('inf')]) if qwen3_results else float('inf')
    qwen2_5_avg = sum([r['avg_time'] for r in qwen2_5_results if r['avg_time'] != float('inf')]) / len([r for r in qwen2_5_results if r['avg_time'] != float('inf')]) if qwen2_5_results else float('inf')
    
    if qwen3_avg < qwen2_5_avg * 1.5:  # If Qwen3 is less than 1.5x slower
        print("🎯 RECOMMENDATION: Use Qwen3:8b as primary model")
        print("   - Better accuracy for complex content")
        print("   - Acceptable speed difference")
        print("   - More detailed responses")
    else:
        print("🎯 RECOMMENDATION: Use hybrid approach")
        print("   - Qwen2.5:3b for simple/quick tasks")
        print("   - Qwen3:8b for complex analysis")
        print("   - Intelligent switching based on content")
    
    print(f"\n📊 Memory Usage:")
    print(f"   Qwen2.5:3b: ~2GB RAM")
    print(f"   Qwen3:8b: ~5GB RAM")
    print(f"   Your MacBook Air 2025: 16GB RAM")
    print(f"   Recommendation: Both models can run simultaneously!")

if __name__ == "__main__":
    main()
