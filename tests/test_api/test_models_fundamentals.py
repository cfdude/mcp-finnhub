"""Tests for fundamental data Pydantic models."""

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.fundamentals import (
    BasicFinancials,
    BasicFinancialsResponse,
    DividendData,
    ReportedFinancial,
    ReportedFinancialsResponse,
    RevenueBreakdownData,
    RevenueBreakdownResponse,
    RevenueProduct,
    SecFinancialData,
    SecFinancialsResponse,
    SplitData,
)


class TestBasicFinancials:
    """Tests for BasicFinancials model."""

    def test_valid_basic_financials(self):
        """Test creating valid basic financials."""
        data = {
            "marketCapitalization": 2500000,
            "peBasicExclExtraTTM": 25.5,
            "roeTTM": 0.85,
            "netProfitMarginTTM": 0.25,
        }
        financials = BasicFinancials(**data)
        assert financials.marketCapitalization == 2500000
        assert financials.peBasicExclExtraTTM == 25.5

    def test_has_positive_earnings_true(self):
        """Test has_positive_earnings property returns True."""
        financials = BasicFinancials(peBasicExclExtraTTM=25.5)
        assert financials.has_positive_earnings is True

    def test_has_positive_earnings_false(self):
        """Test has_positive_earnings property returns False."""
        financials = BasicFinancials(peBasicExclExtraTTM=-5.0)
        assert financials.has_positive_earnings is False

    def test_is_profitable_true(self):
        """Test is_profitable property returns True."""
        financials = BasicFinancials(netProfitMarginTTM=0.25)
        assert financials.is_profitable is True

    def test_is_profitable_false(self):
        """Test is_profitable property returns False."""
        financials = BasicFinancials(netProfitMarginTTM=-0.05)
        assert financials.is_profitable is False


class TestBasicFinancialsResponse:
    """Tests for BasicFinancialsResponse model."""

    def test_valid_basic_financials_response(self):
        """Test creating valid basic financials response."""
        data = {
            "symbol": "AAPL",
            "metric": {
                "marketCapitalization": 2500000,
                "peBasicExclExtraTTM": 25.5,
            },
        }
        response = BasicFinancialsResponse(**data)
        assert response.symbol == "AAPL"
        assert response.metric.marketCapitalization == 2500000


class TestReportedFinancial:
    """Tests for ReportedFinancial model."""

    def test_valid_reported_financial(self):
        """Test creating valid reported financial."""
        data = {
            "accessNumber": "0000320193-23-000077",
            "symbol": "AAPL",
            "cik": "0000320193",
            "year": 2023,
            "quarter": 0,
            "form": "10-K",
            "startDate": "2022-09-25",
            "endDate": "2023-09-30",
            "filedDate": "2023-11-03",
            "acceptedDate": "2023-11-03 18:01:14",
            "report": {},
        }
        financial = ReportedFinancial(**data)
        assert financial.symbol == "AAPL"
        assert financial.year == 2023

    def test_invalid_quarter_too_high(self):
        """Test validation fails for quarter > 4."""
        with pytest.raises(ValidationError, match="less than or equal to"):
            ReportedFinancial(
                accessNumber="123",
                symbol="AAPL",
                cik="0000320193",
                year=2023,
                quarter=5,
                form="10-K",
                startDate="2023-01-01",
                endDate="2023-12-31",
                filedDate="2023-11-03",
                acceptedDate="2023-11-03 18:01:14",
                report={},
            )

    def test_is_annual_true(self):
        """Test is_annual property returns True for quarter 0."""
        financial = ReportedFinancial(
            accessNumber="123",
            symbol="AAPL",
            cik="0000320193",
            year=2023,
            quarter=0,
            form="10-K",
            startDate="2023-01-01",
            endDate="2023-12-31",
            filedDate="2023-11-03",
            acceptedDate="2023-11-03 18:01:14",
            report={},
        )
        assert financial.is_annual is True

    def test_is_annual_false(self):
        """Test is_annual property returns False for quarter > 0."""
        financial = ReportedFinancial(
            accessNumber="123",
            symbol="AAPL",
            cik="0000320193",
            year=2023,
            quarter=1,
            form="10-Q",
            startDate="2023-01-01",
            endDate="2023-03-31",
            filedDate="2023-05-03",
            acceptedDate="2023-05-03 18:01:14",
            report={},
        )
        assert financial.is_annual is False


class TestReportedFinancialsResponse:
    """Tests for ReportedFinancialsResponse model."""

    def test_valid_reported_financials_response(self):
        """Test creating valid reported financials response."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {},
                }
            ],
        }
        response = ReportedFinancialsResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.data) == 1

    def test_annual_reports_property(self):
        """Test annual_reports property filters correctly."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {},
                },
                {
                    "accessNumber": "456",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-Q",
                    "startDate": "2023-10-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2024-02-03",
                    "acceptedDate": "2024-02-03 18:01:14",
                    "report": {},
                },
            ],
        }
        response = ReportedFinancialsResponse(**data)
        assert len(response.annual_reports) == 1
        assert response.annual_reports[0].quarter == 0

    def test_quarterly_reports_property(self):
        """Test quarterly_reports property filters correctly."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {},
                },
                {
                    "accessNumber": "456",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-Q",
                    "startDate": "2023-10-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2024-02-03",
                    "acceptedDate": "2024-02-03 18:01:14",
                    "report": {},
                },
            ],
        }
        response = ReportedFinancialsResponse(**data)
        assert len(response.quarterly_reports) == 1
        assert response.quarterly_reports[0].quarter == 4


class TestSecFinancialData:
    """Tests for SecFinancialData model."""

    def test_valid_sec_financial_data(self):
        """Test creating valid SEC financial data."""
        data = {
            "accessNumber": "123",
            "symbol": "AAPL",
            "cik": "0000320193",
            "year": 2023,
            "quarter": 0,
            "form": "10-K",
            "startDate": "2023-01-01",
            "endDate": "2023-12-31",
            "filedDate": "2023-11-03",
            "acceptedDate": "2023-11-03 18:01:14",
            "report": {"bs": []},
        }
        financial = SecFinancialData(**data)
        assert financial.symbol == "AAPL"


class TestSecFinancialsResponse:
    """Tests for SecFinancialsResponse model."""

    def test_valid_sec_financials_response(self):
        """Test creating valid SEC financials response."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {"bs": []},
                }
            ],
        }
        response = SecFinancialsResponse(**data)
        assert response.symbol == "AAPL"


class TestDividendData:
    """Tests for DividendData model."""

    def test_valid_dividend_data(self):
        """Test creating valid dividend data."""
        data = {
            "symbol": "AAPL",
            "date": "2023-11-10",
            "amount": 0.24,
            "adjustedAmount": 0.24,
            "payDate": "2023-11-16",
            "recordDate": "2023-11-13",
            "declarationDate": "2023-11-02",
            "currency": "USD",
        }
        dividend = DividendData(**data)
        assert dividend.symbol == "AAPL"
        assert dividend.amount == 0.24

    def test_invalid_negative_amount(self):
        """Test validation fails for negative amount."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            DividendData(
                symbol="AAPL",
                date="2023-11-10",
                amount=-0.24,
            )


class TestSplitData:
    """Tests for SplitData model."""

    def test_valid_split_data(self):
        """Test creating valid split data."""
        data = {
            "symbol": "AAPL",
            "date": "2020-08-31",
            "fromFactor": 1.0,
            "toFactor": 4.0,
        }
        split = SplitData(**data)
        assert split.symbol == "AAPL"
        assert split.fromFactor == 1.0
        assert split.toFactor == 4.0

    def test_split_ratio_forward_split(self):
        """Test split_ratio property for forward split."""
        split = SplitData(symbol="AAPL", date="2020-08-31", fromFactor=1.0, toFactor=4.0)
        assert split.split_ratio == 4.0

    def test_split_ratio_reverse_split(self):
        """Test split_ratio property for reverse split."""
        split = SplitData(symbol="XYZ", date="2023-01-01", fromFactor=10.0, toFactor=1.0)
        assert split.split_ratio == 0.1

    def test_is_forward_split_true(self):
        """Test is_forward_split property returns True."""
        split = SplitData(symbol="AAPL", date="2020-08-31", fromFactor=1.0, toFactor=4.0)
        assert split.is_forward_split is True

    def test_is_forward_split_false(self):
        """Test is_forward_split property returns False."""
        split = SplitData(symbol="XYZ", date="2023-01-01", fromFactor=10.0, toFactor=1.0)
        assert split.is_forward_split is False

    def test_is_reverse_split_true(self):
        """Test is_reverse_split property returns True."""
        split = SplitData(symbol="XYZ", date="2023-01-01", fromFactor=10.0, toFactor=1.0)
        assert split.is_reverse_split is True

    def test_is_reverse_split_false(self):
        """Test is_reverse_split property returns False."""
        split = SplitData(symbol="AAPL", date="2020-08-31", fromFactor=1.0, toFactor=4.0)
        assert split.is_reverse_split is False


class TestRevenueProduct:
    """Tests for RevenueProduct model."""

    def test_valid_revenue_product(self):
        """Test creating valid revenue product."""
        data = {"product": "iPhone", "revenue": 200616000000}
        product = RevenueProduct(**data)
        assert product.product == "iPhone"
        assert product.revenue == 200616000000


class TestRevenueBreakdownData:
    """Tests for RevenueBreakdownData model."""

    def test_valid_revenue_breakdown_data(self):
        """Test creating valid revenue breakdown data."""
        data = {
            "accessNumber": "123",
            "symbol": "AAPL",
            "cik": "0000320193",
            "year": 2023,
            "quarter": None,
            "breakdown": [
                {"product": "iPhone", "revenue": 200616000000},
                {"product": "Mac", "revenue": 29357000000},
            ],
        }
        breakdown = RevenueBreakdownData(**data)
        assert breakdown.symbol == "AAPL"
        assert len(breakdown.breakdown) == 2


class TestRevenueBreakdownResponse:
    """Tests for RevenueBreakdownResponse model."""

    def test_valid_revenue_breakdown_response(self):
        """Test creating valid revenue breakdown response."""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": None,
                    "breakdown": [
                        {"product": "iPhone", "revenue": 200616000000},
                    ],
                }
            ],
        }
        response = RevenueBreakdownResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.data) == 1
