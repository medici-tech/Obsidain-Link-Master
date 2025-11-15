"""
Unit tests for intelligent model selector
Tests model selection logic, complexity analysis, and API integration
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import requests

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))


@pytest.fixture
def minimal_config():
    """Minimal configuration for testing"""
    return {
        'primary_ollama_base_url': 'http://localhost:11434',
        'secondary_ollama_base_url': 'http://localhost:11434',
        'primary_ollama_model': 'qwen3:8b',
        'secondary_ollama_model': 'qwen2.5:3b',
        'model_switching_threshold': 1000
    }


@pytest.fixture
def full_config():
    """Full configuration with all options"""
    return {
        'primary_ollama_base_url': 'http://localhost:11434',
        'secondary_ollama_base_url': 'http://localhost:11434',
        'primary_ollama_model': 'qwen3:8b',
        'secondary_ollama_model': 'qwen2.5:3b',
        'primary_ollama_temperature': 0.1,
        'secondary_ollama_temperature': 0.2,
        'primary_ollama_max_tokens': 2048,
        'secondary_ollama_max_tokens': 1024,
        'primary_ollama_context_window': 16384,
        'secondary_ollama_context_window': 8192,
        'primary_ollama_timeout': 120,
        'secondary_ollama_timeout': 60,
        'model_switching_threshold': 1000
    }


@pytest.mark.unit
class TestModelSelectorInitialization:
    """Test model selector initialization"""

    def test_initialization_with_minimal_config(self, minimal_config):
        """Test initialization with minimal configuration"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        assert selector.qwen3_8b_url == 'http://localhost:11434'
        assert selector.qwen2_5_3b_url == 'http://localhost:11434'
        assert selector.word_threshold == 1000

    def test_initialization_with_full_config(self, full_config):
        """Test initialization with full configuration"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(full_config)

        assert selector.qwen3_8b_settings['model'] == 'qwen3:8b'
        assert selector.qwen3_8b_settings['temperature'] == 0.1
        assert selector.qwen3_8b_settings['max_tokens'] == 2048
        assert selector.qwen3_8b_settings['context_window'] == 16384
        assert selector.qwen3_8b_settings['timeout'] == 120

        assert selector.qwen2_5_3b_settings['model'] == 'qwen2.5:3b'
        assert selector.qwen2_5_3b_settings['temperature'] == 0.2
        assert selector.qwen2_5_3b_settings['max_tokens'] == 1024

    def test_default_values(self):
        """Test default values when config is empty"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector({})

        assert selector.qwen3_8b_settings['model'] == 'qwen3:8b'
        assert selector.qwen2_5_3b_settings['model'] == 'qwen2.5:3b'
        assert selector.word_threshold == 1000


@pytest.mark.unit
class TestComplexityAnalysis:
    """Test content complexity analysis"""

    def test_simple_content_low_complexity(self, minimal_config):
        """Test simple content gets low complexity score"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "This is a simple note about my day."

        analysis = selector.analyze_content_complexity(content, "note.md")

        assert analysis['word_count'] == 8
        assert analysis['complexity_score'] < 5
        assert analysis['recommended_model'] == 'qwen2.5:3b'

    def test_technical_content_high_complexity(self, minimal_config):
        """Test technical content gets high complexity score"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = """
        This is a technical analysis of our Python API integration.
        We need to implement database queries using SQL and JSON parsing.
        The function will handle API requests and return structured data.
        """

        analysis = selector.analyze_content_complexity(content, "technical_analysis.md")

        assert analysis['complexity_score'] >= 5
        assert analysis['recommended_model'] == 'qwen3:8b'

    def test_business_content_high_complexity(self, minimal_config):
        """Test business content gets high complexity score"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = """
        Business strategy analysis for Q4 revenue optimization.
        Investment portfolio management and market analysis.
        Financial planning and profit maximization strategies.
        """

        analysis = selector.analyze_content_complexity(content, "business_strategy.md")

        assert analysis['complexity_score'] >= 5
        assert analysis['recommended_model'] == 'qwen3:8b'

    def test_large_file_triggers_qwen3(self, minimal_config):
        """Test large file (>1000 words) triggers qwen3:8b"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        # Create content with >1000 words
        content = " ".join(["word"] * 1100)

        analysis = selector.analyze_content_complexity(content, "large_file.md")

        assert analysis['word_count'] > 1000
        assert analysis['complexity_score'] >= 5
        assert analysis['recommended_model'] == 'qwen3:8b'

    def test_filename_adds_complexity(self, minimal_config):
        """Test filename with complexity keywords adds to score"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "Simple content but complex filename"

        analysis = selector.analyze_content_complexity(content, "technical_business_analysis.md")

        # Filename should add +2 to complexity score
        assert analysis['complexity_score'] >= 3

    def test_keyword_detection(self, minimal_config):
        """Test complexity keywords are detected"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        # Test complexity keywords
        for keyword in ['technical', 'business', 'financial', 'investment', 'strategy']:
            content = f"This is about {keyword} matters"
            analysis = selector.analyze_content_complexity(content, "test.md")
            assert analysis['complexity_score'] > 1

    def test_technical_indicators(self, minimal_config):
        """Test technical indicator detection"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        # Test technical indicators
        for indicator in ['api', 'code', 'python', 'database', 'json']:
            content = f"Working with {indicator} today"
            analysis = selector.analyze_content_complexity(content, "test.md")
            assert analysis['complexity_score'] >= 2


@pytest.mark.unit
class TestReasoning:
    """Test reasoning generation"""

    def test_high_complexity_reasoning(self, minimal_config):
        """Test reasoning for high complexity content"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        reasoning = selector._get_reasoning(complexity_score=7, word_count=500)

        assert "High complexity" in reasoning
        assert "Qwen3:8b" in reasoning
        assert "7" in reasoning

    def test_large_file_reasoning(self, minimal_config):
        """Test reasoning for large files"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        reasoning = selector._get_reasoning(complexity_score=3, word_count=1500)

        assert "Large file" in reasoning
        assert "Qwen3:8b" in reasoning
        assert "1500" in reasoning

    def test_standard_complexity_reasoning(self, minimal_config):
        """Test reasoning for standard complexity"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        reasoning = selector._get_reasoning(complexity_score=2, word_count=300)

        assert "Standard complexity" in reasoning
        assert "Qwen2.5:3b" in reasoning


@pytest.mark.unit
class TestModelSelection:
    """Test model selection logic"""

    def test_select_qwen3_for_complex_content(self, minimal_config):
        """Test qwen3:8b is selected for complex content"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = """
        Technical analysis of business strategy with financial investment
        portfolio optimization using Python API and database integration.
        """

        model, settings = selector.select_model(content, "technical_analysis.md")

        assert model == 'qwen3:8b'
        assert settings['model'] == 'qwen3:8b'
        assert 'analysis' in settings

    def test_select_qwen2_5_for_simple_content(self, minimal_config):
        """Test qwen2.5:3b is selected for simple content"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "This is a simple note about my day."

        model, settings = selector.select_model(content, "note.md")

        assert model == 'qwen2.5:3b'
        assert settings['model'] == 'qwen2.5:3b'
        assert 'analysis' in settings

    def test_settings_include_analysis(self, minimal_config):
        """Test settings include complexity analysis"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "Test content"

        model, settings = selector.select_model(content, "test.md")

        assert 'analysis' in settings
        assert 'word_count' in settings['analysis']
        assert 'complexity_score' in settings['analysis']
        assert 'reasoning' in settings['analysis']


@pytest.mark.unit
class TestAPIIntegration:
    """Test API call integration"""

    def test_call_qwen3_success(self, minimal_config):
        """Test successful qwen3:8b API call"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '{"moc_category": "Business Operations", "confidence_score": 0.85, "reasoning": "Test"}'
        }

        with patch('requests.post', return_value=mock_response):
            result = selector._call_qwen3_8b("test content", "test prompt", selector.qwen3_8b_settings)

            assert result['moc_category'] == 'Business Operations'
            assert result['confidence_score'] == 0.85

    def test_call_qwen2_5_success(self, minimal_config):
        """Test successful qwen2.5:3b API call"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '{"moc_category": "Life & Misc", "confidence_score": 0.75, "reasoning": "Simple"}'
        }

        with patch('requests.post', return_value=mock_response):
            result = selector._call_qwen2_5_3b("test content", "test prompt", selector.qwen2_5_3b_settings)

            assert result['moc_category'] == 'Life & Misc'
            assert result['confidence_score'] == 0.75

    def test_json_parsing_failure(self, minimal_config):
        """Test handling of invalid JSON response"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'This is not valid JSON'
        }

        with patch('requests.post', return_value=mock_response):
            result = selector._call_qwen3_8b("test content", "test prompt", selector.qwen3_8b_settings)

            assert result['moc_category'] == 'Life & Misc'
            assert result['confidence_score'] == 0.0
            assert 'Failed to parse JSON' in result['reasoning']

    def test_api_timeout_error(self, minimal_config):
        """Test handling of API timeout"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        with patch('requests.post', side_effect=requests.exceptions.Timeout("Timeout")):
            with pytest.raises(requests.exceptions.Timeout):
                selector._call_qwen3_8b("test content", "test prompt", selector.qwen3_8b_settings)

    def test_api_connection_error(self, minimal_config):
        """Test handling of API connection error"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            with pytest.raises(requests.exceptions.ConnectionError):
                selector._call_qwen3_8b("test content", "test prompt", selector.qwen3_8b_settings)


@pytest.mark.unit
class TestCallSelectedModel:
    """Test call_selected_model with fallback"""

    def test_calls_qwen3_for_complex_content(self, minimal_config):
        """Test qwen3:8b is called for complex content"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "Technical business analysis with financial strategy and Python code integration"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '{"moc_category": "Business Operations", "confidence_score": 0.85, "reasoning": "Test"}'
        }

        with patch('requests.post', return_value=mock_response):
            with patch('builtins.print'):  # Suppress print output
                result = selector.call_selected_model(content, "test.md", "Analyze this")

                assert result['moc_category'] == 'Business Operations'

    def test_calls_qwen2_5_for_simple_content(self, minimal_config):
        """Test qwen2.5:3b is called for simple content"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "Simple note about my day"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '{"moc_category": "Life & Misc", "confidence_score": 0.70, "reasoning": "Simple"}'
        }

        with patch('requests.post', return_value=mock_response):
            with patch('builtins.print'):
                result = selector.call_selected_model(content, "note.md", "Analyze this")

                assert result['moc_category'] == 'Life & Misc'

    def test_fallback_to_qwen2_5_on_error(self, minimal_config):
        """Test fallback to qwen2.5:3b when qwen3:8b fails"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)
        content = "Technical business content that should use qwen3"

        # First call (qwen3) fails, second call (qwen2.5) succeeds
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {
            'response': '{"moc_category": "Life & Misc", "confidence_score": 0.60, "reasoning": "Fallback"}'
        }

        with patch('requests.post') as mock_post:
            mock_post.side_effect = [
                requests.exceptions.Timeout("Qwen3 timeout"),
                mock_success
            ]
            with patch('builtins.print'):
                result = selector.call_selected_model(content, "test.md", "Analyze this")

                # Should get result from fallback
                assert result['moc_category'] == 'Life & Misc'
                assert mock_post.call_count == 2


@pytest.mark.integration
class TestModelSelectorIntegration:
    """Integration tests for model selector"""

    def test_end_to_end_workflow(self, full_config):
        """Test complete workflow from content to result"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(full_config)

        test_cases = [
            {
                'content': 'Simple note',
                'file': 'note.md',
                'expected_model': 'qwen2.5:3b'
            },
            {
                'content': 'Technical business analysis with Python API and database integration for revenue optimization',
                'file': 'technical_business_analysis.md',
                'expected_model': 'qwen3:8b'
            }
        ]

        for test in test_cases:
            model, settings = selector.select_model(test['content'], test['file'])
            assert model == test['expected_model']

    def test_threshold_boundary(self, minimal_config):
        """Test behavior at threshold boundary"""
        from intelligent_model_selector import IntelligentModelSelector

        selector = IntelligentModelSelector(minimal_config)

        # Exactly at threshold
        content_at_threshold = " ".join(["word"] * 1000)
        # Just below threshold
        content_below_threshold = " ".join(["word"] * 999)
        # Just above threshold
        content_above_threshold = " ".join(["word"] * 1001)

        analysis_at = selector.analyze_content_complexity(content_at_threshold, "test.md")
        analysis_below = selector.analyze_content_complexity(content_below_threshold, "test.md")
        analysis_above = selector.analyze_content_complexity(content_above_threshold, "test.md")

        # Above threshold should have higher complexity score
        assert analysis_above['complexity_score'] > analysis_below['complexity_score']


@pytest.mark.unit
class TestConfigLoading:
    """Test configuration loading"""

    def test_load_hybrid_config_success(self):
        """Test successful config loading"""
        from intelligent_model_selector import load_hybrid_config

        mock_config = {
            'primary_ollama_model': 'qwen3:8b',
            'secondary_ollama_model': 'qwen2.5:3b'
        }

        with patch('builtins.open', create=True):
            with patch('yaml.safe_load', return_value=mock_config):
                config = load_hybrid_config()
                assert config == mock_config

    def test_load_hybrid_config_file_not_found(self):
        """Test config loading when file doesn't exist"""
        from intelligent_model_selector import load_hybrid_config

        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with patch('builtins.print'):
                config = load_hybrid_config()
                assert config == {}

    def test_load_hybrid_config_yaml_error(self):
        """Test config loading with YAML parse error"""
        from intelligent_model_selector import load_hybrid_config

        with patch('builtins.open', create=True):
            with patch('yaml.safe_load', side_effect=Exception("YAML error")):
                with patch('builtins.print'):
                    config = load_hybrid_config()
                    assert config == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
