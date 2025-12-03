"""Pydantic models for technical analysis API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class IndicatorValue(BaseModel):
    """Single indicator value with timestamp."""

    t: int = Field(description="Unix timestamp")
    v: float = Field(description="Indicator value")

    @field_validator("t")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Validate timestamp is reasonable."""
        if v < 946684800:  # 2000-01-01
            raise ValueError("Timestamp must be after year 2000")
        return v

    @property
    def timestamp_dt(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.t)


class IndicatorResponse(BaseModel):
    """Technical indicator response."""

    symbol: str = Field(description="Stock symbol")
    indicator: str = Field(description="Indicator name")
    resolution: str = Field(description="Time resolution")
    data: list[IndicatorValue] = Field(description="Indicator values with timestamps")

    @property
    def values(self) -> list[float]:
        """Get just the indicator values."""
        return [item.v for item in self.data]

    @property
    def timestamps(self) -> list[int]:
        """Get just the timestamps."""
        return [item.t for item in self.data]

    @property
    def timestamps_dt(self) -> list[datetime]:
        """Get timestamps as datetime objects."""
        return [item.timestamp_dt for item in self.data]


class SignalCount(BaseModel):
    """Signal count breakdown."""

    buy: int = Field(description="Number of buy signals")
    neutral: int = Field(description="Number of neutral signals")
    sell: int = Field(description="Number of sell signals")


class TechnicalAnalysis(BaseModel):
    """Technical analysis summary."""

    count: SignalCount = Field(description="Signal count breakdown")
    signal: str = Field(description="Overall signal: buy, sell, neutral")

    @field_validator("signal")
    @classmethod
    def validate_signal(cls, v: str) -> str:
        """Validate signal value."""
        valid_signals = {"buy", "sell", "neutral"}
        if v.lower() not in valid_signals:
            raise ValueError(f"Signal must be one of {valid_signals}")
        return v.lower()


class TrendInfo(BaseModel):
    """Trend information."""

    adx: float = Field(description="Average Directional Index")
    trending: bool = Field(description="Whether the stock is trending")


class AggregateSignalsResponse(BaseModel):
    """Aggregated technical indicator signals."""

    # Note: Finnhub API does not return symbol in this response
    symbol: str | None = Field(default=None, description="Stock symbol (injected from request)")
    technicalAnalysis: TechnicalAnalysis = Field(  # noqa: N815
        description="Technical analysis summary"
    )
    trend: TrendInfo = Field(description="Trend information")

    @property
    def overall_signal(self) -> str:
        """Get overall signal."""
        return self.technicalAnalysis.signal

    @property
    def is_trending(self) -> bool:
        """Check if stock is trending."""
        return self.trend.trending


class Pattern(BaseModel):
    """Chart pattern detection result."""

    patternName: str = Field(description="Pattern name")  # noqa: N815
    patternType: str = Field(description="Pattern type")  # noqa: N815
    mature: bool = Field(description="Whether pattern is mature")
    entryPoint: float | None = Field(default=None, description="Entry point price")  # noqa: N815
    target: float | None = Field(default=None, description="Target price")
    stopLoss: float | None = Field(default=None, description="Stop loss price")  # noqa: N815


class PatternRecognitionResponse(BaseModel):
    """Pattern recognition response."""

    symbol: str = Field(description="Stock symbol")
    resolution: str = Field(description="Time resolution")
    patterns: list[Pattern] = Field(description="Detected patterns")

    @property
    def mature_patterns(self) -> list[Pattern]:
        """Get only mature patterns."""
        return [p for p in self.patterns if p.mature]

    @property
    def pattern_count(self) -> int:
        """Get count of detected patterns."""
        return len(self.patterns)


class SupportResistanceLevel(BaseModel):
    """Support or resistance level."""

    level: float = Field(description="Price level")
    type: str = Field(description="Level type: support or resistance")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate level type."""
        valid_types = {"support", "resistance"}
        if v.lower() not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v.lower()


class SupportResistanceResponse(BaseModel):
    """Support and resistance levels response."""

    symbol: str = Field(description="Stock symbol")
    resolution: str = Field(description="Time resolution")
    levels: list[SupportResistanceLevel] = Field(description="Support/resistance levels")

    @property
    def support_levels(self) -> list[float]:
        """Get support levels."""
        return [lvl.level for lvl in self.levels if lvl.type == "support"]

    @property
    def resistance_levels(self) -> list[float]:
        """Get resistance levels."""
        return [lvl.level for lvl in self.levels if lvl.type == "resistance"]
