"""Pydantic models for market events."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarketHoliday(BaseModel):
    """Market holiday information."""

    data: list[dict[str, Any]] | None = Field(default=None, description="Holiday data")
    exchange: str | None = Field(default=None, description="Exchange")
    timezone: str | None = Field(default=None, description="Timezone")


class UpgradeDowngrade(BaseModel):
    """Analyst upgrade/downgrade event."""

    action: str | None = Field(
        default=None, description="Action (upgrade/downgrade/init/reiterate)"
    )
    company: str | None = Field(default=None, description="Analyst firm")
    fromGrade: str | None = Field(default=None, description="From grade")  # noqa: N815
    toGrade: str | None = Field(default=None, description="To grade")  # noqa: N815
    gradeTime: int | None = Field(default=None, description="Unix timestamp")  # noqa: N815
    symbol: str | None = Field(default=None, description="Stock symbol")


class MergerAcquisition(BaseModel):
    """Merger & acquisition event."""

    acquirer: str | None = Field(default=None, description="Acquirer company")
    acquirerSymbol: str | None = Field(default=None, description="Acquirer symbol")  # noqa: N815
    announcementDate: str | None = Field(default=None, description="Announcement date")  # noqa: N815
    dealValue: float | None = Field(default=None, description="Deal value")  # noqa: N815
    paymentMethod: str | None = Field(default=None, description="Payment method")  # noqa: N815
    target: str | None = Field(default=None, description="Target company")
    targetSymbol: str | None = Field(default=None, description="Target symbol")  # noqa: N815
