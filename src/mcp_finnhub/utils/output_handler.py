"""Result output handler for smart routing of tool results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from mcp_finnhub.config import AppConfig
    from mcp_finnhub.jobs.manager import JobManager
    from mcp_finnhub.utils.file_writer import FileWriter
    from mcp_finnhub.utils.json_to_csv import JSONToCSVConverter
    from mcp_finnhub.utils.path_resolver import PathResolver
    from mcp_finnhub.utils.token_estimator import TokenEstimator


class ResultOutputHandler:
    """Handles smart routing of tool results to screen, file, or background job."""

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


__all__ = ["ResultOutputHandler"]
