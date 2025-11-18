"""Pydantic response models for Finnhub API responses."""

from mcp_finnhub.api.models.alternative import (
    ESGScore,
    PatentData,
    Patents,
    SocialSentiment,
    SocialSentimentData,
    SupplyChain,
    SupplyChainRelationship,
)
from mcp_finnhub.api.models.calendar import (
    EarningsCalendar,
    EarningsEvent,
    EconomicCalendar,
    EconomicEvent,
    FDAEvent,
    IPOCalendar,
    IPOEvent,
)
from mcp_finnhub.api.models.common import (
    CandleResponse,
    CompanyProfile,
    MarketStatusResponse,
    NewsArticle,
    QuoteResponse,
    Resolution,
    SymbolLookupResult,
)
from mcp_finnhub.api.models.crypto import (
    CryptoCandleResponse,
    CryptoProfile,
    CryptoSymbol,
)
from mcp_finnhub.api.models.estimates import (
    EarningsEstimateInfo,
    EarningsEstimates,
    EbitdaEstimateInfo,
    EbitdaEstimates,
    PriceTarget,
    RecommendationTrend,
    RevenueEstimateInfo,
    RevenueEstimates,
)
from mcp_finnhub.api.models.events import (
    MarketHoliday,
    MergerAcquisition,
    UpgradeDowngrade,
)
from mcp_finnhub.api.models.filings import (
    FilingData,
    FilingSentiment,
    SimilarityIndex,
)
from mcp_finnhub.api.models.forex import (
    ForexCandleResponse,
    ForexRate,
    ForexSymbol,
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
from mcp_finnhub.api.models.ownership import (
    CongressionalTrade,
    CongressionalTrading,
    InsiderTransactionData,
    InsiderTransactions,
    InstitutionalOwnership,
    InstitutionalOwnershipData,
    InstitutionalOwnershipPosition,
    InstitutionalPortfolio,
    PortfolioData,
    PortfolioHolding,
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
    # Ownership models
    "CongressionalTrade",
    "CongressionalTrading",
    # Crypto models
    "CryptoCandleResponse",
    "CryptoProfile",
    "CryptoSymbol",
    "DividendData",
    # Alternative data models
    "ESGScore",
    # Calendar models
    "EarningsCalendar",
    # Market data models
    "EarningsData",
    # Estimates models
    "EarningsEstimateInfo",
    "EarningsEstimates",
    # Calendar models
    "EarningsEvent",
    "EarningsResponse",
    "EbitdaEstimateInfo",
    "EbitdaEstimates",
    # Calendar models
    "EconomicCalendar",
    "EconomicEvent",
    # Calendar models
    "FDAEvent",
    # SEC filings models
    "FilingData",
    "FilingSentiment",
    "FinancialMetric",
    "FinancialReport",
    "FinancialsResponse",
    # Forex models
    "ForexCandleResponse",
    "ForexRate",
    "ForexSymbol",
    # Calendar models
    "IPOCalendar",
    "IPOEvent",
    "IndicatorResponse",
    "IndicatorValue",
    # News and sentiment models
    "InsiderSentimentResponse",
    "InsiderTransaction",
    "InsiderTransactionData",
    "InsiderTransactions",
    "InstitutionalOwnership",
    "InstitutionalOwnershipData",
    "InstitutionalOwnershipPosition",
    "InstitutionalPortfolio",
    # Market events models
    "MarketHoliday",
    "MarketStatusResponse",
    # Market events models
    "MergerAcquisition",
    "NewsArticle",
    "NewsSentimentResponse",
    "PatentData",
    "Patents",
    "Pattern",
    "PatternRecognitionResponse",
    "PortfolioData",
    "PortfolioHolding",
    "PriceTarget",
    "QuoteResponse",
    "RecommendationTrend",
    "ReportedFinancial",
    "ReportedFinancialsResponse",
    "Resolution",
    "RevenueBreakdownData",
    "RevenueBreakdownResponse",
    "RevenueEstimateInfo",
    "RevenueEstimates",
    "RevenueGeography",
    "RevenueProduct",
    "SecFinancialData",
    "SecFinancialsResponse",
    "SentimentBuzz",
    "SentimentScore",
    "SignalCount",
    "SimilarityIndex",
    "SocialSentiment",
    "SocialSentimentData",
    "SplitData",
    "SupplyChain",
    "SupplyChainRelationship",
    "SupportResistanceLevel",
    "SupportResistanceResponse",
    "SymbolLookupResult",
    "SymbolSearchResponse",
    "TechnicalAnalysis",
    "TrendInfo",
    # Market events models
    "UpgradeDowngrade",
]
