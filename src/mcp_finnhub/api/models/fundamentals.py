"""Pydantic models for fundamental data responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class BasicFinancials(BaseModel):
    """Basic financial metrics."""

    # Valuation metrics
    marketCapitalization: float | None = Field(  # noqa: N815
        default=None, description="Market capitalization"
    )
    enterpriseValue: float | None = Field(  # noqa: N815
        default=None, description="Enterprise value"
    )
    peBasicExclExtraTTM: float | None = Field(  # noqa: N815
        default=None, description="P/E ratio (trailing 12 months)"
    )
    pbAnnual: float | None = Field(  # noqa: N815
        default=None, description="Price to book ratio"
    )
    psAnnual: float | None = Field(  # noqa: N815
        default=None, description="Price to sales ratio"
    )

    # Profitability metrics
    roeTTM: float | None = Field(  # noqa: N815
        default=None, description="Return on equity TTM"
    )
    roaTTM: float | None = Field(  # noqa: N815
        default=None, description="Return on assets TTM"
    )
    grossMarginTTM: float | None = Field(  # noqa: N815
        default=None, description="Gross margin TTM"
    )
    operatingMarginTTM: float | None = Field(  # noqa: N815
        default=None, description="Operating margin TTM"
    )
    netProfitMarginTTM: float | None = Field(  # noqa: N815
        default=None, description="Net profit margin TTM"
    )

    # Growth metrics
    revenueGrowthTTMYoy: float | None = Field(  # noqa: N815
        default=None, description="Revenue growth YoY"
    )
    epsGrowthTTMYoy: float | None = Field(  # noqa: N815
        default=None, description="EPS growth YoY"
    )

    # Dividend metrics
    dividendYieldIndicatedAnnual: float | None = Field(  # noqa: N815
        default=None, description="Dividend yield"
    )
    dividendPerShareAnnual: float | None = Field(  # noqa: N815
        default=None, description="Dividend per share annual"
    )

    @property
    def has_positive_earnings(self) -> bool:
        """Check if company has positive earnings."""
        return self.peBasicExclExtraTTM is not None and self.peBasicExclExtraTTM > 0

    @property
    def is_profitable(self) -> bool:
        """Check if company is profitable."""
        return self.netProfitMarginTTM is not None and self.netProfitMarginTTM > 0


class BasicFinancialsResponse(BaseModel):
    """Response for basic financials endpoint."""

    symbol: str = Field(description="Stock symbol")
    metric: BasicFinancials = Field(description="Financial metrics")
    series: dict[str, Any] | None = Field(
        default=None, description="Historical series data"
    )


class ReportedFinancial(BaseModel):
    """Single reported financial statement."""

    accessNumber: str = Field(description="SEC access number")  # noqa: N815
    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Fiscal year")
    quarter: int = Field(ge=0, le=4, description="Fiscal quarter (0=annual)")
    form: str = Field(description="SEC form type (10-K, 10-Q)")
    startDate: str = Field(description="Period start date")  # noqa: N815
    endDate: str = Field(description="Period end date")  # noqa: N815
    filedDate: str = Field(description="Filing date")  # noqa: N815
    acceptedDate: str = Field(description="Acceptance date")  # noqa: N815
    report: dict[str, Any] = Field(description="Financial statement data")

    @field_validator("quarter")
    @classmethod
    def validate_quarter(cls, v: int) -> int:
        """Validate quarter is 0-4."""
        if v < 0 or v > 4:
            raise ValueError("Quarter must be between 0 (annual) and 4")
        return v

    @property
    def is_annual(self) -> bool:
        """Check if this is annual report."""
        return self.quarter == 0


class ReportedFinancialsResponse(BaseModel):
    """Response for reported financials endpoint."""

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    data: list[ReportedFinancial] = Field(description="Reported financials")

    @property
    def annual_reports(self) -> list[ReportedFinancial]:
        """Get only annual reports."""
        return [report for report in self.data if report.is_annual]

    @property
    def quarterly_reports(self) -> list[ReportedFinancial]:
        """Get only quarterly reports."""
        return [report for report in self.data if not report.is_annual]


class SecFinancialData(BaseModel):
    """SEC financial data point."""

    accessNumber: str = Field(description="SEC access number")  # noqa: N815
    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Fiscal year")
    quarter: int = Field(ge=0, le=4, description="Fiscal quarter")
    form: str = Field(description="SEC form type")
    startDate: str = Field(description="Period start date")  # noqa: N815
    endDate: str = Field(description="Period end date")  # noqa: N815
    filedDate: str = Field(description="Filing date")  # noqa: N815
    acceptedDate: str = Field(description="Acceptance date")  # noqa: N815
    report: dict[str, Any] = Field(
        description="Standardized financial data"
    )


class SecFinancialsResponse(BaseModel):
    """Response for SEC financials endpoint."""

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    data: list[SecFinancialData] = Field(description="SEC financial statements")


class DividendData(BaseModel):
    """Dividend payment data."""

    symbol: str = Field(description="Stock symbol")
    date: str = Field(description="Ex-dividend date")
    amount: float = Field(ge=0, description="Dividend amount per share")
    adjustedAmount: float | None = Field(  # noqa: N815
        default=None, ge=0, description="Split-adjusted dividend amount"
    )
    payDate: str | None = Field(  # noqa: N815
        default=None, description="Payment date"
    )
    recordDate: str | None = Field(  # noqa: N815
        default=None, description="Record date"
    )
    declarationDate: str | None = Field(  # noqa: N815
        default=None, description="Declaration date"
    )
    currency: str | None = Field(default=None, description="Currency")

    @field_validator("amount", "adjustedAmount")
    @classmethod
    def validate_positive(cls, v: float | None) -> float | None:
        """Validate amount is positive."""
        if v is not None and v < 0:
            raise ValueError("Dividend amount must be positive")
        return v


class SplitData(BaseModel):
    """Stock split data."""

    symbol: str = Field(description="Stock symbol")
    date: str = Field(description="Split date")
    fromFactor: float = Field(  # noqa: N815
        gt=0, description="Split from factor"
    )
    toFactor: float = Field(gt=0, description="Split to factor")  # noqa: N815

    @property
    def split_ratio(self) -> float:
        """Calculate split ratio (e.g., 2.0 for 2-for-1 split)."""
        return self.toFactor / self.fromFactor

    @property
    def is_forward_split(self) -> bool:
        """Check if this is a forward split (increases shares)."""
        return self.split_ratio > 1.0

    @property
    def is_reverse_split(self) -> bool:
        """Check if this is a reverse split (decreases shares)."""
        return self.split_ratio < 1.0


class RevenueProduct(BaseModel):
    """Revenue breakdown by product."""

    product: str = Field(description="Product name")
    revenue: float = Field(description="Revenue amount")


class RevenueGeography(BaseModel):
    """Revenue breakdown by geography."""

    geography: str = Field(description="Geographic region")
    revenue: float = Field(description="Revenue amount")


class RevenueBreakdownData(BaseModel):
    """Revenue breakdown data for a period."""

    accessNumber: str = Field(description="SEC access number")  # noqa: N815
    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Fiscal year")
    quarter: int | None = Field(default=None, ge=0, le=4, description="Fiscal quarter")
    breakdown: list[RevenueProduct] | list[RevenueGeography] = Field(
        description="Revenue breakdown"
    )


class RevenueBreakdownResponse(BaseModel):
    """Response for revenue breakdown endpoint."""

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    data: list[RevenueBreakdownData] = Field(description="Revenue breakdowns")
