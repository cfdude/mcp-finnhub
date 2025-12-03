"""Pydantic models for calendar data."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IPOEvent(BaseModel):
    """IPO event information."""

    date: str | None = Field(default=None, description="IPO date")
    exchange: str | None = Field(default=None, description="Exchange")
    name: str | None = Field(default=None, description="Company name")
    numberOfShares: int | None = Field(default=None, ge=0, description="Number of shares")  # noqa: N815
    price: str | None = Field(default=None, description="Price range")
    status: str | None = Field(default=None, description="Status")
    symbol: str | None = Field(default=None, description="Stock symbol")
    totalSharesValue: int | None = Field(default=None, ge=0, description="Total shares value")  # noqa: N815


class IPOCalendar(BaseModel):
    """IPO calendar response."""

    ipoCalendar: list[IPOEvent] | None = Field(default=None, description="IPO events")  # noqa: N815


class EarningsEvent(BaseModel):
    """Earnings event information."""

    date: str | None = Field(default=None, description="Earnings date")
    epsActual: float | None = Field(default=None, description="Actual EPS")  # noqa: N815
    epsEstimate: float | None = Field(default=None, description="Estimated EPS")  # noqa: N815
    hour: str | None = Field(default=None, description="Time of day")
    quarter: int | None = Field(default=None, ge=1, le=4, description="Quarter")
    revenueActual: float | None = Field(default=None, description="Actual revenue")  # noqa: N815
    revenueEstimate: float | None = Field(default=None, description="Estimated revenue")  # noqa: N815
    symbol: str | None = Field(default=None, description="Stock symbol")
    year: int | None = Field(default=None, description="Year")


class EarningsCalendar(BaseModel):
    """Earnings calendar response."""

    earningsCalendar: list[EarningsEvent] | None = Field(  # noqa: N815
        default=None, description="Earnings events"
    )


class EconomicEvent(BaseModel):
    """Economic event information."""

    actual: float | None = Field(default=None, description="Actual value")
    estimate: float | None = Field(default=None, description="Estimated value")
    country: str | None = Field(default=None, description="Country")
    event: str | None = Field(default=None, description="Event name")
    impact: str | None = Field(default=None, description="Impact level")
    prev: float | None = Field(default=None, description="Previous value")
    time: str | None = Field(default=None, description="Event time")


class EconomicCalendar(BaseModel):
    """Economic calendar response."""

    economicCalendar: list[EconomicEvent] | None = Field(  # noqa: N815
        default=None, description="Economic events"
    )


class FDAEvent(BaseModel):
    """FDA committee meeting event."""

    fromDate: str | None = Field(default=None, description="Start date")  # noqa: N815
    toDate: str | None = Field(default=None, description="End date")  # noqa: N815
    eventDescription: str | None = Field(default=None, description="Event description")  # noqa: N815
    url: str | None = Field(default=None, description="Event URL")
