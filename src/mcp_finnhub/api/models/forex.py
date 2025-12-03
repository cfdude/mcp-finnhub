"""Pydantic models for foreign exchange (forex) data."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ForexSymbol(BaseModel):
    """Forex symbol information."""

    description: str | None = Field(default=None, description="Symbol description")
    displaySymbol: str | None = Field(default=None, description="Display symbol")  # noqa: N815
    symbol: str | None = Field(default=None, description="Symbol identifier")


class ForexCandleResponse(BaseModel):
    """Forex candle (OHLC) response."""

    c: list[float] | None = Field(default=None, description="Close prices")
    h: list[float] | None = Field(default=None, description="High prices")
    l: list[float] | None = Field(default=None, description="Low prices")  # noqa: E741
    o: list[float] | None = Field(default=None, description="Open prices")
    s: str | None = Field(default=None, description="Status (ok or no_data)")
    t: list[int] | None = Field(default=None, description="Unix timestamps")

    @field_validator("s")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate status field."""
        if v is not None and v not in {"ok", "no_data"}:
            raise ValueError(f"Invalid status: {v}. Must be 'ok' or 'no_data'")
        return v

    @property
    def has_data(self) -> bool:
        """Check if response contains data."""
        return self.s == "ok"

    @property
    def candle_count(self) -> int:
        """Get number of candles."""
        if self.t is None:
            return 0
        return len(self.t)


class ForexRate(BaseModel):
    """Forex exchange rate information."""

    base: str | None = Field(default=None, description="Base currency")
    quote: dict[str, float] | None = Field(default=None, description="Quote currencies and rates")
