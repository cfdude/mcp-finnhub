"""Token estimation utilities using tiktoken.

Provides token counting and estimation for managing context window usage.
Uses cl100k_base encoding which is compatible with GPT-4 and Claude models.
"""

from __future__ import annotations

import json
from typing import Any

import tiktoken


class TokenEstimator:
    """Token estimation using tiktoken for context window management.

    Uses cl100k_base encoding (GPT-4/Claude) for accurate token counts.
    Useful for determining output size and managing context limits.

    Example:
        >>> estimator = TokenEstimator()
        >>> count = estimator.estimate_tokens("Hello, world!")
        >>> print(f"Tokens: {count}")
        >>> can_fit = estimator.will_fit_in_context(text, limit=1000)
    """

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize TokenEstimator with specified encoding.

        Args:
            encoding_name: Tiktoken encoding name (default: cl100k_base for GPT-4/Claude)
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in a text string.

        Args:
            text: Text to estimate tokens for

        Returns:
            Number of tokens in the text

        Example:
            >>> estimator = TokenEstimator()
            >>> estimator.estimate_tokens("Hello")
            1
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def estimate_json_tokens(self, data: dict[str, Any] | list[Any]) -> int:
        """Estimate number of tokens in a JSON-serializable data structure.

        Args:
            data: Dictionary or list to estimate tokens for

        Returns:
            Number of tokens in the JSON representation

        Example:
            >>> estimator = TokenEstimator()
            >>> estimator.estimate_json_tokens({"key": "value"})
            5
        """
        json_str = json.dumps(data, indent=2)
        return self.estimate_tokens(json_str)

    def will_fit_in_context(self, text: str, limit: int) -> bool:
        """Check if text will fit within a token limit.

        Args:
            text: Text to check
            limit: Maximum token limit

        Returns:
            True if text fits within limit, False otherwise

        Example:
            >>> estimator = TokenEstimator()
            >>> estimator.will_fit_in_context("Hello", limit=1000)
            True
        """
        return self.estimate_tokens(text) <= limit

    def truncate_to_token_limit(self, text: str, limit: int, suffix: str = "...") -> str:
        """Truncate text to fit within a token limit.

        Truncates at token boundaries and adds optional suffix.
        Ensures the result (including suffix) fits within the limit.

        Args:
            text: Text to truncate
            limit: Maximum token limit
            suffix: Suffix to append to truncated text (default: "...")

        Returns:
            Truncated text with suffix if truncation occurred

        Example:
            >>> estimator = TokenEstimator()
            >>> result = estimator.truncate_to_token_limit("A" * 1000, limit=10)
            >>> estimator.estimate_tokens(result) <= 10
            True
        """
        if not text:
            return text

        # If text already fits, return as-is
        if self.will_fit_in_context(text, limit):
            return text

        # Encode text to tokens
        tokens = self.encoding.encode(text)

        # Reserve tokens for suffix
        suffix_tokens = self.encoding.encode(suffix)
        available_tokens = limit - len(suffix_tokens)

        if available_tokens <= 0:
            # If no room for content, return just the suffix truncated
            return self.encoding.decode(tokens[:limit])

        # Truncate to available tokens and decode
        truncated_tokens = tokens[:available_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)

        return truncated_text + suffix

    def estimate_tokens_batch(self, texts: list[str]) -> list[int]:
        """Estimate tokens for multiple texts efficiently.

        Args:
            texts: List of texts to estimate

        Returns:
            List of token counts corresponding to each text

        Example:
            >>> estimator = TokenEstimator()
            >>> estimator.estimate_tokens_batch(["Hello", "World"])
            [1, 1]
        """
        return [self.estimate_tokens(text) for text in texts]

    def get_token_text_ratio(self, text: str) -> float:
        """Calculate the token-to-character ratio for the text.

        Useful for rough estimation without full tokenization.

        Args:
            text: Text to analyze

        Returns:
            Ratio of tokens to characters (typically 0.2-0.4 for English)

        Example:
            >>> estimator = TokenEstimator()
            >>> ratio = estimator.get_token_text_ratio("Hello, world!")
            >>> print(f"Ratio: {ratio:.2f}")
        """
        if not text:
            return 0.0

        token_count = self.estimate_tokens(text)
        char_count = len(text)

        return token_count / char_count if char_count > 0 else 0.0


__all__ = ["TokenEstimator"]
