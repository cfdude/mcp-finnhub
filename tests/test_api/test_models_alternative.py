"""Tests for alternative data Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.alternative import (
    ESGScore,
    PatentData,
    Patents,
    SocialSentiment,
    SocialSentimentData,
    SupplyChain,
    SupplyChainRelationship,
)


class TestESGScore:
    """Test suite for ESGScore model."""

    def test_valid_esg_score(self):
        """Test valid ESG score creation."""
        data = {
            "symbol": "AAPL",
            "totalESG": 85.5,
            "environmentScore": 90.2,
            "socialScore": 82.3,
            "governanceScore": 84.0,
        }
        model = ESGScore(**data)
        assert model.symbol == "AAPL"
        assert model.totalESG == 85.5

    def test_esg_score_minimal(self):
        """Test ESG score with minimal data."""
        data = {"symbol": "AAPL"}
        model = ESGScore(**data)
        assert model.symbol == "AAPL"
        assert model.totalESG is None

    def test_esg_score_missing_symbol(self):
        """Test ESG score with missing required symbol."""
        data = {"totalESG": 85.5}
        with pytest.raises(ValidationError):
            ESGScore(**data)


class TestSocialSentiment:
    """Test suite for SocialSentiment models."""

    def test_valid_social_sentiment_data(self):
        """Test valid social sentiment data creation."""
        data = {
            "atTime": "2024-01-15T10:00:00Z",
            "mention": 1500,
            "positiveScore": 0.75,
            "negativeScore": 0.25,
            "score": 0.50,
        }
        model = SocialSentimentData(**data)
        assert model.mention == 1500
        assert model.positiveScore == 0.75

    def test_social_sentiment_data_negative_mention(self):
        """Test social sentiment data with invalid negative mention count."""
        data = {
            "atTime": "2024-01-15T10:00:00Z",
            "mention": -100,
            "positiveScore": 0.75,
            "negativeScore": 0.25,
            "score": 0.50,
        }
        with pytest.raises(ValidationError):
            SocialSentimentData(**data)

    def test_valid_social_sentiment(self):
        """Test valid social sentiment response."""
        data = {
            "symbol": "AAPL",
            "data": [
                {
                    "atTime": "2024-01-15T10:00:00Z",
                    "mention": 1500,
                    "positiveScore": 0.75,
                    "negativeScore": 0.25,
                    "score": 0.50,
                }
            ],
        }
        model = SocialSentiment(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 1

    def test_social_sentiment_empty_data(self):
        """Test social sentiment with empty data list."""
        data = {"symbol": "AAPL", "data": []}
        model = SocialSentiment(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 0


class TestSupplyChain:
    """Test suite for SupplyChain models."""

    def test_valid_supply_chain_relationship(self):
        """Test valid supply chain relationship creation."""
        data = {
            "symbol": "TSM",
            "name": "Taiwan Semiconductor Manufacturing",
            "country": "TW",
        }
        model = SupplyChainRelationship(**data)
        assert model.symbol == "TSM"
        assert model.country == "TW"

    def test_supply_chain_relationship_minimal(self):
        """Test supply chain relationship with minimal data."""
        data = {}
        model = SupplyChainRelationship(**data)
        assert model.symbol is None
        assert model.name is None

    def test_valid_supply_chain(self):
        """Test valid supply chain response."""
        data = {
            "symbol": "AAPL",
            "data": [
                {
                    "symbol": "TSM",
                    "name": "Taiwan Semiconductor Manufacturing",
                    "country": "TW",
                }
            ],
        }
        model = SupplyChain(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 1

    def test_supply_chain_missing_symbol(self):
        """Test supply chain with missing required symbol."""
        data = {"data": []}
        with pytest.raises(ValidationError):
            SupplyChain(**data)


class TestPatents:
    """Test suite for Patents models."""

    def test_valid_patent_data(self):
        """Test valid patent data creation."""
        data = {
            "applicationNumber": "16/123,456",
            "filingDate": "2024-01-15",
            "patentNumber": "US11234567B2",
            "publicationDate": "2024-06-15",
            "title": "Mobile Device Technology",
            "url": "https://patents.uspto.gov/patent/US11234567B2",
        }
        model = PatentData(**data)
        assert model.patentNumber == "US11234567B2"
        assert model.title == "Mobile Device Technology"

    def test_patent_data_minimal(self):
        """Test patent data with minimal fields."""
        data = {}
        model = PatentData(**data)
        assert model.patentNumber is None
        assert model.title is None

    def test_valid_patents(self):
        """Test valid patents response."""
        data = {
            "symbol": "AAPL",
            "data": [
                {
                    "applicationNumber": "16/123,456",
                    "filingDate": "2024-01-15",
                    "patentNumber": "US11234567B2",
                    "publicationDate": "2024-06-15",
                    "title": "Mobile Device Technology",
                    "url": "https://patents.uspto.gov/patent/US11234567B2",
                }
            ],
        }
        model = Patents(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 1

    def test_patents_missing_symbol(self):
        """Test patents with missing required symbol."""
        data = {"data": []}
        with pytest.raises(ValidationError):
            Patents(**data)
