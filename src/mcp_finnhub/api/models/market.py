"""Pydantic models for market data API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SymbolSearchResponse(BaseModel):
    """Symbol search results wrapper."""

    count: int = Field(description="Number of results")
    result: list[dict[str, str]] = Field(description="Search results")

    @property
    def symbols(self) -> list[str]:
        """Extract list of symbols."""
        return [r.get("symbol", "") for r in self.result if r.get("symbol")]


class FinancialMetric(BaseModel):
    """Single financial metric with label and value."""

    label: str = Field(description="Metric label")
    value: float | str | None = Field(default=None, description="Metric value")


class FinancialReport(BaseModel):
    """Financial report for a single period."""

    year: int = Field(description="Report year")
    quarter: int | None = Field(default=None, description="Report quarter (1-4)")
    form: str = Field(description="Report form type")
    startDate: str = Field(description="Report start date")  # noqa: N815
    endDate: str = Field(description="Report end date")  # noqa: N815
    acceptedDate: str = Field(description="SEC acceptance date")  # noqa: N815
    report: dict[str, list[FinancialMetric]] = Field(description="Financial data by category")

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate year is reasonable."""
        if v < 1900 or v > 2100:
            raise ValueError("Year must be between 1900 and 2100")
        return v

    @field_validator("quarter")
    @classmethod
    def validate_quarter(cls, v: int | None) -> int | None:
        """Validate quarter is 1-4."""
        if v is not None and (v < 1 or v > 4):
            raise ValueError("Quarter must be between 1 and 4")
        return v


class FinancialsResponse(BaseModel):
    """Financial statements response."""

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    data: list[FinancialReport] = Field(description="Financial reports")

    @property
    def latest_report(self) -> FinancialReport | None:
        """Get most recent financial report."""
        return self.data[0] if self.data else None

    @property
    def report_count(self) -> int:
        """Get number of reports."""
        return len(self.data)


class EarningsData(BaseModel):
    """Earnings data for a single period."""

    actual: float | None = Field(default=None, description="Actual EPS")
    estimate: float | None = Field(default=None, description="Estimated EPS")
    period: str = Field(description="Period date (YYYY-MM-DD)")
    quarter: int = Field(description="Quarter number (1-4)")
    surprise: float | None = Field(default=None, description="Earnings surprise")
    surprisePercent: float | None = Field(  # noqa: N815
        default=None, description="Earnings surprise percent"
    )
    symbol: str = Field(description="Stock symbol")
    year: int = Field(description="Year")

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        """Validate period date format."""
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("Period must be in YYYY-MM-DD format") from exc
        return v

    @field_validator("quarter")
    @classmethod
    def validate_quarter(cls, v: int) -> int:
        """Validate quarter is 1-4."""
        if v < 1 or v > 4:
            raise ValueError("Quarter must be between 1 and 4")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate year is reasonable."""
        if v < 1900 or v > 2100:
            raise ValueError("Year must be between 1900 and 2100")
        return v

    @property
    def beat_estimate(self) -> bool | None:
        """Check if actual beat estimate."""
        if self.actual is not None and self.estimate is not None:
            return self.actual > self.estimate
        return None


class EarningsResponse(BaseModel):
    """Earnings history response."""

    earnings: list[EarningsData] = Field(description="Historical earnings")

    @property
    def latest_earnings(self) -> EarningsData | None:
        """Get most recent earnings."""
        return self.earnings[0] if self.earnings else None

    @property
    def earnings_count(self) -> int:
        """Get number of earnings reports."""
        return len(self.earnings)

    @property
    def beat_count(self) -> int:
        """Count how many times beat estimate."""
        return sum(1 for e in self.earnings if e.beat_estimate is True)


__all__ = [
    "EarningsData",
    "EarningsResponse",
    "FinancialMetric",
    "FinancialReport",
    "FinancialsResponse",
    "SymbolSearchResponse",
]
