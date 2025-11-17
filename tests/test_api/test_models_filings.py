"""Tests for SEC filings Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.filings import (
    FilingData,
    FilingSentiment,
    SimilarityIndex,
)


class TestFilingData:
    """Test suite for FilingData model."""

    def test_valid_filing_data(self):
        """Test valid filing data creation."""
        data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
            "cik": "0000320193",
            "form": "10-K",
            "filedDate": "2024-01-15",
            "acceptedDate": "2024-01-15 16:30:00",
            "reportUrl": "https://www.sec.gov/report.html",
            "filingUrl": "https://www.sec.gov/filing.html",
        }
        model = FilingData(**data)
        assert model.accessNumber == "0001193125-24-001234"
        assert model.symbol == "AAPL"
        assert model.form == "10-K"

    def test_filing_data_minimal(self):
        """Test filing data with minimal fields."""
        data = {}
        model = FilingData(**data)
        assert model.accessNumber is None
        assert model.symbol is None
        assert model.form is None

    def test_filing_data_partial(self):
        """Test filing data with partial fields."""
        data = {
            "symbol": "AAPL",
            "form": "10-Q",
            "filedDate": "2024-01-15",
        }
        model = FilingData(**data)
        assert model.symbol == "AAPL"
        assert model.form == "10-Q"
        assert model.accessNumber is None


class TestFilingSentiment:
    """Test suite for FilingSentiment model."""

    def test_valid_filing_sentiment(self):
        """Test valid filing sentiment creation."""
        data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
            "cik": "0000320193",
            "sentiment": {
                "positive": 0.65,
                "negative": 0.15,
                "neutral": 0.20,
            },
            "positiveWord": 150,
            "negativeWord": 35,
        }
        model = FilingSentiment(**data)
        assert model.accessNumber == "0001193125-24-001234"
        assert model.positiveWord == 150
        assert model.negativeWord == 35

    def test_filing_sentiment_minimal(self):
        """Test filing sentiment with minimal fields."""
        data = {}
        model = FilingSentiment(**data)
        assert model.accessNumber is None
        assert model.sentiment is None
        assert model.positiveWord is None

    def test_filing_sentiment_negative_word_count(self):
        """Test filing sentiment with invalid negative word count."""
        data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
            "positiveWord": 150,
            "negativeWord": -10,
        }
        with pytest.raises(ValidationError):
            FilingSentiment(**data)

    def test_filing_sentiment_zero_word_counts(self):
        """Test filing sentiment with zero word counts."""
        data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
            "positiveWord": 0,
            "negativeWord": 0,
        }
        model = FilingSentiment(**data)
        assert model.positiveWord == 0
        assert model.negativeWord == 0


class TestSimilarityIndex:
    """Test suite for SimilarityIndex model."""

    def test_valid_similarity_index(self):
        """Test valid similarity index creation."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "similarity": [
                {
                    "item1": 0.95,
                    "item1a": 0.92,
                    "item7": 0.88,
                }
            ],
        }
        model = SimilarityIndex(**data)
        assert model.symbol == "AAPL"
        assert model.cik == "0000320193"
        assert len(model.similarity) == 1

    def test_similarity_index_minimal(self):
        """Test similarity index with minimal fields."""
        data = {"symbol": "AAPL"}
        model = SimilarityIndex(**data)
        assert model.symbol == "AAPL"
        assert model.cik is None
        assert model.similarity is None

    def test_similarity_index_empty_similarity(self):
        """Test similarity index with empty similarity list."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "similarity": [],
        }
        model = SimilarityIndex(**data)
        assert model.symbol == "AAPL"
        assert len(model.similarity) == 0

    def test_similarity_index_missing_symbol(self):
        """Test similarity index with missing required symbol."""
        data = {
            "cik": "0000320193",
            "similarity": [],
        }
        with pytest.raises(ValidationError):
            SimilarityIndex(**data)
