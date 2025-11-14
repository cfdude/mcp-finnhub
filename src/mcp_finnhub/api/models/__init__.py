"""Pydantic response models for Finnhub API responses."""

from mcp_finnhub.api.models.common import (
    CandleResponse,
    CompanyProfile,
    MarketStatusResponse,
    NewsArticle,
    QuoteResponse,
    Resolution,
    SymbolLookupResult,
)
from mcp_finnhub.api.models.market import (
    EarningsData,
    EarningsResponse,
    FinancialMetric,
    FinancialReport,
    FinancialsResponse,
    SymbolSearchResponse,
)
from mcp_finnhub.api.models.technical import (
    AggregateSignalsResponse,
    IndicatorResponse,
    IndicatorValue,
    Pattern,
    PatternRecognitionResponse,
    SignalCount,
    SupportResistanceLevel,
    SupportResistanceResponse,
    TechnicalAnalysis,
    TrendInfo,
)

__all__ = [
    # Common models
    "CandleResponse",
    "CompanyProfile",
    "MarketStatusResponse",
    "NewsArticle",
    "QuoteResponse",
    "Resolution",
    "SymbolLookupResult",
    # Market data models
    "EarningsData",
    "EarningsResponse",
    "FinancialMetric",
    "FinancialReport",
    "FinancialsResponse",
    "SymbolSearchResponse",
    # Technical analysis models
    "AggregateSignalsResponse",
    "IndicatorResponse",
    "IndicatorValue",
    "Pattern",
    "PatternRecognitionResponse",
    "SignalCount",
    "SupportResistanceLevel",
    "SupportResistanceResponse",
    "TechnicalAnalysis",
    "TrendInfo",
]
