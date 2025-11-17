"""Pydantic models for Finnhub alternative data."""

from pydantic import BaseModel, Field


class ESGScore(BaseModel):
    """ESG scores for a company."""

    symbol: str = Field(description="Stock symbol")
    totalESG: float | None = Field(default=None, description="Total ESG score")  # noqa: N815
    environmentScore: float | None = Field(default=None, description="Environmental score")  # noqa: N815
    socialScore: float | None = Field(default=None, description="Social score")  # noqa: N815
    governanceScore: float | None = Field(default=None, description="Governance score")  # noqa: N815


class SocialSentimentData(BaseModel):
    """Social sentiment data for a period."""

    atTime: str | None = Field(default=None, description="Timestamp")  # noqa: N815
    mention: int | None = Field(default=None, ge=0, description="Number of mentions")
    positiveScore: float | None = Field(default=None, description="Positive sentiment score")  # noqa: N815
    negativeScore: float | None = Field(default=None, description="Negative sentiment score")  # noqa: N815
    score: float | None = Field(default=None, description="Overall sentiment score")


class SocialSentiment(BaseModel):
    """Social sentiment response."""

    symbol: str = Field(description="Stock symbol")
    data: list[SocialSentimentData] = Field(description="Sentiment data by period")


class SupplyChainRelationship(BaseModel):
    """Supply chain relationship."""

    symbol: str | None = Field(default=None, description="Related company symbol")
    name: str | None = Field(default=None, description="Related company name")
    country: str | None = Field(default=None, description="Country")


class SupplyChain(BaseModel):
    """Supply chain data."""

    symbol: str = Field(description="Stock symbol")
    data: list[SupplyChainRelationship] = Field(description="Supply chain relationships")


class PatentData(BaseModel):
    """USPTO patent data."""

    applicationNumber: str | None = Field(default=None, description="Application number")  # noqa: N815
    filingDate: str | None = Field(default=None, description="Filing date")  # noqa: N815
    patentNumber: str | None = Field(default=None, description="Patent number")  # noqa: N815
    publicationDate: str | None = Field(default=None, description="Publication date")  # noqa: N815
    title: str | None = Field(default=None, description="Patent title")
    url: str | None = Field(default=None, description="Patent URL")


class Patents(BaseModel):
    """Patents response."""

    symbol: str = Field(description="Stock symbol")
    data: list[PatentData] = Field(description="Patent data")
