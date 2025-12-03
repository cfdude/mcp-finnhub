"""Pydantic models for news and sentiment API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SentimentScore(BaseModel):
    """Sentiment score statistics."""

    bearishPercent: float = Field(description="Percentage of bearish articles")  # noqa: N815
    bullishPercent: float = Field(description="Percentage of bullish articles")  # noqa: N815

    @property
    def is_bullish(self) -> bool:
        """Check if overall sentiment is bullish."""
        return self.bullishPercent > self.bearishPercent

    @property
    def sentiment_spread(self) -> float:
        """Calculate sentiment spread (bullish - bearish)."""
        return self.bullishPercent - self.bearishPercent


class SentimentBuzz(BaseModel):
    """Article volume and sentiment buzz metrics."""

    articlesInLastWeek: int = Field(description="Articles in last week")  # noqa: N815
    weeklyAverage: float = Field(description="Weekly average article count")  # noqa: N815
    buzz: float = Field(description="Relative buzz (current/average)")

    @property
    def is_high_buzz(self) -> bool:
        """Check if buzz is above average."""
        return self.buzz > 1.0


class NewsSentimentResponse(BaseModel):
    """News sentiment analysis response."""

    symbol: str = Field(description="Stock symbol")
    companyNewsScore: float = Field(  # noqa: N815
        description="Company news sentiment score"
    )
    sectorAverageBullishPercent: float = Field(  # noqa: N815
        description="Sector average bullish percentage"
    )
    sectorAverageNewsScore: float = Field(  # noqa: N815
        description="Sector average news score"
    )
    sentiment: SentimentScore = Field(description="Sentiment statistics")
    buzz: SentimentBuzz = Field(description="Buzz metrics")

    @field_validator("companyNewsScore", "sectorAverageNewsScore")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        """Validate score is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Score must be between 0 and 1")
        return v

    @property
    def outperforms_sector(self) -> bool:
        """Check if company outperforms sector sentiment."""
        return self.companyNewsScore > self.sectorAverageNewsScore


class InsiderTransaction(BaseModel):
    """Insider sentiment for a single month."""

    year: int = Field(description="Year")
    month: int = Field(description="Month (1-12)")
    change: int = Field(description="Net change in shares")
    mspr: float = Field(description="MSPR (Month since positive return)")

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        """Validate month is 1-12."""
        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate year is reasonable."""
        if v < 1900 or v > 2100:
            raise ValueError("Year must be between 1900 and 2100")
        return v

    @property
    def is_buying(self) -> bool:
        """Check if insiders are net buying."""
        return self.change > 0

    @property
    def is_selling(self) -> bool:
        """Check if insiders are net selling."""
        return self.change < 0


class InsiderSentimentResponse(BaseModel):
    """Insider trading sentiment response."""

    symbol: str = Field(description="Stock symbol")
    data: list[InsiderTransaction] = Field(description="Monthly insider transactions")

    @property
    def latest_month(self) -> InsiderTransaction | None:
        """Get most recent month's data."""
        return self.data[0] if self.data else None

    @property
    def net_buying_months(self) -> int:
        """Count months with net buying."""
        return sum(1 for t in self.data if t.is_buying)

    @property
    def net_selling_months(self) -> int:
        """Count months with net selling."""
        return sum(1 for t in self.data if t.is_selling)

    @property
    def overall_sentiment(self) -> str:
        """Get overall insider sentiment."""
        if self.net_buying_months > self.net_selling_months:
            return "bullish"
        elif self.net_selling_months > self.net_buying_months:
            return "bearish"
        return "neutral"


__all__ = [
    "InsiderSentimentResponse",
    "InsiderTransaction",
    "NewsSentimentResponse",
    "SentimentBuzz",
    "SentimentScore",
]
