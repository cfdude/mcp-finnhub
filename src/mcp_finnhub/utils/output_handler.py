"""Result output handler for smart routing of tool results."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from pathlib import Path

    from mcp_finnhub.config import AppConfig
    from mcp_finnhub.jobs.manager import JobManager
    from mcp_finnhub.utils.file_writer import FileWriter
    from mcp_finnhub.utils.json_to_csv import JSONToCSVConverter
    from mcp_finnhub.utils.path_resolver import PathResolver
    from mcp_finnhub.utils.token_estimator import TokenEstimator


class ResultOutputHandler:
    """Handles smart routing of tool results to screen, file, or background job.

    When tool results exceed the configured token limit, the handler:
    1. Writes the full data to a file in the project's exports directory
    2. Returns a truncated preview with information about where full data was saved
    3. Supports both JSON and CSV export formats
    """

    def __init__(
        self,
        config: AppConfig,
        token_estimator: TokenEstimator,
        csv_converter: JSONToCSVConverter,
        path_resolver: PathResolver,
        file_writer: FileWriter,
        job_manager: JobManager,
    ) -> None:
        """Initialize output handler with dependencies.

        Args:
            config: Application configuration
            token_estimator: Token usage estimator
            csv_converter: JSON to CSV converter
            path_resolver: Storage path resolver
            file_writer: File writing utility
            job_manager: Background job manager
        """
        self.config = config
        self.token_estimator = token_estimator
        self.csv_converter = csv_converter
        self.path_resolver = path_resolver
        self.file_writer = file_writer
        self.job_manager = job_manager

    def route_result(
        self,
        data: dict[str, Any] | list[Any],
        project_name: str | None = None,
        operation_name: str = "export",
        export_format: str = "json",
    ) -> dict[str, Any]:
        """Route result based on size - return directly or save to file.

        Args:
            data: The tool result data (dict or list)
            project_name: Project name for file exports (uses 'default' if None)
            operation_name: Name of the operation (used in filename)
            export_format: Export format ('json' or 'csv')

        Returns:
            The original data if it fits in context, or a dict with:
            - truncated data preview
            - file path where full data was saved
            - metadata about the export
        """
        # Convert data to JSON string for token estimation
        json_str = json.dumps(data, indent=2, default=str)
        token_count = self.token_estimator.estimate_tokens(json_str)
        token_limit = self.config.safe_token_limit

        # If data fits in context, return as-is
        if token_count <= token_limit:
            return data

        # Data exceeds limit - save to file and return truncated preview
        project = project_name or "default"

        # Ensure project directory exists with exports subdirectory
        self.path_resolver.ensure_project_dir(project)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "csv" and isinstance(data, list):
            filename = f"{operation_name}_{timestamp}.csv"
            file_path = self.path_resolver.get_export_path(project, filename)
            self._write_csv(data, file_path)
        else:
            filename = f"{operation_name}_{timestamp}.json"
            file_path = self.path_resolver.get_export_path(project, filename)
            self._write_json(data, file_path)

        # Create truncated preview
        preview = self._create_preview(data, token_limit // 2)

        # Count records
        record_count = len(data) if isinstance(data, list) else 1

        return {
            "status": "truncated",
            "message": f"Data exceeded token limit ({token_count:,} tokens > {token_limit:,} limit). Full data saved to file.",
            "file_path": str(file_path),
            "file_format": export_format,
            "record_count": record_count,
            "token_count": token_count,
            "token_limit": token_limit,
            "preview": preview,
            "hint": f"To access full data, read the file at: {file_path}",
        }

    def _write_json(self, data: Any, file_path: Path) -> None:
        """Write data to JSON file.

        Args:
            data: Data to write
            file_path: Target file path
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_writer.write_json(data, file_path)

    def _write_csv(self, data: list[dict[str, Any]], file_path: Path) -> None:
        """Write data to CSV file.

        Args:
            data: List of dicts to write as CSV
            file_path: Target file path
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_writer.write_csv(data, file_path)

    def _create_preview(
        self,
        data: dict[str, Any] | list[Any],
        max_tokens: int,
    ) -> dict[str, Any] | list[Any]:
        """Create a truncated preview of the data.

        Args:
            data: Original data
            max_tokens: Maximum tokens for preview

        Returns:
            Truncated preview of the data
        """
        if isinstance(data, list):
            # For lists, return first N items that fit
            preview_items = []
            current_tokens = 0

            for item in data:
                item_str = json.dumps(item, default=str)
                item_tokens = self.token_estimator.estimate_tokens(item_str)

                if current_tokens + item_tokens > max_tokens:
                    break

                preview_items.append(item)
                current_tokens += item_tokens

            return preview_items
        else:
            # For dicts, return the full dict but note it's truncated
            # The token limit check happens at route_result level
            return data

    def estimate_tokens(self, data: Any) -> int:
        """Estimate token count for data.

        Args:
            data: Data to estimate

        Returns:
            Estimated token count
        """
        json_str = json.dumps(data, indent=2, default=str)
        return self.token_estimator.estimate_tokens(json_str)

    def will_fit_in_context(self, data: Any) -> bool:
        """Check if data will fit within the token limit.

        Args:
            data: Data to check

        Returns:
            True if data fits within limit
        """
        token_count = self.estimate_tokens(data)
        return token_count <= self.config.safe_token_limit


__all__ = ["ResultOutputHandler"]
