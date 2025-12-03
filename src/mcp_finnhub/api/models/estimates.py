"""Pydantic models for Finnhub stock estimates data."""

from pydantic import BaseModel, Field, field_validator


class EarningsEstimateInfo(BaseModel):
    """Individual earnings estimate data point."""

    epsAvg: float | None = Field(default=None, description="Average EPS estimate")  # noqa: N815
    epsHigh: float | None = Field(default=None, description="Highest EPS estimate")  # noqa: N815
    epsLow: float | None = Field(default=None, description="Lowest EPS estimate")  # noqa: N815
    numberAnalysts: int | None = Field(default=None, ge=0, description="Number of analysts")  # noqa: N815
    period: str | None = Field(default=None, description="Period (YYYY-MM-DD)")
    year: int | None = Field(default=None, description="Fiscal year")
    quarter: int | None = Field(default=None, ge=0, le=4, description="Fiscal quarter (1-4)")

    @property
    def is_annual(self) -> bool:
        """Check if this is an annual estimate."""
        return self.quarter is None or self.quarter == 0

    @property
    def estimate_range(self) -> float | None:
        """Calculate the range between high and low estimates."""
        if self.epsHigh is not None and self.epsLow is not None:
            return self.epsHigh - self.epsLow
        return None


class EarningsEstimates(BaseModel):
    """Earnings (EPS) estimates response."""

    data: list[EarningsEstimateInfo] = Field(description="List of earnings estimates")
    freq: str | None = Field(default=None, description="Frequency (annual/quarterly)")
    symbol: str = Field(description="Stock symbol")

    @field_validator("freq")
    @classmethod
    def validate_freq(cls, v: str | None) -> str | None:
        """Validate frequency."""
        if v is not None and v not in {"annual", "quarterly"}:
            raise ValueError(f"freq must be 'annual' or 'quarterly', got: {v}")
        return v


class RevenueEstimateInfo(BaseModel):
    """Individual revenue estimate data point."""

    revenueAvg: float | None = Field(default=None, description="Average revenue estimate")  # noqa: N815
    revenueHigh: float | None = Field(default=None, description="Highest revenue estimate")  # noqa: N815
    revenueLow: float | None = Field(default=None, description="Lowest revenue estimate")  # noqa: N815
    numberAnalysts: int | None = Field(default=None, ge=0, description="Number of analysts")  # noqa: N815
    period: str | None = Field(default=None, description="Period (YYYY-MM-DD)")
    year: int | None = Field(default=None, description="Fiscal year")
    quarter: int | None = Field(default=None, ge=0, le=4, description="Fiscal quarter (1-4)")

    @property
    def is_annual(self) -> bool:
        """Check if this is an annual estimate."""
        return self.quarter is None or self.quarter == 0

    @property
    def estimate_range(self) -> float | None:
        """Calculate the range between high and low estimates."""
        if self.revenueHigh is not None and self.revenueLow is not None:
            return self.revenueHigh - self.revenueLow
        return None


class RevenueEstimates(BaseModel):
    """Revenue estimates response."""

    data: list[RevenueEstimateInfo] = Field(description="List of revenue estimates")
    freq: str | None = Field(default=None, description="Frequency (annual/quarterly)")
    symbol: str = Field(description="Stock symbol")

    @field_validator("freq")
    @classmethod
    def validate_freq(cls, v: str | None) -> str | None:
        """Validate frequency."""
        if v is not None and v not in {"annual", "quarterly"}:
            raise ValueError(f"freq must be 'annual' or 'quarterly', got: {v}")
        return v


class EbitdaEstimateInfo(BaseModel):
    """Individual EBITDA estimate data point."""

    ebitdaAvg: float | None = Field(default=None, description="Average EBITDA estimate")  # noqa: N815
    ebitdaHigh: float | None = Field(default=None, description="Highest EBITDA estimate")  # noqa: N815
    ebitdaLow: float | None = Field(default=None, description="Lowest EBITDA estimate")  # noqa: N815
    numberAnalysts: int | None = Field(default=None, ge=0, description="Number of analysts")  # noqa: N815
    period: str | None = Field(default=None, description="Period (YYYY-MM-DD)")
    year: int | None = Field(default=None, description="Fiscal year")
    quarter: int | None = Field(default=None, ge=0, le=4, description="Fiscal quarter (1-4)")

    @property
    def is_annual(self) -> bool:
        """Check if this is an annual estimate."""
        return self.quarter is None or self.quarter == 0

    @property
    def estimate_range(self) -> float | None:
        """Calculate the range between high and low estimates."""
        if self.ebitdaHigh is not None and self.ebitdaLow is not None:
            return self.ebitdaHigh - self.ebitdaLow
        return None


class EbitdaEstimates(BaseModel):
    """EBITDA estimates response."""

    data: list[EbitdaEstimateInfo] = Field(description="List of EBITDA estimates")
    freq: str | None = Field(default=None, description="Frequency (annual/quarterly)")
    symbol: str = Field(description="Stock symbol")

    @field_validator("freq")
    @classmethod
    def validate_freq(cls, v: str | None) -> str | None:
        """Validate frequency."""
        if v is not None and v not in {"annual", "quarterly"}:
            raise ValueError(f"freq must be 'annual' or 'quarterly', got: {v}")
        return v


class PriceTarget(BaseModel):
    """Price target consensus data."""

    symbol: str = Field(description="Stock symbol")
    targetHigh: float | None = Field(default=None, description="Highest analyst target price")  # noqa: N815
    targetLow: float | None = Field(default=None, description="Lowest analyst target price")  # noqa: N815
    targetMean: float | None = Field(default=None, description="Mean analyst target price")  # noqa: N815
    targetMedian: float | None = Field(default=None, description="Median analyst target price")  # noqa: N815
    numberAnalysts: int | None = Field(default=None, ge=0, description="Number of analysts")  # noqa: N815
    lastUpdated: str | None = Field(default=None, description="Last updated timestamp")  # noqa: N815

    @property
    def target_range(self) -> float | None:
        """Calculate the range between high and low targets."""
        if self.targetHigh is not None and self.targetLow is not None:
            return self.targetHigh - self.targetLow
        return None

    @property
    def upside_from_mean(self) -> float | None:
        """Calculate potential upside/downside from mean target (requires current price)."""
        # This would require current price to calculate, so we just return the mean target
        return self.targetMean


class RecommendationTrend(BaseModel):
    """Analyst recommendation trend data for a specific period."""

    symbol: str = Field(description="Stock symbol")
    buy: int | None = Field(default=None, ge=0, description="Number of buy recommendations")
    hold: int | None = Field(default=None, ge=0, description="Number of hold recommendations")
    sell: int | None = Field(default=None, ge=0, description="Number of sell recommendations")
    strongBuy: int | None = Field(  # noqa: N815
        default=None, ge=0, description="Number of strong buy recommendations"
    )
    strongSell: int | None = Field(  # noqa: N815
        default=None, ge=0, description="Number of strong sell recommendations"
    )
    period: str | None = Field(default=None, description="Period (YYYY-MM-DD)")

    @property
    def total_recommendations(self) -> int:
        """Calculate total number of recommendations."""
        return sum(
            filter(
                None,
                [
                    self.buy or 0,
                    self.hold or 0,
                    self.sell or 0,
                    self.strongBuy or 0,
                    self.strongSell or 0,
                ],
            )
        )

    @property
    def bullish_ratio(self) -> float | None:
        """Calculate ratio of bullish (buy + strong buy) to total recommendations."""
        total = self.total_recommendations
        if total == 0:
            return None
        bullish = (self.buy or 0) + (self.strongBuy or 0)
        return bullish / total

    @property
    def bearish_ratio(self) -> float | None:
        """Calculate ratio of bearish (sell + strong sell) to total recommendations."""
        total = self.total_recommendations
        if total == 0:
            return None
        bearish = (self.sell or 0) + (self.strongSell or 0)
        return bearish / total
