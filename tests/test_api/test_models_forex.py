"""Tests for forex Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.forex import ForexCandleResponse, ForexRate, ForexSymbol


class TestForexSymbol:
    """Test suite for ForexSymbol model."""

    def test_valid_forex_symbol(self):
        """Test valid forex symbol creation."""
        data = {"description": "EUR/USD", "displaySymbol": "EUR/USD", "symbol": "OANDA:EUR_USD"}
        model = ForexSymbol(**data)
        assert model.symbol == "OANDA:EUR_USD"

    def test_forex_symbol_minimal(self):
        """Test forex symbol with minimal data."""
        data = {}
        model = ForexSymbol(**data)
        assert model.symbol is None


class TestForexCandleResponse:
    """Test suite for ForexCandleResponse model."""

    def test_valid_forex_candle_response(self):
        """Test valid forex candle response creation."""
        data = {"c": [1.18], "h": [1.19], "l": [1.17], "o": [1.175], "s": "ok", "t": [1609459200]}
        model = ForexCandleResponse(**data)
        assert model.s == "ok"
        assert model.has_data is True
        assert model.candle_count == 1

    def test_forex_candle_response_no_data(self):
        """Test forex candle response with no_data status."""
        data = {"s": "no_data"}
        model = ForexCandleResponse(**data)
        assert model.has_data is False
        assert model.candle_count == 0

    def test_forex_candle_response_invalid_status(self):
        """Test forex candle response with invalid status."""
        data = {"s": "invalid"}
        with pytest.raises(ValidationError):
            ForexCandleResponse(**data)


class TestForexRate:
    """Test suite for ForexRate model."""

    def test_valid_forex_rate(self):
        """Test valid forex rate creation."""
        data = {"base": "USD", "quote": {"EUR": 0.85, "GBP": 0.73}}
        model = ForexRate(**data)
        assert model.base == "USD"
        assert model.quote["EUR"] == 0.85

    def test_forex_rate_minimal(self):
        """Test forex rate with minimal data."""
        data = {}
        model = ForexRate(**data)
        assert model.base is None
