"""Tests for technical analysis Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.technical import (
    AggregateSignalsResponse,
    IndicatorResponse,
    IndicatorValue,
    Pattern,
    PatternRecognitionResponse,
    SignalCount,
    SupportResistanceLevel,
    SupportResistanceResponse,
    TechnicalAnalysis,
    TrendInfo,
)


class TestIndicatorValue:
    """Tests for IndicatorValue model."""

    def test_valid_indicator_value(self):
        """Test creating valid indicator value."""
        data = {"t": 1609459200, "v": 45.5}
        value = IndicatorValue(**data)
        assert value.t == 1609459200
        assert value.v == 45.5

    def test_timestamp_conversion(self):
        """Test timestamp to datetime conversion."""
        value = IndicatorValue(t=1609459200, v=45.5)
        dt = value.timestamp_dt
        assert isinstance(dt, datetime)
        assert dt.timestamp() == 1609459200

    def test_invalid_timestamp(self):
        """Test validation fails for invalid timestamp."""
        with pytest.raises(ValidationError, match="after year 2000"):
            IndicatorValue(t=100, v=45.5)


class TestIndicatorResponse:
    """Tests for IndicatorResponse model."""

    def test_valid_indicator_response(self):
        """Test creating valid indicator response."""
        data = {
            "symbol": "AAPL",
            "indicator": "rsi",
            "resolution": "D",
            "data": [
                {"t": 1609459200, "v": 45.5},
                {"t": 1609545600, "v": 52.3},
            ],
        }
        response = IndicatorResponse(**data)
        assert response.symbol == "AAPL"
        assert response.indicator == "rsi"
        assert len(response.data) == 2

    def test_values_property(self):
        """Test values property extracts indicator values."""
        data = {
            "symbol": "AAPL",
            "indicator": "rsi",
            "resolution": "D",
            "data": [
                {"t": 1609459200, "v": 45.5},
                {"t": 1609545600, "v": 52.3},
            ],
        }
        response = IndicatorResponse(**data)
        assert response.values == [45.5, 52.3]

    def test_timestamps_property(self):
        """Test timestamps property extracts timestamps."""
        data = {
            "symbol": "AAPL",
            "indicator": "rsi",
            "resolution": "D",
            "data": [
                {"t": 1609459200, "v": 45.5},
                {"t": 1609545600, "v": 52.3},
            ],
        }
        response = IndicatorResponse(**data)
        assert response.timestamps == [1609459200, 1609545600]

    def test_timestamps_dt_property(self):
        """Test timestamps_dt property returns datetime objects."""
        data = {
            "symbol": "AAPL",
            "indicator": "rsi",
            "resolution": "D",
            "data": [
                {"t": 1609459200, "v": 45.5},
            ],
        }
        response = IndicatorResponse(**data)
        timestamps_dt = response.timestamps_dt
        assert len(timestamps_dt) == 1
        assert isinstance(timestamps_dt[0], datetime)


class TestSignalCount:
    """Tests for SignalCount model."""

    def test_valid_signal_count(self):
        """Test creating valid signal count."""
        data = {"buy": 5, "neutral": 3, "sell": 2}
        count = SignalCount(**data)
        assert count.buy == 5
        assert count.neutral == 3
        assert count.sell == 2


class TestTechnicalAnalysis:
    """Tests for TechnicalAnalysis model."""

    def test_valid_technical_analysis(self):
        """Test creating valid technical analysis."""
        data = {
            "count": {"buy": 5, "neutral": 3, "sell": 2},
            "signal": "buy",
        }
        analysis = TechnicalAnalysis(**data)
        assert analysis.signal == "buy"
        assert analysis.count.buy == 5

    def test_signal_case_normalization(self):
        """Test signal is normalized to lowercase."""
        data = {
            "count": {"buy": 5, "neutral": 3, "sell": 2},
            "signal": "BUY",
        }
        analysis = TechnicalAnalysis(**data)
        assert analysis.signal == "buy"

    def test_invalid_signal(self):
        """Test validation fails for invalid signal."""
        with pytest.raises(ValidationError):
            TechnicalAnalysis(
                count={"buy": 5, "neutral": 3, "sell": 2},
                signal="invalid",
            )


class TestTrendInfo:
    """Tests for TrendInfo model."""

    def test_valid_trend_info(self):
        """Test creating valid trend info."""
        data = {"adx": 25.5, "trending": True}
        trend = TrendInfo(**data)
        assert trend.adx == 25.5
        assert trend.trending is True


class TestAggregateSignalsResponse:
    """Tests for AggregateSignalsResponse model."""

    def test_valid_response(self):
        """Test creating valid aggregate signals response."""
        data = {
            "symbol": "AAPL",
            "technicalAnalysis": {
                "count": {"buy": 5, "neutral": 3, "sell": 2},
                "signal": "buy",
            },
            "trend": {"adx": 25.5, "trending": True},
        }
        response = AggregateSignalsResponse(**data)
        assert response.symbol == "AAPL"
        assert response.overall_signal == "buy"
        assert response.is_trending is True
        assert response.technicalAnalysis.count.buy == 5


class TestPattern:
    """Tests for Pattern model."""

    def test_valid_pattern(self):
        """Test creating valid pattern."""
        data = {
            "patternName": "Double Top",
            "patternType": "M",
            "mature": True,
            "entryPoint": 150.0,
            "target": 160.0,
            "stopLoss": 145.0,
        }
        pattern = Pattern(**data)
        assert pattern.patternName == "Double Top"
        assert pattern.mature is True

    def test_pattern_without_optional_fields(self):
        """Test pattern without optional price fields."""
        data = {
            "patternName": "Head and Shoulders",
            "patternType": "M",
            "mature": False,
        }
        pattern = Pattern(**data)
        assert pattern.entryPoint is None
        assert pattern.target is None
        assert pattern.stopLoss is None


class TestPatternRecognitionResponse:
    """Tests for PatternRecognitionResponse model."""

    def test_valid_response(self):
        """Test creating valid pattern recognition response."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "patterns": [
                {
                    "patternName": "Double Top",
                    "patternType": "M",
                    "mature": True,
                },
                {
                    "patternName": "Triangle",
                    "patternType": "W",
                    "mature": False,
                },
            ],
        }
        response = PatternRecognitionResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.patterns) == 2

    def test_mature_patterns_property(self):
        """Test mature_patterns property filters mature patterns."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "patterns": [
                {"patternName": "Double Top", "patternType": "M", "mature": True},
                {"patternName": "Triangle", "patternType": "W", "mature": False},
                {"patternName": "Cup & Handle", "patternType": "W", "mature": True},
            ],
        }
        response = PatternRecognitionResponse(**data)
        mature = response.mature_patterns
        assert len(mature) == 2
        assert all(p.mature for p in mature)

    def test_pattern_count_property(self):
        """Test pattern_count property."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "patterns": [
                {"patternName": "Double Top", "patternType": "M", "mature": True},
                {"patternName": "Triangle", "patternType": "W", "mature": False},
            ],
        }
        response = PatternRecognitionResponse(**data)
        assert response.pattern_count == 2


class TestSupportResistanceLevel:
    """Tests for SupportResistanceLevel model."""

    def test_valid_support_level(self):
        """Test creating valid support level."""
        data = {"level": 145.0, "type": "support"}
        level = SupportResistanceLevel(**data)
        assert level.level == 145.0
        assert level.type == "support"

    def test_valid_resistance_level(self):
        """Test creating valid resistance level."""
        data = {"level": 160.0, "type": "resistance"}
        level = SupportResistanceLevel(**data)
        assert level.type == "resistance"

    def test_type_case_normalization(self):
        """Test type is normalized to lowercase."""
        data = {"level": 150.0, "type": "SUPPORT"}
        level = SupportResistanceLevel(**data)
        assert level.type == "support"

    def test_invalid_type(self):
        """Test validation fails for invalid type."""
        with pytest.raises(ValidationError):
            SupportResistanceLevel(level=150.0, type="invalid")


class TestSupportResistanceResponse:
    """Tests for SupportResistanceResponse model."""

    def test_valid_response(self):
        """Test creating valid support/resistance response."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "levels": [
                {"level": 145.0, "type": "support"},
                {"level": 150.0, "type": "support"},
                {"level": 160.0, "type": "resistance"},
                {"level": 165.0, "type": "resistance"},
            ],
        }
        response = SupportResistanceResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.levels) == 4

    def test_support_levels_property(self):
        """Test support_levels property filters support levels."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "levels": [
                {"level": 145.0, "type": "support"},
                {"level": 150.0, "type": "support"},
                {"level": 160.0, "type": "resistance"},
            ],
        }
        response = SupportResistanceResponse(**data)
        support = response.support_levels
        assert support == [145.0, 150.0]

    def test_resistance_levels_property(self):
        """Test resistance_levels property filters resistance levels."""
        data = {
            "symbol": "AAPL",
            "resolution": "D",
            "levels": [
                {"level": 145.0, "type": "support"},
                {"level": 160.0, "type": "resistance"},
                {"level": 165.0, "type": "resistance"},
            ],
        }
        response = SupportResistanceResponse(**data)
        resistance = response.resistance_levels
        assert resistance == [160.0, 165.0]
