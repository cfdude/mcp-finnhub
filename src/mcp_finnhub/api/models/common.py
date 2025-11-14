"""Common Pydantic response models for Finnhub API.

Provides type-safe data models for parsing and validating API responses.
Covers the most frequently used endpoints: quotes, candles, news, company profiles.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Resolution(str, Enum):
    """Supported candle resolutions."""

    ONE_MIN = "1"
    FIVE_MIN = "5"
    FIFTEEN_MIN = "15"
    THIRTY_MIN = "30"
    SIXTY_MIN = "60"
    DAY = "D"
    WEEK = "W"
    MONTH = "M"


class QuoteResponse(BaseModel):
    """Real-time quote data for a symbol.

    Attributes:
        c: Current price
        d: Change from previous close
        dp: Percent change from previous close
        h: High price of the day
        l: Low price of the day
        o: Open price of the day
        pc: Previous close price
        t: Timestamp (Unix seconds)
    """

    c: float = Field(description="Current price")
    d: float = Field(description="Change")
    dp: float = Field(description="Percent change")
    h: float = Field(description="High price of the day")
    l: float = Field(description="Low price of the day")  # noqa: E741
    o: float = Field(description="Open price of the day")
    pc: float = Field(description="Previous close price")
    t: int = Field(description="Timestamp (Unix seconds)")

    @field_validator("t")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Validate timestamp is reasonable (after year 2000)."""
        if v < 946684800:  # 2000-01-01
            raise ValueError("Timestamp must be after year 2000")
        return v

    @property
    def timestamp_dt(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.t)


class CandleResponse(BaseModel):
    """Historical candlestick/OHLC data.

    Attributes:
        c: List of close prices
        h: List of high prices
        l: List of low prices
        o: List of open prices
        s: Status (ok or no_data)
        t: List of timestamps (Unix seconds)
        v: List of volumes
    """

    c: list[float] = Field(description="Close prices")
    h: list[float] = Field(description="High prices")
    l: list[float] = Field(description="Low prices")  # noqa: E741
    o: list[float] = Field(description="Open prices")
    s: str = Field(description="Status (ok or no_data)")
    t: list[int] = Field(description="Timestamps (Unix seconds)")
    v: list[int] = Field(description="Volumes")

    @field_validator("s")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is either 'ok' or 'no_data'."""
        if v not in {"ok", "no_data"}:
            raise ValueError("Status must be 'ok' or 'no_data'")
        return v

    @field_validator("c", "h", "l", "o", "t", "v")
    @classmethod
    def validate_lists_same_length(cls, v: list[Any], info) -> list[Any]:
        """Ensure all lists have the same length."""
        # This validator runs on each field, so we just return the value
        # The actual length validation happens in model_validator
        return v

    def model_post_init(self, __context: Any) -> None:
        """Validate all arrays have the same length."""
        if self.s == "ok":
            lengths = {
                len(self.c),
                len(self.h),
                len(self.l),
                len(self.o),
                len(self.t),
                len(self.v),
            }
            if len(lengths) > 1:
                raise ValueError("All candle arrays must have the same length")

    @property
    def timestamps_dt(self) -> list[datetime]:
        """Convert Unix timestamps to datetime objects."""
        return [datetime.fromtimestamp(ts) for ts in self.t]

    def __len__(self) -> int:
        """Return number of candles."""
        return len(self.t)


class NewsArticle(BaseModel):
    """News article from Finnhub.

    Attributes:
        category: News category
        datetime: Publication time (Unix seconds)
        headline: Article headline
        id: Article ID
        image: Thumbnail image URL
        related: Related stock symbols
        source: News source
        summary: Article summary/description
        url: Article URL
    """

    category: str = Field(description="News category")
    datetime: int = Field(description="Publication time (Unix seconds)")
    headline: str = Field(description="Article headline")
    id: int = Field(description="Article ID")
    image: str = Field(description="Thumbnail image URL")
    related: str = Field(description="Related stock symbols (comma-separated)")
    source: str = Field(description="News source")
    summary: str = Field(description="Article summary")
    url: str = Field(description="Article URL")

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, v: int) -> int:
        """Validate datetime is reasonable (after year 2000)."""
        if v < 946684800:  # 2000-01-01
            raise ValueError("Datetime must be after year 2000")
        return v

    @property
    def datetime_dt(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.datetime)

    @property
    def related_symbols(self) -> list[str]:
        """Parse comma-separated related symbols into list."""
        return [s.strip() for s in self.related.split(",") if s.strip()]


class CompanyProfile(BaseModel):
    """Company profile information.

    Attributes:
        country: Country of company headquarters
        currency: Currency used in financial reports
        exchange: Stock exchange
        ipo: IPO date (YYYY-MM-DD)
        marketCapitalization: Market capitalization in millions
        name: Company name
        phone: Company phone number
        shareOutstanding: Number of outstanding shares in millions
        ticker: Stock ticker symbol
        weburl: Company website URL
        logo: Company logo URL
        finnhubIndustry: Finnhub industry classification
    """

    country: str = Field(description="Country of headquarters")
    currency: str = Field(description="Currency code (e.g., USD)")
    exchange: str = Field(description="Stock exchange")
    ipo: str = Field(description="IPO date (YYYY-MM-DD)")
    marketCapitalization: float = Field(description="Market cap in millions")  # noqa: N815
    name: str = Field(description="Company name")
    phone: str = Field(description="Phone number")
    shareOutstanding: float = Field(description="Outstanding shares in millions")  # noqa: N815
    ticker: str = Field(description="Stock ticker symbol")
    weburl: str = Field(description="Company website")
    logo: str = Field(description="Logo URL")
    finnhubIndustry: str = Field(description="Industry classification")  # noqa: N815

    @field_validator("ipo")
    @classmethod
    def validate_ipo_date(cls, v: str) -> str:
        """Validate IPO date format is YYYY-MM-DD."""
        if v and len(v) == 10:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("IPO date must be in YYYY-MM-DD format") from exc
        return v

    @field_validator("marketCapitalization", "shareOutstanding")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Validate financial metrics are positive."""
        if v < 0:
            raise ValueError("Financial metrics must be non-negative")
        return v


class SymbolLookupResult(BaseModel):
    """Symbol search result.

    Attributes:
        description: Company/security name
        displaySymbol: Display symbol with exchange
        symbol: Symbol that can be used in API calls
        type: Security type (Common Stock, ETF, etc.)
    """

    description: str = Field(description="Company/security name")
    displaySymbol: str = Field(description="Display symbol with exchange")  # noqa: N815
    symbol: str = Field(description="API symbol")
    type: str = Field(description="Security type")


class MarketStatusResponse(BaseModel):
    """Market status for an exchange.

    Attributes:
        exchange: Exchange name
        holiday: Holiday name if market is closed
        isOpen: Whether market is currently open
        session: Trading session (pre-market, regular, after-hours, closed)
        timezone: Exchange timezone
        t: Current timestamp (Unix seconds)
    """

    exchange: str = Field(description="Exchange name")
    holiday: str | None = Field(default=None, description="Holiday name if closed")
    isOpen: bool = Field(description="Whether market is open")  # noqa: N815
    session: str = Field(description="Trading session")
    timezone: str = Field(description="Exchange timezone")
    t: int = Field(description="Current timestamp (Unix seconds)")

    @field_validator("session")
    @classmethod
    def validate_session(cls, v: str) -> str:
        """Validate session is a known type."""
        valid_sessions = {"pre-market", "regular", "after-hours", "closed"}
        if v not in valid_sessions:
            raise ValueError(f"Session must be one of: {', '.join(valid_sessions)}")
        return v


__all__ = [
    "CandleResponse",
    "CompanyProfile",
    "MarketStatusResponse",
    "NewsArticle",
    "QuoteResponse",
    "Resolution",
    "SymbolLookupResult",
]
