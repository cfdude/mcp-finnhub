"""Tests for market data Pydantic models."""

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.market import (
    EarningsData,
    EarningsResponse,
    FinancialMetric,
    FinancialReport,
    FinancialsResponse,
    SymbolSearchResponse,
)


class TestSymbolSearchResponse:
    """Tests for SymbolSearchResponse model."""

    def test_valid_search_response(self):
        """Test creating valid search response."""
        data = {
            "count": 2,
            "result": [
                {"symbol": "AAPL", "description": "Apple Inc"},
                {"symbol": "APLE", "description": "Apple Hospitality"},
            ],
        }
        response = SymbolSearchResponse(**data)
        assert response.count == 2
        assert len(response.result) == 2

    def test_symbols_property(self):
        """Test symbols property extracts symbol list."""
        data = {
            "count": 2,
            "result": [
                {"symbol": "AAPL", "description": "Apple Inc"},
                {"symbol": "APLE", "description": "Apple Hospitality"},
            ],
        }
        response = SymbolSearchResponse(**data)
        assert response.symbols == ["AAPL", "APLE"]


class TestFinancialMetric:
    """Tests for FinancialMetric model."""

    def test_valid_metric_with_float(self):
        """Test creating metric with float value."""
        data = {"label": "Total Assets", "value": 352755000000}
        metric = FinancialMetric(**data)
        assert metric.label == "Total Assets"
        assert metric.value == 352755000000

    def test_valid_metric_with_string(self):
        """Test creating metric with string value."""
        data = {"label": "Entity", "value": "Apple Inc"}
        metric = FinancialMetric(**data)
        assert metric.value == "Apple Inc"

    def test_valid_metric_with_none(self):
        """Test creating metric with None value."""
        data = {"label": "N/A"}
        metric = FinancialMetric(**data)
        assert metric.value is None


class TestFinancialReport:
    """Tests for FinancialReport model."""

    def test_valid_quarterly_report(self):
        """Test creating valid quarterly report."""
        data = {
            "year": 2023,
            "quarter": 4,
            "form": "10-Q",
            "startDate": "2023-07-01",
            "endDate": "2023-09-30",
            "acceptedDate": "2023-11-03 06:01:36",
            "report": {
                "bs": [
                    {"label": "Assets", "value": 352755000000},
                    {"label": "Liabilities", "value": 290437000000},
                ]
            },
        }
        report = FinancialReport(**data)
        assert report.year == 2023
        assert report.quarter == 4
        assert len(report.report["bs"]) == 2

    def test_valid_annual_report(self):
        """Test creating valid annual report without quarter."""
        data = {
            "year": 2023,
            "form": "10-K",
            "startDate": "2022-10-01",
            "endDate": "2023-09-30",
            "acceptedDate": "2023-11-03 06:01:36",
            "report": {"ic": [{"label": "Revenue", "value": 383285000000}]},
        }
        report = FinancialReport(**data)
        assert report.year == 2023
        assert report.quarter is None

    def test_invalid_year(self):
        """Test validation fails for invalid year."""
        with pytest.raises(ValidationError, match="between 1900 and 2100"):
            FinancialReport(
                year=1800,
                form="10-K",
                startDate="2023-01-01",
                endDate="2023-12-31",
                acceptedDate="2024-01-15",
                report={},
            )

    def test_invalid_quarter(self):
        """Test validation fails for invalid quarter."""
        with pytest.raises(ValidationError, match="between 1 and 4"):
            FinancialReport(
                year=2023,
                quarter=5,
                form="10-Q",
                startDate="2023-01-01",
                endDate="2023-03-31",
                acceptedDate="2023-05-01",
                report={},
            )


class TestFinancialsResponse:
    """Tests for FinancialsResponse model."""

    def test_valid_financials_response(self):
        """Test creating valid financials response."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-Q",
                    "startDate": "2023-07-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03",
                    "report": {"bs": [{"label": "Assets", "value": 352755000000}]},
                },
                {
                    "year": 2023,
                    "quarter": 3,
                    "form": "10-Q",
                    "startDate": "2023-04-01",
                    "endDate": "2023-06-30",
                    "acceptedDate": "2023-08-03",
                    "report": {"bs": [{"label": "Assets", "value": 350000000000}]},
                },
            ],
        }
        response = FinancialsResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.data) == 2

    def test_latest_report_property(self):
        """Test latest_report property returns first report."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-Q",
                    "startDate": "2023-07-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03",
                    "report": {},
                },
                {
                    "year": 2023,
                    "quarter": 3,
                    "form": "10-Q",
                    "startDate": "2023-04-01",
                    "endDate": "2023-06-30",
                    "acceptedDate": "2023-08-03",
                    "report": {},
                },
            ],
        }
        response = FinancialsResponse(**data)
        latest = response.latest_report
        assert latest is not None
        assert latest.quarter == 4

    def test_report_count_property(self):
        """Test report_count property."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "year": 2023,
                    "form": "10-K",
                    "startDate": "2022-10-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03",
                    "report": {},
                }
            ],
        }
        response = FinancialsResponse(**data)
        assert response.report_count == 1


class TestEarningsData:
    """Tests for EarningsData model."""

    def test_valid_earnings_data(self):
        """Test creating valid earnings data."""
        data = {
            "actual": 1.52,
            "estimate": 1.43,
            "period": "2023-09-30",
            "quarter": 4,
            "surprise": 0.09,
            "surprisePercent": 6.2937,
            "symbol": "AAPL",
            "year": 2023,
        }
        earnings = EarningsData(**data)
        assert earnings.actual == 1.52
        assert earnings.estimate == 1.43
        assert earnings.quarter == 4

    def test_earnings_with_none_values(self):
        """Test earnings with optional None values."""
        data = {
            "period": "2023-09-30",
            "quarter": 4,
            "symbol": "AAPL",
            "year": 2023,
        }
        earnings = EarningsData(**data)
        assert earnings.actual is None
        assert earnings.estimate is None

    def test_invalid_period_format(self):
        """Test validation fails for invalid period format."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD"):
            EarningsData(
                period="2023/09/30",
                quarter=4,
                symbol="AAPL",
                year=2023,
            )

    def test_invalid_quarter(self):
        """Test validation fails for invalid quarter."""
        with pytest.raises(ValidationError, match="between 1 and 4"):
            EarningsData(
                period="2023-09-30",
                quarter=5,
                symbol="AAPL",
                year=2023,
            )

    def test_invalid_year(self):
        """Test validation fails for invalid year."""
        with pytest.raises(ValidationError, match="between 1900 and 2100"):
            EarningsData(
                period="2023-09-30",
                quarter=4,
                symbol="AAPL",
                year=1800,
            )

    def test_beat_estimate_property_true(self):
        """Test beat_estimate property returns True."""
        data = {
            "actual": 1.52,
            "estimate": 1.43,
            "period": "2023-09-30",
            "quarter": 4,
            "symbol": "AAPL",
            "year": 2023,
        }
        earnings = EarningsData(**data)
        assert earnings.beat_estimate is True

    def test_beat_estimate_property_false(self):
        """Test beat_estimate property returns False."""
        data = {
            "actual": 1.40,
            "estimate": 1.43,
            "period": "2023-09-30",
            "quarter": 4,
            "symbol": "AAPL",
            "year": 2023,
        }
        earnings = EarningsData(**data)
        assert earnings.beat_estimate is False

    def test_beat_estimate_property_none(self):
        """Test beat_estimate property returns None when data missing."""
        data = {
            "period": "2023-09-30",
            "quarter": 4,
            "symbol": "AAPL",
            "year": 2023,
        }
        earnings = EarningsData(**data)
        assert earnings.beat_estimate is None


class TestEarningsResponse:
    """Tests for EarningsResponse model."""

    def test_valid_earnings_response(self):
        """Test creating valid earnings response."""
        data = {
            "earnings": [
                {
                    "actual": 1.52,
                    "estimate": 1.43,
                    "period": "2023-09-30",
                    "quarter": 4,
                    "symbol": "AAPL",
                    "year": 2023,
                },
                {
                    "actual": 1.26,
                    "estimate": 1.19,
                    "period": "2023-06-30",
                    "quarter": 3,
                    "symbol": "AAPL",
                    "year": 2023,
                },
            ]
        }
        response = EarningsResponse(**data)
        assert len(response.earnings) == 2

    def test_latest_earnings_property(self):
        """Test latest_earnings property returns first item."""
        data = {
            "earnings": [
                {
                    "actual": 1.52,
                    "period": "2023-09-30",
                    "quarter": 4,
                    "symbol": "AAPL",
                    "year": 2023,
                },
                {
                    "actual": 1.26,
                    "period": "2023-06-30",
                    "quarter": 3,
                    "symbol": "AAPL",
                    "year": 2023,
                },
            ]
        }
        response = EarningsResponse(**data)
        latest = response.latest_earnings
        assert latest is not None
        assert latest.quarter == 4

    def test_earnings_count_property(self):
        """Test earnings_count property."""
        data = {
            "earnings": [
                {
                    "period": "2023-09-30",
                    "quarter": 4,
                    "symbol": "AAPL",
                    "year": 2023,
                }
            ]
        }
        response = EarningsResponse(**data)
        assert response.earnings_count == 1

    def test_beat_count_property(self):
        """Test beat_count property counts beats."""
        data = {
            "earnings": [
                {
                    "actual": 1.52,
                    "estimate": 1.43,
                    "period": "2023-09-30",
                    "quarter": 4,
                    "symbol": "AAPL",
                    "year": 2023,
                },
                {
                    "actual": 1.26,
                    "estimate": 1.19,
                    "period": "2023-06-30",
                    "quarter": 3,
                    "symbol": "AAPL",
                    "year": 2023,
                },
                {
                    "actual": 1.10,
                    "estimate": 1.15,
                    "period": "2023-03-31",
                    "quarter": 2,
                    "symbol": "AAPL",
                    "year": 2023,
                },
            ]
        }
        response = EarningsResponse(**data)
        assert response.beat_count == 2
