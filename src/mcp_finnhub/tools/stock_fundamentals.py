"""Stock fundamentals MCP tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import fundamentals
from mcp_finnhub.api.models.fundamentals import (
    BasicFinancialsResponse,
    DividendData,
    ReportedFinancialsResponse,
    RevenueBreakdownResponse,
    SecFinancialsResponse,
    SplitData,
)

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class StockFundamentalsTool:
    """Stock fundamentals tool with 6 operations."""

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_basic_financials",
        "get_reported_financials",
        "get_sec_financials",
        "get_dividends",
        "get_splits",
        "get_revenue_breakdown",
    }

    VALID_FREQUENCIES: ClassVar[set[str]] = {"annual", "quarterly"}
    VALID_STATEMENTS: ClassVar[set[str]] = {"bs", "ic", "cf"}
    VALID_METRICS: ClassVar[set[str]] = {
        "all",
        "price",
        "valuation",
        "margin",
        "growth",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize stock fundamentals tool.

        Args:
            client: FinnhubClient instance
        """
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate operation name.

        Args:
            operation: Operation to validate

        Raises:
            ValueError: If operation is invalid
        """
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation: {operation}. "
                f"Valid operations: {', '.join(sorted(self.VALID_OPERATIONS))}"
            )

    def validate_frequency(self, freq: str) -> None:
        """Validate frequency parameter.

        Args:
            freq: Frequency to validate

        Raises:
            ValueError: If frequency is invalid
        """
        if freq not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency: {freq}. "
                f"Valid frequencies: {', '.join(sorted(self.VALID_FREQUENCIES))}"
            )

    def validate_statement(self, statement: str) -> None:
        """Validate statement type.

        Args:
            statement: Statement type to validate

        Raises:
            ValueError: If statement is invalid
        """
        if statement not in self.VALID_STATEMENTS:
            raise ValueError(
                f"Invalid statement: {statement}. "
                f"Valid statements: {', '.join(sorted(self.VALID_STATEMENTS))}"
            )

    def validate_metric(self, metric: str) -> None:
        """Validate metric type.

        Args:
            metric: Metric type to validate

        Raises:
            ValueError: If metric is invalid
        """
        if metric not in self.VALID_METRICS:
            raise ValueError(
                f"Invalid metric: {metric}. Valid metrics: {', '.join(sorted(self.VALID_METRICS))}"
            )

    async def get_basic_financials(
        self,
        symbol: str,
        metric: str = "all",
        include_series: bool = False,
        series_limit: int | None = None,
    ) -> dict[str, Any]:
        """Get basic financial metrics.

        Args:
            symbol: Stock symbol
            metric: Metric type (all, price, valuation, margin, growth)
            include_series: Whether to include historical series data (default: False).
                           Series data can be very large (100K+ tokens) and may exceed
                           context limits. Set to True only when historical trends needed.
            series_limit: Maximum number of periods to include per metric in series
                         (e.g., 4 = last 4 quarters/years). Only applies when
                         include_series=True. Default: None (all periods).

        Returns:
            Basic financial metrics. By default returns only current 'metric' values.
            With include_series=True, also includes historical 'series' data.
        """
        self.validate_metric(metric)

        response = await fundamentals.get_basic_financials(
            self.client,
            symbol,
            metric,
        )

        # Validate with Pydantic model
        model = BasicFinancialsResponse(**response)
        result = model.model_dump()

        # Handle series exclusion/limiting for context window management
        if not include_series:
            # Remove series to keep response small (default behavior)
            result.pop("series", None)
        elif series_limit is not None and result.get("series"):
            # Limit the number of periods in each series metric
            result["series"] = self._limit_series_periods(result["series"], series_limit)

        return result

    def _limit_series_periods(self, series: dict[str, Any], limit: int) -> dict[str, Any]:
        """Limit the number of periods in series data.

        Args:
            series: Series data with annual/quarterly nested dicts
            limit: Maximum periods per metric

        Returns:
            Series with limited periods
        """
        limited = {}
        for period_type, metrics in series.items():
            if isinstance(metrics, dict):
                limited[period_type] = {}
                for metric_name, values in metrics.items():
                    if isinstance(values, list):
                        # Take only the most recent N periods
                        limited[period_type][metric_name] = values[:limit]
                    else:
                        limited[period_type][metric_name] = values
            else:
                limited[period_type] = metrics
        return limited

    async def get_reported_financials(
        self,
        symbol: str,
        freq: str = "annual",
    ) -> dict[str, Any]:
        """Get reported financials as filed with SEC.

        Args:
            symbol: Stock symbol
            freq: Frequency (annual or quarterly)

        Returns:
            Reported financial statements
        """
        self.validate_frequency(freq)

        response = await fundamentals.get_reported_financials(
            self.client,
            symbol,
            freq,
        )

        # Validate with Pydantic model
        model = ReportedFinancialsResponse(**response)
        return model.model_dump()

    async def get_sec_financials(
        self,
        symbol: str,
        statement: str,
        freq: str = "annual",
    ) -> dict[str, Any]:
        """Get SEC-standardized financial statements.

        Args:
            symbol: Stock symbol
            statement: Statement type (bs=balance sheet, ic=income, cf=cash flow)
            freq: Frequency (annual or quarterly)

        Returns:
            SEC-standardized financial data
        """
        self.validate_statement(statement)
        self.validate_frequency(freq)

        response = await fundamentals.get_sec_financials(
            self.client,
            symbol,
            statement,
            freq,
        )

        # Validate with Pydantic model
        model = SecFinancialsResponse(**response)
        return model.model_dump()

    async def get_dividends(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, Any]]:
        """Get dividend payment history.

        Args:
            symbol: Stock symbol
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)

        Returns:
            List of dividend payments
        """
        response = await fundamentals.get_dividends(
            self.client,
            symbol,
            from_date,
            to_date,
        )

        # Validate each dividend with Pydantic model
        dividends = [DividendData(**div) for div in response]
        return [div.model_dump() for div in dividends]

    async def get_splits(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, Any]]:
        """Get stock split history.

        Args:
            symbol: Stock symbol
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)

        Returns:
            List of stock splits
        """
        response = await fundamentals.get_splits(
            self.client,
            symbol,
            from_date,
            to_date,
        )

        # Validate each split with Pydantic model
        splits = [SplitData(**split) for split in response]
        return [split.model_dump() for split in splits]

    async def get_revenue_breakdown(
        self,
        symbol: str,
        cik: str | None = None,
    ) -> dict[str, Any]:
        """Get revenue breakdown by product/geography.

        Args:
            symbol: Stock symbol
            cik: Optional CIK number

        Returns:
            Revenue breakdown data
        """
        response = await fundamentals.get_revenue_breakdown(
            self.client,
            symbol,
            cik,
        )

        # Validate with Pydantic model
        model = RevenueBreakdownResponse(**response)
        return model.model_dump()

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a fundamentals operation.

        Args:
            operation: Operation name
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid
        """
        self.validate_operation(operation)

        # Route to operation handler
        if operation == "get_basic_financials":
            return await self.get_basic_financials(**params)
        elif operation == "get_reported_financials":
            return await self.get_reported_financials(**params)
        elif operation == "get_sec_financials":
            return await self.get_sec_financials(**params)
        elif operation == "get_dividends":
            return await self.get_dividends(**params)
        elif operation == "get_splits":
            return await self.get_splits(**params)
        elif operation == "get_revenue_breakdown":
            return await self.get_revenue_breakdown(**params)
        else:
            # Should never reach here due to validation
            raise ValueError(f"Unknown operation: {operation}")
