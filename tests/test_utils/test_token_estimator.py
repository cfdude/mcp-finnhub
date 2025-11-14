"""Unit tests for TokenEstimator.

Tests token counting, JSON estimation, truncation, and batch operations.
"""

from __future__ import annotations

from mcp_finnhub.utils.token_estimator import TokenEstimator


class TestTokenEstimator:
    """Tests for TokenEstimator class."""

    def test_initialization(self):
        """Test TokenEstimator can be initialized."""
        estimator = TokenEstimator()
        assert estimator.encoding is not None
        assert estimator.encoding.name == "cl100k_base"

    def test_custom_encoding(self):
        """Test TokenEstimator with custom encoding."""
        estimator = TokenEstimator(encoding_name="p50k_base")
        assert estimator.encoding.name == "p50k_base"

    def test_estimate_tokens_simple(self):
        """Test estimating tokens for simple text."""
        estimator = TokenEstimator()

        # Simple words
        assert estimator.estimate_tokens("Hello") == 1
        assert estimator.estimate_tokens("Hello world") == 2
        assert estimator.estimate_tokens("Hello, world!") == 4  # punctuation counts

    def test_estimate_tokens_empty_string(self):
        """Test that empty string has zero tokens."""
        estimator = TokenEstimator()
        assert estimator.estimate_tokens("") == 0

    def test_estimate_tokens_multiline(self):
        """Test estimating tokens for multiline text."""
        estimator = TokenEstimator()
        text = """Line 1
Line 2
Line 3"""
        count = estimator.estimate_tokens(text)
        assert count > 0
        assert count < len(text)  # Tokens should be fewer than characters

    def test_estimate_json_tokens_dict(self):
        """Test estimating tokens for dictionary."""
        estimator = TokenEstimator()
        data = {"key": "value", "number": 123, "boolean": True}
        count = estimator.estimate_json_tokens(data)
        assert count > 0

    def test_estimate_json_tokens_list(self):
        """Test estimating tokens for list."""
        estimator = TokenEstimator()
        data = ["item1", "item2", "item3"]
        count = estimator.estimate_json_tokens(data)
        assert count > 0

    def test_estimate_json_tokens_nested(self):
        """Test estimating tokens for nested structure."""
        estimator = TokenEstimator()
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
            "metadata": {"count": 2, "source": "api"},
        }
        count = estimator.estimate_json_tokens(data)
        assert count > 20  # Should have meaningful size

    def test_will_fit_in_context_true(self):
        """Test text that fits within limit."""
        estimator = TokenEstimator()
        text = "Hello world"
        assert estimator.will_fit_in_context(text, limit=100) is True

    def test_will_fit_in_context_false(self):
        """Test text that exceeds limit."""
        estimator = TokenEstimator()
        text = "word " * 100  # Many words
        assert estimator.will_fit_in_context(text, limit=10) is False

    def test_will_fit_in_context_exact(self):
        """Test text that exactly matches limit."""
        estimator = TokenEstimator()
        text = "Hello"
        token_count = estimator.estimate_tokens(text)
        assert estimator.will_fit_in_context(text, limit=token_count) is True
        assert estimator.will_fit_in_context(text, limit=token_count - 1) is False

    def test_truncate_to_token_limit_no_truncation_needed(self):
        """Test truncation when text already fits."""
        estimator = TokenEstimator()
        text = "Hello world"
        result = estimator.truncate_to_token_limit(text, limit=100)
        assert result == text  # No truncation needed

    def test_truncate_to_token_limit_with_truncation(self):
        """Test truncation of text that exceeds limit."""
        estimator = TokenEstimator()
        text = "word " * 100  # Many words
        result = estimator.truncate_to_token_limit(text, limit=20)

        # Result should fit within limit
        assert estimator.estimate_tokens(result) <= 20
        # Result should end with suffix
        assert result.endswith("...")
        # Result should be shorter than original
        assert len(result) < len(text)

    def test_truncate_to_token_limit_custom_suffix(self):
        """Test truncation with custom suffix."""
        estimator = TokenEstimator()
        text = "word " * 100
        result = estimator.truncate_to_token_limit(text, limit=20, suffix=" [truncated]")

        assert estimator.estimate_tokens(result) <= 20
        assert result.endswith(" [truncated]")

    def test_truncate_to_token_limit_empty_string(self):
        """Test truncation of empty string."""
        estimator = TokenEstimator()
        result = estimator.truncate_to_token_limit("", limit=10)
        assert result == ""

    def test_truncate_to_token_limit_very_small_limit(self):
        """Test truncation with limit smaller than suffix."""
        estimator = TokenEstimator()
        text = "This is a long text"
        result = estimator.truncate_to_token_limit(text, limit=1)

        # Should still return something within limit
        assert estimator.estimate_tokens(result) <= 1

    def test_truncate_preserves_token_boundaries(self):
        """Test that truncation happens at token boundaries."""
        estimator = TokenEstimator()
        text = "The quick brown fox jumps over the lazy dog"
        result = estimator.truncate_to_token_limit(text, limit=5, suffix="")

        # Result should decode cleanly (no broken tokens)
        assert isinstance(result, str)
        # Should fit within limit
        assert estimator.estimate_tokens(result) <= 5

    def test_estimate_tokens_batch_empty(self):
        """Test batch estimation with empty list."""
        estimator = TokenEstimator()
        result = estimator.estimate_tokens_batch([])
        assert result == []

    def test_estimate_tokens_batch_multiple(self):
        """Test batch estimation with multiple texts."""
        estimator = TokenEstimator()
        texts = ["Hello", "Hello world", "Hello, world!"]
        result = estimator.estimate_tokens_batch(texts)

        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 4

    def test_estimate_tokens_batch_consistency(self):
        """Test that batch estimation matches individual estimation."""
        estimator = TokenEstimator()
        texts = ["Text 1", "Text 2", "Text 3"]

        batch_result = estimator.estimate_tokens_batch(texts)
        individual_results = [estimator.estimate_tokens(text) for text in texts]

        assert batch_result == individual_results

    def test_get_token_text_ratio_english(self):
        """Test token-to-character ratio for English text."""
        estimator = TokenEstimator()
        text = "The quick brown fox jumps over the lazy dog"
        ratio = estimator.get_token_text_ratio(text)

        # English text typically has ratio between 0.2 and 0.4
        assert 0.1 < ratio < 0.5

    def test_get_token_text_ratio_empty_string(self):
        """Test ratio for empty string."""
        estimator = TokenEstimator()
        ratio = estimator.get_token_text_ratio("")
        assert ratio == 0.0

    def test_get_token_text_ratio_consistent(self):
        """Test that ratio is consistent for similar texts."""
        estimator = TokenEstimator()
        text1 = "Hello world this is a test"
        text2 = "Hello world this is another test"

        ratio1 = estimator.get_token_text_ratio(text1)
        ratio2 = estimator.get_token_text_ratio(text2)

        # Ratios should be similar (within 20%)
        assert abs(ratio1 - ratio2) < 0.2

    def test_unicode_handling(self):
        """Test that Unicode characters are handled correctly."""
        estimator = TokenEstimator()

        # Emoji and special characters
        text = "Hello 👋 世界"
        count = estimator.estimate_tokens(text)
        assert count > 0

        # Should be able to truncate Unicode text
        result = estimator.truncate_to_token_limit(text, limit=5)
        assert isinstance(result, str)

    def test_large_text_performance(self):
        """Test that large text can be processed efficiently."""
        estimator = TokenEstimator()

        # Generate large text (10K words)
        large_text = "word " * 10000

        # Should complete quickly
        count = estimator.estimate_tokens(large_text)
        assert count > 1000

        # Truncation should also work
        result = estimator.truncate_to_token_limit(large_text, limit=100)
        assert estimator.estimate_tokens(result) <= 100
