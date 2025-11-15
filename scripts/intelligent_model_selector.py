#!/usr/bin/env python3
"""
Intelligent Model Selector for Hybrid Processing
Automatically chooses between Qwen3:8b and Qwen2.5:3b based on content complexity
"""

import os
import re
import json
from typing import Dict, Any, Tuple
import requests

class IntelligentModelSelector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.qwen3_8b_url = config.get('primary_ollama_base_url', 'http://localhost:11434')
        self.qwen2_5_3b_url = config.get('secondary_ollama_base_url', 'http://localhost:11434')
        
        # Model settings
        self.qwen3_8b_settings = {
            'model': config.get('primary_ollama_model', 'qwen3:8b'),
            'temperature': config.get('primary_ollama_temperature', 0.1),
            'max_tokens': config.get('primary_ollama_max_tokens', 2048),
            'context_window': config.get('primary_ollama_context_window', 16384),
            'timeout': config.get('primary_ollama_timeout', 120)
        }
        
        self.qwen2_5_3b_settings = {
            'model': config.get('secondary_ollama_model', 'qwen2.5:3b'),
            'temperature': config.get('secondary_ollama_temperature', 0.1),
            'max_tokens': config.get('secondary_ollama_max_tokens', 1024),
            'context_window': config.get('secondary_ollama_context_window', 8192),
            'timeout': config.get('secondary_ollama_timeout', 60)
        }
        
        # Switching thresholds
        self.word_threshold = config.get('model_switching_threshold', 1000)
        self.complexity_keywords = [
            'technical', 'business', 'financial', 'investment', 'analysis',
            'strategy', 'development', 'automation', 'integration', 'optimization'
        ]
    
    def analyze_content_complexity(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze content to determine which model to use"""
        word_count = len(content.split())
        char_count = len(content)
        
        # Complexity indicators
        complexity_score = 0
        
        # File size factor
        if word_count > self.word_threshold:
            complexity_score += 3
        elif word_count > 500:
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Content complexity
        content_lower = content.lower()
        for keyword in self.complexity_keywords:
            if keyword in content_lower:
                complexity_score += 1
        
        # Technical content indicators
        technical_indicators = [
            'api', 'code', 'function', 'variable', 'database', 'sql',
            'python', 'javascript', 'html', 'css', 'json', 'xml'
        ]
        for indicator in technical_indicators:
            if indicator in content_lower:
                complexity_score += 1
        
        # Business/finance content
        business_indicators = [
            'revenue', 'profit', 'investment', 'portfolio', 'market',
            'business', 'strategy', 'analysis', 'financial'
        ]
        for indicator in business_indicators:
            if indicator in content_lower:
                complexity_score += 1
        
        # File type analysis
        filename = os.path.basename(file_path).lower()
        if any(term in filename for term in ['analysis', 'strategy', 'business', 'technical']):
            complexity_score += 2
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'complexity_score': complexity_score,
            'recommended_model': 'qwen3:8b' if complexity_score >= 5 else 'qwen2.5:3b',
            'reasoning': self._get_reasoning(complexity_score, word_count)
        }
    
    def _get_reasoning(self, complexity_score: int, word_count: int) -> str:
        """Generate reasoning for model selection"""
        if complexity_score >= 5:
            return f"High complexity (score: {complexity_score}) and {word_count} words - using Qwen3:8b for detailed analysis"
        elif word_count > self.word_threshold:
            return f"Large file ({word_count} words) - using Qwen3:8b for better context handling"
        else:
            return f"Standard complexity (score: {complexity_score}) and {word_count} words - using Qwen2.5:3b for efficiency"
    
    def select_model(self, content: str, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Select the best model for the given content"""
        analysis = self.analyze_content_complexity(content, file_path)
        selected_model = analysis['recommended_model']
        
        if selected_model == 'qwen3:8b':
            return 'qwen3:8b', {**self.qwen3_8b_settings, 'analysis': analysis}
        else:
            return 'qwen2.5:3b', {**self.qwen2_5_3b_settings, 'analysis': analysis}
    
    def call_selected_model(self, content: str, file_path: str, prompt: str) -> Dict[str, Any]:
        """Call the selected model with the content"""
        selected_model, settings = self.select_model(content, file_path)
        
        print(f"  🤖 Using {selected_model} (Reason: {settings['analysis']['reasoning']})")
        
        try:
            if selected_model == 'qwen3:8b':
                return self._call_qwen3_8b(content, prompt, settings)
            else:
                return self._call_qwen2_5_3b(content, prompt, settings)
        except Exception as e:
            print(f"  ⚠️ {selected_model} failed, falling back to qwen2.5:3b")
            return self._call_qwen2_5_3b(content, prompt, self.qwen2_5_3b_settings)
    
    def _call_qwen3_8b(self, content: str, prompt: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Call Qwen3:8b model"""
        url = f"{self.qwen3_8b_url}/api/generate"
        
        payload = {
            "model": settings['model'],
            "prompt": f"{prompt}\n\nContent: {content[:settings['context_window']//2]}",
            "stream": False,
            "options": {
                "temperature": settings['temperature'],
                "top_p": 0.9,
                "top_k": 20,
                "num_ctx": settings['context_window'],
                "num_predict": settings['max_tokens'],
                "stop": ["```", "\n\n\n"]
            }
        }
        
        response = requests.post(url, json=payload, timeout=settings['timeout'])
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '').strip()
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Failed to parse JSON"}
        except json.JSONDecodeError:
            return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Invalid JSON response"}
    
    def _call_qwen2_5_3b(self, content: str, prompt: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Call Qwen2.5:3b model"""
        url = f"{self.qwen2_5_3b_url}/api/generate"
        
        payload = {
            "model": settings['model'],
            "prompt": f"{prompt}\n\nContent: {content[:settings['context_window']//2]}",
            "stream": False,
            "options": {
                "temperature": settings['temperature'],
                "top_p": 0.9,
                "top_k": 20,
                "num_ctx": settings['context_window'],
                "num_predict": settings['max_tokens'],
                "stop": ["```", "\n\n\n"]
            }
        }
        
        response = requests.post(url, json=payload, timeout=settings['timeout'])
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '').strip()
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Failed to parse JSON"}
        except json.JSONDecodeError:
            return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Invalid JSON response"}

def load_hybrid_config() -> Dict[str, Any]:
    """Load hybrid model configuration"""
    try:
        with open('config_hybrid_models.yaml', 'r') as f:
            import yaml
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading hybrid config: {e}")
        return {}

if __name__ == "__main__":
    # Test the model selector
    config = load_hybrid_config()
    selector = IntelligentModelSelector(config)
    
    # Test with sample content
    test_content = "This is a technical analysis of our business strategy for Q4 revenue optimization and market expansion."
    test_file = "business_analysis.md"
    
    selected_model, settings = selector.select_model(test_content, test_file)
    print(f"Selected model: {selected_model}")
    print(f"Settings: {settings}")
