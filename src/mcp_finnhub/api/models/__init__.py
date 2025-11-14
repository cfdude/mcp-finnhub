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
from mcp_finnhub.api.models.fundamentals import (
    BasicFinancials,
    BasicFinancialsResponse,
    DividendData,
    ReportedFinancial,
    ReportedFinancialsResponse,
    RevenueBreakdownData,
    RevenueBreakdownResponse,
    RevenueGeography,
    RevenueProduct,
    SecFinancialData,
    SecFinancialsResponse,
    SplitData,
)
from mcp_finnhub.api.models.market import (
    EarningsData,
    EarningsResponse,
    FinancialMetric,
    FinancialReport,
    FinancialsResponse,
    SymbolSearchResponse,
)
from mcp_finnhub.api.models.news import (
    InsiderSentimentResponse,
    InsiderTransaction,
    NewsSentimentResponse,
    SentimentBuzz,
    SentimentScore,
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
    # Technical analysis models
    "AggregateSignalsResponse",
    # Fundamentals models
    "BasicFinancials",
    "BasicFinancialsResponse",
    # Common models
    "CandleResponse",
    "CompanyProfile",
    "DividendData",
    # Market data models
    "EarningsData",
    "EarningsResponse",
    "FinancialMetric",
    "FinancialReport",
    "FinancialsResponse",
    "IndicatorResponse",
    "IndicatorValue",
    # News and sentiment models
    "InsiderSentimentResponse",
    "InsiderTransaction",
    "MarketStatusResponse",
    "NewsArticle",
    "NewsSentimentResponse",
    "Pattern",
    "PatternRecognitionResponse",
    "QuoteResponse",
    "ReportedFinancial",
    "ReportedFinancialsResponse",
    "Resolution",
    "RevenueBreakdownData",
    "RevenueBreakdownResponse",
    "RevenueGeography",
    "RevenueProduct",
    "SecFinancialData",
    "SecFinancialsResponse",
    "SentimentBuzz",
    "SentimentScore",
    "SignalCount",
    "SplitData",
    "SupportResistanceLevel",
    "SupportResistanceResponse",
    "SymbolLookupResult",
    "SymbolSearchResponse",
    "TechnicalAnalysis",
    "TrendInfo",
]
