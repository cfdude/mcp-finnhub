"""Tests for estimates Pydantic models."""

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.estimates import (
    EarningsEstimateInfo,
    EarningsEstimates,
    EbitdaEstimateInfo,
    EbitdaEstimates,
    PriceTarget,
    RecommendationTrend,
    RevenueEstimateInfo,
    RevenueEstimates,
)


class TestEarningsEstimateInfo:
    """Test EarningsEstimateInfo model."""

    def test_valid_earnings_estimate_info(self):
        """Test creating valid earnings estimate info."""
        data = {
            "epsAvg": 1.25,
            "epsHigh": 1.50,
            "epsLow": 1.00,
            "numberAnalysts": 30,
            "period": "2024-03-31",
            "year": 2024,
            "quarter": 1,
        }
        model = EarningsEstimateInfo(**data)
        assert model.epsAvg == 1.25
        assert model.numberAnalysts == 30
        assert model.quarter == 1

    def test_is_annual_property(self):
        """Test is_annual property."""
        quarterly = EarningsEstimateInfo(epsAvg=1.25, period="2024-03-31", year=2024, quarter=1)
        assert not quarterly.is_annual

        annual = EarningsEstimateInfo(epsAvg=5.00, period="2024-12-31", year=2024, quarter=0)
        assert annual.is_annual

    def test_estimate_range_property(self):
        """Test estimate_range property."""
        model = EarningsEstimateInfo(epsAvg=1.25, epsHigh=1.50, epsLow=1.00, period="2024-03-31")
        assert model.estimate_range == 0.50

    def test_invalid_negative_analysts(self):
        """Test validation fails for negative analysts."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            EarningsEstimateInfo(
                epsAvg=1.25,
                numberAnalysts=-5,
                period="2024-03-31",
            )

    def test_invalid_quarter_too_high(self):
        """Test validation fails for quarter > 4."""
        with pytest.raises(ValidationError, match="less than or equal to"):
            EarningsEstimateInfo(
                epsAvg=1.25,
                quarter=5,
                period="2024-03-31",
            )


class TestEarningsEstimates:
    """Test EarningsEstimates model."""

    def test_valid_earnings_estimates(self):
        """Test creating valid earnings estimates."""
        data = {
            "data": [
                {
                    "epsAvg": 1.25,
                    "epsHigh": 1.50,
                    "epsLow": 1.00,
                    "numberAnalysts": 30,
                    "period": "2024-03-31",
                    "year": 2024,
                    "quarter": 1,
                }
            ],
            "freq": "quarterly",
            "symbol": "AAPL",
        }
        model = EarningsEstimates(**data)
        assert model.symbol == "AAPL"
        assert model.freq == "quarterly"
        assert len(model.data) == 1
        assert model.data[0].epsAvg == 1.25

    def test_invalid_freq(self):
        """Test validation fails for invalid frequency."""
        with pytest.raises(ValidationError, match="freq must be"):
            EarningsEstimates(
                data=[],
                freq="monthly",
                symbol="AAPL",
            )


class TestRevenueEstimateInfo:
    """Test RevenueEstimateInfo model."""

    def test_valid_revenue_estimate_info(self):
        """Test creating valid revenue estimate info."""
        data = {
            "revenueAvg": 100000000000,
            "revenueHigh": 110000000000,
            "revenueLow": 90000000000,
            "numberAnalysts": 25,
            "period": "2024-03-31",
            "year": 2024,
            "quarter": 1,
        }
        model = RevenueEstimateInfo(**data)
        assert model.revenueAvg == 100000000000
        assert model.numberAnalysts == 25

    def test_estimate_range_property(self):
        """Test estimate_range property."""
        model = RevenueEstimateInfo(
            revenueAvg=100000000000,
            revenueHigh=110000000000,
            revenueLow=90000000000,
            period="2024-03-31",
        )
        assert model.estimate_range == 20000000000


class TestRevenueEstimates:
    """Test RevenueEstimates model."""

    def test_valid_revenue_estimates(self):
        """Test creating valid revenue estimates."""
        data = {
            "data": [
                {
                    "revenueAvg": 100000000000,
                    "revenueHigh": 110000000000,
                    "revenueLow": 90000000000,
                    "numberAnalysts": 25,
                    "period": "2024-03-31",
                    "year": 2024,
                    "quarter": 1,
                }
            ],
            "freq": "annual",
            "symbol": "TSLA",
        }
        model = RevenueEstimates(**data)
        assert model.symbol == "TSLA"
        assert model.freq == "annual"
        assert len(model.data) == 1


class TestEbitdaEstimateInfo:
    """Test EbitdaEstimateInfo model."""

    def test_valid_ebitda_estimate_info(self):
        """Test creating valid EBITDA estimate info."""
        data = {
            "ebitdaAvg": 25000000000,
            "ebitdaHigh": 28000000000,
            "ebitdaLow": 22000000000,
            "numberAnalysts": 20,
            "period": "2024-12-31",
            "year": 2024,
            "quarter": 0,
        }
        model = EbitdaEstimateInfo(**data)
        assert model.ebitdaAvg == 25000000000
        assert model.is_annual  # quarter=0 means annual


class TestEbitdaEstimates:
    """Test EbitdaEstimates model."""

    def test_valid_ebitda_estimates(self):
        """Test creating valid EBITDA estimates."""
        data = {
            "data": [
                {
                    "ebitdaAvg": 25000000000,
                    "ebitdaHigh": 28000000000,
                    "ebitdaLow": 22000000000,
                    "numberAnalysts": 20,
                    "period": "2024-12-31",
                    "year": 2024,
                    "quarter": 0,
                }
            ],
            "freq": "annual",
            "symbol": "MSFT",
        }
        model = EbitdaEstimates(**data)
        assert model.symbol == "MSFT"
        assert model.freq == "annual"


class TestPriceTarget:
    """Test PriceTarget model."""

    def test_valid_price_target(self):
        """Test creating valid price target."""
        data = {
            "symbol": "NFLX",
            "targetHigh": 500.0,
            "targetLow": 300.0,
            "targetMean": 400.0,
            "targetMedian": 395.0,
            "numberAnalysts": 35,
            "lastUpdated": "2024-01-15 00:00:00",
        }
        model = PriceTarget(**data)
        assert model.symbol == "NFLX"
        assert model.targetMean == 400.0
        assert model.numberAnalysts == 35

    def test_target_range_property(self):
        """Test target_range property."""
        model = PriceTarget(
            symbol="NFLX",
            targetHigh=500.0,
            targetLow=300.0,
            targetMean=400.0,
        )
        assert model.target_range == 200.0

    def test_upside_from_mean_property(self):
        """Test upside_from_mean property."""
        model = PriceTarget(
            symbol="NFLX",
            targetMean=400.0,
        )
        assert model.upside_from_mean == 400.0

    def test_invalid_negative_analysts(self):
        """Test validation fails for negative analysts."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            PriceTarget(
                symbol="NFLX",
                numberAnalysts=-10,
            )


class TestRecommendationTrend:
    """Test RecommendationTrend model."""

    def test_valid_recommendation_trend(self):
        """Test creating valid recommendation trend."""
        data = {
            "symbol": "AAPL",
            "buy": 20,
            "hold": 5,
            "sell": 1,
            "strongBuy": 10,
            "strongSell": 0,
            "period": "2024-01-01",
        }
        model = RecommendationTrend(**data)
        assert model.symbol == "AAPL"
        assert model.buy == 20
        assert model.strongBuy == 10

    def test_total_recommendations_property(self):
        """Test total_recommendations property."""
        model = RecommendationTrend(
            symbol="AAPL",
            buy=20,
            hold=5,
            sell=1,
            strongBuy=10,
            strongSell=0,
        )
        assert model.total_recommendations == 36

    def test_bullish_ratio_property(self):
        """Test bullish_ratio property."""
        model = RecommendationTrend(
            symbol="AAPL",
            buy=20,
            hold=5,
            sell=1,
            strongBuy=10,
            strongSell=0,
        )
        # (20 + 10) / 36 = 0.833...
        assert model.bullish_ratio is not None
        assert round(model.bullish_ratio, 2) == 0.83

    def test_bearish_ratio_property(self):
        """Test bearish_ratio property."""
        model = RecommendationTrend(
            symbol="AAPL",
            buy=20,
            hold=5,
            sell=1,
            strongBuy=10,
            strongSell=0,
        )
        # (1 + 0) / 36 = 0.0277...
        assert model.bearish_ratio is not None
        assert round(model.bearish_ratio, 2) == 0.03

    def test_invalid_negative_recommendations(self):
        """Test validation fails for negative recommendation counts."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            RecommendationTrend(
                symbol="AAPL",
                buy=-5,
            )

    def test_empty_recommendations_ratios(self):
        """Test ratio properties with zero total recommendations."""
        model = RecommendationTrend(
            symbol="AAPL",
            buy=0,
            hold=0,
            sell=0,
            strongBuy=0,
            strongSell=0,
        )
        assert model.total_recommendations == 0
        assert model.bullish_ratio is None
        assert model.bearish_ratio is None
