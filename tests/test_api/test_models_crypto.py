"""Tests for cryptocurrency Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.crypto import CryptoCandleResponse, CryptoProfile, CryptoSymbol


class TestCryptoSymbol:
    """Test suite for CryptoSymbol model."""

    def test_valid_crypto_symbol(self):
        """Test valid crypto symbol creation."""
        data = {
            "description": "Bitcoin/US Dollar",
            "displaySymbol": "BTC/USDT",
            "symbol": "BINANCE:BTCUSDT",
        }
        model = CryptoSymbol(**data)
        assert model.symbol == "BINANCE:BTCUSDT"
        assert model.displaySymbol == "BTC/USDT"

    def test_crypto_symbol_minimal(self):
        """Test crypto symbol with minimal data."""
        data = {}
        model = CryptoSymbol(**data)
        assert model.symbol is None
        assert model.description is None


class TestCryptoProfile:
    """Test suite for CryptoProfile model."""

    def test_valid_crypto_profile(self):
        """Test valid crypto profile creation."""
        data = {
            "name": "Bitcoin",
            "description": "Digital currency",
            "logo": "https://example.com/btc.png",
            "cmc": 1,
            "website": "https://bitcoin.org",
            "whitepaper": "https://bitcoin.org/bitcoin.pdf",
        }
        model = CryptoProfile(**data)
        assert model.name == "Bitcoin"
        assert model.cmc == 1

    def test_crypto_profile_minimal(self):
        """Test crypto profile with minimal data."""
        data = {}
        model = CryptoProfile(**data)
        assert model.name is None
        assert model.cmc is None

    def test_crypto_profile_negative_cmc(self):
        """Test crypto profile with invalid negative CMC ID."""
        data = {
            "name": "Bitcoin",
            "cmc": -1,
        }
        with pytest.raises(ValidationError):
            CryptoProfile(**data)


class TestCryptoCandleResponse:
    """Test suite for CryptoCandleResponse model."""

    def test_valid_crypto_candle_response(self):
        """Test valid crypto candle response creation."""
        data = {
            "c": [45000.0, 45500.0],
            "h": [45200.0, 45700.0],
            "l": [44800.0, 45300.0],
            "o": [44900.0, 45100.0],
            "s": "ok",
            "t": [1609459200, 1609545600],
            "v": [100.5, 120.3],
        }
        model = CryptoCandleResponse(**data)
        assert model.s == "ok"
        assert len(model.c) == 2
        assert model.has_data is True
        assert model.candle_count == 2

    def test_crypto_candle_response_no_data(self):
        """Test crypto candle response with no_data status."""
        data = {
            "s": "no_data",
        }
        model = CryptoCandleResponse(**data)
        assert model.s == "no_data"
        assert model.has_data is False
        assert model.candle_count == 0

    def test_crypto_candle_response_invalid_status(self):
        """Test crypto candle response with invalid status."""
        data = {
            "s": "invalid",
        }
        with pytest.raises(ValidationError):
            CryptoCandleResponse(**data)

    def test_crypto_candle_response_has_data_property(self):
        """Test has_data property."""
        data_ok = {"s": "ok", "t": [1609459200]}
        model_ok = CryptoCandleResponse(**data_ok)
        assert model_ok.has_data is True

        data_no = {"s": "no_data"}
        model_no = CryptoCandleResponse(**data_no)
        assert model_no.has_data is False

    def test_crypto_candle_response_candle_count(self):
        """Test candle_count property."""
        data = {"s": "ok", "t": [1, 2, 3, 4, 5]}
        model = CryptoCandleResponse(**data)
        assert model.candle_count == 5

        data_empty = {"s": "ok"}
        model_empty = CryptoCandleResponse(**data_empty)
        assert model_empty.candle_count == 0
