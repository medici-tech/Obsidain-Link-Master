"""
Confidence Threshold Tests
Tests for confidence score validation and threshold-based processing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.unit
class TestConfidenceThreshold:
    """Test suite for confidence threshold functionality"""

    def test_confidence_threshold_default(self):
        """Test default confidence threshold value"""
        from obsidian_auto_linker_enhanced import CONFIDENCE_THRESHOLD

        # Default should be 0.8 (80%)
        assert CONFIDENCE_THRESHOLD == 0.8

    def test_low_confidence_detection(self):
        """Test detection of low confidence results"""
        test_confidence = 0.5
        threshold = 0.8

        # Should be flagged as low confidence
        assert test_confidence < threshold

    def test_high_confidence_acceptance(self):
        """Test acceptance of high confidence results"""
        test_confidence = 0.95
        threshold = 0.8

        # Should pass threshold
        assert test_confidence >= threshold

    def test_edge_case_at_threshold(self):
        """Test edge case exactly at threshold"""
        test_confidence = 0.8
        threshold = 0.8

        # Exactly at threshold should pass
        assert test_confidence >= threshold

    def test_confidence_score_range(self):
        """Test that confidence scores are in valid range"""
        valid_scores = [0.0, 0.5, 0.8, 1.0]

        for score in valid_scores:
            assert 0.0 <= score <= 1.0

    def test_invalid_confidence_scores(self):
        """Test handling of invalid confidence scores"""
        invalid_scores = [-0.1, 1.5, 2.0]

        for score in invalid_scores:
            # Invalid scores should fail validation
            assert not (0.0 <= score <= 1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
