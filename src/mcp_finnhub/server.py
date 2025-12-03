"""MCP server bootstrap for Finnhub."""

from __future__ import annotations

from .api.client import FinnhubClient
from .config import AppConfig, load_config
from .jobs.manager import JobManager
from .jobs.worker import BackgroundWorker
from .utils.file_writer import FileWriter
from .utils.json_to_csv import JSONToCSVConverter
from .utils.output_handler import ResultOutputHandler
from .utils.path_resolver import PathResolver
from .utils.token_estimator import TokenEstimator


class ServerContext:
    """Container wiring together shared client and utilities.

    The ServerContext provides dependency injection for all MCP tools,
    managing the lifecycle of the HTTP client, job management system,
    and utility services.

    Attributes:
        config: Application configuration
        client: Async HTTP client for Finnhub API
        token_estimator: Estimates token usage for output handling
        csv_converter: Converts JSON responses to CSV format
        path_resolver: Resolves storage paths for projects
        file_writer: Writes data to filesystem
        job_manager: Manages background job lifecycle
        background_worker: Executes async jobs with concurrency control
        output_handler: Handles smart output routing (screen/file/job)
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize server context with configuration.

        Args:
            config: Application configuration with API keys and settings
        """
        self.config = config

        # API Client
        self.client = FinnhubClient(config)

        # Utilities
        self.token_estimator = TokenEstimator()
        self.csv_converter = JSONToCSVConverter()
        self.path_resolver = PathResolver(config.storage_directory)
        self.file_writer = FileWriter()

        # Job management with dedicated jobs directory
        jobs_dir = config.storage_directory / "jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        self.job_manager = JobManager(jobs_dir)
        self.background_worker = BackgroundWorker(self.job_manager)
        self.output_handler = ResultOutputHandler(
            config,
            self.token_estimator,
            self.csv_converter,
            self.path_resolver,
            self.file_writer,
            self.job_manager,
        )

    async def aclose(self) -> None:
        """Close the HTTP client and clean up resources.

        This should be called when the server is shutting down to ensure
        graceful cleanup of connections and background tasks.
        """
        await self.client.aclose()


def build_server_context(**overrides: object) -> ServerContext:
    """Build a server context with optional configuration overrides.

    Args:
        **overrides: Configuration overrides passed to load_config()

    Returns:
        Initialized ServerContext ready for use

    Example:
        >>> context = build_server_context(finnhub_api_key="test_key")
        >>> await context.aclose()
    """
    config = load_config(**overrides)
    return ServerContext(config)


__all__ = ["ServerContext", "build_server_context"]
