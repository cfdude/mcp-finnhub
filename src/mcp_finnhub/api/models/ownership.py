"""Pydantic models for Finnhub stock ownership data."""

from pydantic import BaseModel, Field


class InsiderTransactionData(BaseModel):
    """Individual insider transaction."""

    name: str | None = Field(default=None, description="Insider name")
    share: int | None = Field(default=None, description="Shares held after transaction")
    change: int | None = Field(default=None, description="Change in shares")
    filingDate: str | None = Field(default=None, description="Filing date")  # noqa: N815
    transactionDate: str | None = Field(default=None, description="Transaction date")  # noqa: N815
    transactionCode: str | None = Field(
        default=None, description="Transaction code (S, M, P, etc.)"
    )  # noqa: N815
    transactionPrice: float | None = Field(default=None, description="Transaction price")  # noqa: N815

    @property
    def is_purchase(self) -> bool:
        """Check if transaction is a purchase."""
        return self.change is not None and self.change > 0

    @property
    def is_sale(self) -> bool:
        """Check if transaction is a sale."""
        return self.change is not None and self.change < 0

    @property
    def transaction_value(self) -> float | None:
        """Calculate transaction value."""
        if self.change is not None and self.transactionPrice is not None:
            return abs(self.change) * self.transactionPrice
        return None


class InsiderTransactions(BaseModel):
    """Insider transactions response."""

    data: list[InsiderTransactionData] = Field(description="List of insider transactions")
    symbol: str = Field(description="Stock symbol")


class InstitutionalOwnershipPosition(BaseModel):
    """Individual institutional position."""

    change: int | None = Field(default=None, description="Change in shares")
    cik: str | None = Field(default=None, description="Institution CIK")
    name: str | None = Field(default=None, description="Institution name")
    noVoting: int | None = Field(default=None, ge=0, description="Shares with no voting rights")  # noqa: N815
    percentage: float | None = Field(default=None, ge=0, le=100, description="Ownership percentage")
    putCall: str | None = Field(default=None, description="Put/Call indicator")  # noqa: N815
    share: int | None = Field(default=None, ge=0, description="Number of shares held")
    sharedVoting: int | None = Field(default=None, ge=0, description="Shares with shared voting")  # noqa: N815
    soleVoting: int | None = Field(default=None, ge=0, description="Shares with sole voting")  # noqa: N815
    value: int | None = Field(default=None, ge=0, description="Position value in USD")

    @property
    def total_voting_shares(self) -> int:
        """Calculate total voting shares."""
        return (self.sharedVoting or 0) + (self.soleVoting or 0)


class InstitutionalOwnershipData(BaseModel):
    """Institutional ownership data for a specific report date."""

    ownership: list[InstitutionalOwnershipPosition] = Field(description="List of positions")
    reportDate: str | None = Field(default=None, description="Report date")  # noqa: N815


class InstitutionalOwnership(BaseModel):
    """Institutional ownership response."""

    cusip: str | None = Field(default=None, description="CUSIP identifier")
    data: list[InstitutionalOwnershipData] = Field(description="Ownership data by report date")
    symbol: str = Field(description="Stock symbol")


class PortfolioHolding(BaseModel):
    """Individual holding in institutional portfolio."""

    change: int | None = Field(default=None, description="Change in shares")
    name: str | None = Field(default=None, description="Company name")
    noVoting: int | None = Field(default=None, ge=0, description="Shares with no voting rights")  # noqa: N815
    percentage: float | None = Field(default=None, ge=0, le=100, description="Portfolio percentage")
    putCall: str | None = Field(default=None, description="Put/Call indicator")  # noqa: N815
    share: int | None = Field(default=None, ge=0, description="Number of shares held")
    sharedVoting: int | None = Field(default=None, ge=0, description="Shares with shared voting")  # noqa: N815
    soleVoting: int | None = Field(default=None, ge=0, description="Shares with sole voting")  # noqa: N815
    symbol: str | None = Field(default=None, description="Stock symbol")
    value: int | None = Field(default=None, ge=0, description="Position value in USD")


class PortfolioData(BaseModel):
    """Portfolio data for a specific filing date."""

    filingDate: str | None = Field(default=None, description="Filing date")  # noqa: N815
    portfolio: list[PortfolioHolding] = Field(description="List of holdings")
    reportDate: str | None = Field(default=None, description="Report date")  # noqa: N815


class InstitutionalPortfolio(BaseModel):
    """Institutional portfolio response."""

    cik: str = Field(description="Institution CIK")
    data: list[PortfolioData] = Field(description="Portfolio data by filing date")
    name: str | None = Field(default=None, description="Institution name")


class CongressionalTrade(BaseModel):
    """Individual congressional trade."""

    amountFrom: int | None = Field(default=None, ge=0, description="Trade amount range from")  # noqa: N815
    amountTo: int | None = Field(default=None, ge=0, description="Trade amount range to")  # noqa: N815
    assetName: str | None = Field(default=None, description="Asset name")  # noqa: N815
    filingDate: str | None = Field(default=None, description="Filing date")  # noqa: N815
    name: str | None = Field(default=None, description="Congress member name")
    ownerType: str | None = Field(default=None, description="Owner type (Self, Spouse, etc.)")  # noqa: N815
    position: str | None = Field(default=None, description="Position (senator, representative)")
    symbol: str | None = Field(default=None, description="Stock symbol")
    transactionDate: str | None = Field(default=None, description="Transaction date")  # noqa: N815
    transactionType: str | None = Field(
        default=None, description="Transaction type (Purchase, Sale)"
    )  # noqa: N815

    @property
    def is_purchase(self) -> bool:
        """Check if trade is a purchase."""
        return self.transactionType == "Purchase"

    @property
    def is_sale(self) -> bool:
        """Check if trade is a sale."""
        return self.transactionType == "Sale"

    @property
    def estimated_value(self) -> float | None:
        """Estimate transaction value (midpoint of range)."""
        if self.amountFrom is not None and self.amountTo is not None:
            return (self.amountFrom + self.amountTo) / 2
        return None


class CongressionalTrading(BaseModel):
    """Congressional trading response."""

    data: list[CongressionalTrade] = Field(description="List of congressional trades")
    symbol: str = Field(description="Stock symbol")
