"""Pydantic models for Finnhub SEC filings data."""

from typing import Any

from pydantic import BaseModel, Field


class FilingData(BaseModel):
    """SEC filing data."""

    accessNumber: str | None = Field(default=None, description="SEC access number")  # noqa: N815
    symbol: str | None = Field(default=None, description="Stock symbol")
    cik: str | None = Field(default=None, description="CIK number")
    form: str | None = Field(default=None, description="Form type (10-K, 10-Q, etc.)")
    filedDate: str | None = Field(default=None, description="Filing date")  # noqa: N815
    acceptedDate: str | None = Field(default=None, description="Accepted date")  # noqa: N815
    reportUrl: str | None = Field(default=None, description="Report URL")  # noqa: N815
    filingUrl: str | None = Field(default=None, description="Filing URL")  # noqa: N815


class FilingSentiment(BaseModel):
    """SEC filing sentiment analysis."""

    accessNumber: str | None = Field(default=None, description="SEC access number")  # noqa: N815
    symbol: str | None = Field(default=None, description="Stock symbol")
    cik: str | None = Field(default=None, description="CIK number")
    sentiment: dict[str, float] | None = Field(default=None, description="Sentiment scores")
    positiveWord: int | None = Field(default=None, ge=0, description="Positive word count")  # noqa: N815
    negativeWord: int | None = Field(default=None, ge=0, description="Negative word count")  # noqa: N815


class SimilarityIndex(BaseModel):
    """Filing similarity index data."""

    symbol: str = Field(description="Stock symbol")
    cik: str | None = Field(default=None, description="CIK number")
    similarity: list[dict[str, Any]] | None = Field(default=None, description="Similarity scores")


# Import Any for type hints
