"""
Unit tests for Ollama AI integration
Tests the call_ollama function with various scenarios
"""

import pytest
import json
import requests
from unittest.mock import Mock, patch, MagicMock
import time


# Import the function to test
# We'll need to import from the main module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def ollama_config():
    """Configuration for Ollama tests"""
    return {
        'base_url': 'http://localhost:11434',
        'model': 'qwen3:8b',
        'timeout': 300,
        'max_retries': 5,
        'temperature': 0.1,
        'max_tokens': 1024
    }


@pytest.mark.unit
@pytest.mark.ai
class TestOllamaIntegration:
    """Test suite for Ollama API integration"""

    def test_call_ollama_success(self, mock_ollama_success, ollama_config):
        """Test successful Ollama API call"""
        # Import here to avoid issues with global config
        from obsidian_auto_linker_enhanced import call_ollama

        result = call_ollama("Test prompt", "Test system prompt")

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_call_ollama_with_json_response(self, ollama_config):
        """Test Ollama returns valid JSON"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'response': json.dumps({
                    'moc_category': 'Technical & Automation',
                    'confidence_score': 0.85
                })
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            result = call_ollama("Analyze this content")

            assert result is not None
            # Should be able to parse as JSON
            parsed = json.loads(result)
            assert 'moc_category' in parsed

    def test_call_ollama_timeout_retry(self, mock_ollama_timeout, ollama_config):
        """Test Ollama timeout triggers retry logic"""
        from obsidian_auto_linker_enhanced import call_ollama

        # Should retry on timeout
        result = call_ollama("Test prompt", max_retries=2)

        # Should return empty string after all retries fail
        assert result == ""
        # Verify it tried to call multiple times
        assert mock_ollama_timeout.call_count == 2

    def test_call_ollama_exponential_backoff(self, ollama_config):
        """Test exponential backoff between retries"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Timeout")

            with patch('time.sleep') as mock_sleep:
                from obsidian_auto_linker_enhanced import call_ollama
                result = call_ollama("Test prompt", max_retries=3)

                # Verify exponential backoff: 1s, 2s, 4s
                assert mock_sleep.call_count == 2  # One less than retries
                # Check sleep times (2^0, 2^1)
                sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
                assert sleep_calls == [1, 2]

    def test_call_ollama_request_exception(self, mock_ollama_error, ollama_config):
        """Test handling of request exceptions"""
        from obsidian_auto_linker_enhanced import call_ollama

        result = call_ollama("Test prompt", max_retries=2)

        # Should return empty string after failures
        assert result == ""
        assert mock_ollama_error.call_count == 2

    def test_call_ollama_invalid_json_response(self, ollama_config):
        """Test handling of invalid JSON in response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'response': 'This is not valid JSON'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            result = call_ollama("Test prompt")

            # Should still return the response even if not JSON
            assert result == 'This is not valid JSON'

    def test_call_ollama_empty_response(self, ollama_config):
        """Test handling of empty response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'response': ''}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            result = call_ollama("Test prompt")

            assert result == ""

    def test_call_ollama_timeout_increases_with_retries(self, ollama_config):
        """Test that timeout increases with each retry"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Timeout")

            from obsidian_auto_linker_enhanced import call_ollama
            call_ollama("Test prompt", max_retries=3)

            # Verify timeout increases for each attempt
            timeouts = []
            for call in mock_post.call_args_list:
                if 'timeout' in call.kwargs:
                    timeouts.append(call.kwargs['timeout'])

            # Timeout should increase: base, base+180, base+360
            assert len(timeouts) > 0
            # Each should be larger than previous
            for i in range(1, len(timeouts)):
                assert timeouts[i] > timeouts[i-1]

    def test_call_ollama_with_markdown_cleanup(self, ollama_config):
        """Test cleanup of markdown code blocks in response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            # Response wrapped in markdown code block
            mock_response.json.return_value = {
                'response': '```json\n{"moc_category": "Test"}\n```'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            result = call_ollama("Test prompt")

            # Should strip markdown markers
            assert '```' not in result
            assert result.strip() == '{"moc_category": "Test"}'

    @pytest.mark.slow
    def test_call_ollama_performance(self, mock_ollama_success, ollama_config):
        """Ensure mocked Ollama calls execute without blocking by asserting invocation counts instead of timing."""
        from obsidian_auto_linker_enhanced import call_ollama

        result = call_ollama("Test prompt")

        assert result is not None
        assert mock_ollama_success.call_count == 1

    def test_call_ollama_payload_structure(self, ollama_config):
        """Test that the API payload is correctly structured"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'response': 'OK'}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            call_ollama("Test prompt", "System prompt")

            # Verify the payload structure
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']

            assert 'model' in payload
            assert 'prompt' in payload
            assert 'stream' in payload
            assert 'options' in payload
            assert payload['stream'] is False

            # Verify options
            options = payload['options']
            assert 'temperature' in options
            assert 'top_p' in options
            assert 'num_ctx' in options

    def test_call_ollama_combines_prompts(self, ollama_config):
        """Test that system and user prompts are combined correctly"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'response': 'OK'}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            call_ollama("User prompt", "System prompt")

            # Verify prompts are combined
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']

            assert 'System prompt' in payload['prompt']
            assert 'User prompt' in payload['prompt']

    def test_call_ollama_stop_tokens(self, ollama_config):
        """Test that stop tokens are included in options"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'response': 'OK'}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import call_ollama
            call_ollama("Test prompt")

            # Verify stop tokens
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']
            options = payload['options']

            assert 'stop' in options
            assert isinstance(options['stop'], list)
            assert '```' in options['stop']
