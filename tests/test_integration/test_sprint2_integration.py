"""Integration tests for Sprint 2 components.

Tests the integration of:
- FinnhubClient (API client with rate limiting, retries)
- FinnhubAPIError (error handling)
- Pydantic response models (QuoteResponse, CandleResponse, etc.)
- JobManager (job persistence and lifecycle)
- BackgroundWorker (async job execution)
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.errors import AuthenticationError, RateLimitError
from mcp_finnhub.api.models.common import CandleResponse, QuoteResponse
from mcp_finnhub.config import AppConfig
from mcp_finnhub.jobs.manager import JobManager
from mcp_finnhub.jobs.models import JobStatus
from mcp_finnhub.jobs.worker import BackgroundWorker


class TestClientErrorIntegration:
    """Test integration of FinnhubClient with error handling."""

    @pytest.fixture
    def test_config(self, tmp_path: Path) -> AppConfig:
        """Create test configuration."""
        return AppConfig(
            finnhub_api_key="test_api_key",
            storage_directory=tmp_path / "data",
            rate_limit_rpm=60,
            request_timeout=5,
            max_retries=2,
            retry_backoff_factor=1.5,
            retry_jitter=0.1,
        )

    @respx.mock
    async def test_client_handles_authentication_error(self, test_config: AppConfig):
        """Test that client properly handles 401 errors."""
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(401, json={"error": "Invalid API key"})
        )

        async with FinnhubClient(test_config) as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.get("/quote", params={"symbol": "AAPL"})

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.message

    @respx.mock
    async def test_client_handles_rate_limit(self, test_config: AppConfig):
        """Test that client properly handles 429 errors."""
        respx.get("https://finnhub.io/api/v1/quote").mock(
            side_effect=[
                httpx.Response(429, json={"error": "Rate limit exceeded"}),
                httpx.Response(429, json={"error": "Rate limit exceeded"}),
                httpx.Response(429, json={"error": "Rate limit exceeded"}),
            ]
        )

        async with FinnhubClient(test_config) as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.get("/quote", params={"symbol": "AAPL"})

        assert exc_info.value.status_code == 429
        assert "Rate limit" in exc_info.value.message


class TestClientModelIntegration:
    """Test integration of FinnhubClient with Pydantic models."""

    @pytest.fixture
    def test_config(self, tmp_path: Path) -> AppConfig:
        """Create test configuration."""
        return AppConfig(
            finnhub_api_key="test_api_key",
            storage_directory=tmp_path / "data",
            rate_limit_rpm=60,
            request_timeout=5,
            max_retries=2,
            retry_backoff_factor=1.5,
            retry_jitter=0.1,
        )

    @respx.mock
    async def test_client_returns_valid_quote_model(self, test_config: AppConfig):
        """Test that client can fetch and parse quote data."""
        quote_data = {
            "c": 150.25,
            "d": 2.50,
            "dp": 1.69,
            "h": 151.00,
            "l": 149.00,
            "o": 149.50,
            "pc": 147.75,
            "t": 1609459200,
        }

        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(200, json=quote_data)
        )

        async with FinnhubClient(test_config) as client:
            response = await client.get("/quote", params={"symbol": "AAPL"})

        # Parse with Pydantic model
        quote = QuoteResponse(**response)
        assert quote.c == 150.25
        assert quote.d == 2.50
        assert quote.t == 1609459200
        assert isinstance(quote.timestamp_dt, datetime)

    @respx.mock
    async def test_client_returns_valid_candle_model(self, test_config: AppConfig):
        """Test that client can fetch and parse candle data."""
        candle_data = {
            "c": [150.0, 151.0, 152.0],
            "h": [151.0, 152.0, 153.0],
            "l": [149.0, 150.0, 151.0],
            "o": [149.5, 150.5, 151.5],
            "s": "ok",
            "t": [1609459200, 1609545600, 1609632000],
            "v": [1000000, 1100000, 1200000],
        }

        respx.get("https://finnhub.io/api/v1/stock/candle").mock(
            return_value=httpx.Response(200, json=candle_data)
        )

        async with FinnhubClient(test_config) as client:
            response = await client.get(
                "/stock/candle",
                params={"symbol": "AAPL", "resolution": "D", "from": 1609459200, "to": 1609632000},
            )

        # Parse with Pydantic model
        candles = CandleResponse(**response)
        assert candles.s == "ok"
        assert len(candles.c) == 3
        assert len(candles.h) == 3
        assert len(candles.timestamps_dt) == 3


class TestJobWorkerIntegration:
    """Test integration of JobManager with BackgroundWorker."""

    @pytest.fixture
    def job_manager(self, tmp_path: Path) -> JobManager:
        """Create job manager."""
        return JobManager(tmp_path / "jobs")

    @pytest.fixture
    def worker(self, job_manager: JobManager) -> BackgroundWorker:
        """Create background worker."""
        return BackgroundWorker(job_manager, max_workers=3, default_timeout=5.0)

    async def test_job_lifecycle_with_worker(
        self, job_manager: JobManager, worker: BackgroundWorker
    ):
        """Test complete job lifecycle from creation to completion."""

        # Define a tool handler
        async def calculate_sum(values: list[int]) -> dict:
            await asyncio.sleep(0.1)
            return {"sum": sum(values), "count": len(values)}

        worker.register_tool("calculate_sum", calculate_sum)

        # 1. Create job
        job = job_manager.create_job("calculate_sum", {"values": [1, 2, 3, 4, 5]})
        assert job.status == JobStatus.PENDING

        # 2. Submit job to worker
        task = await worker.submit_job(job.job_id)
        assert worker.is_running(job.job_id)

        # 3. Wait for completion
        result_job = await task
        assert result_job.status == JobStatus.COMPLETED
        assert result_job.result == {"sum": 15, "count": 5}

        # 4. Verify persistence
        persisted_job = job_manager.get_job(job.job_id)
        assert persisted_job.status == JobStatus.COMPLETED
        assert persisted_job.result == {"sum": 15, "count": 5}

    async def test_concurrent_jobs_with_persistence(
        self, job_manager: JobManager, worker: BackgroundWorker
    ):
        """Test multiple concurrent jobs with persistence."""

        async def process_data(value: int) -> dict:
            await asyncio.sleep(0.1)
            return {"result": value * 2}

        worker.register_tool("process_data", process_data)

        # Create multiple jobs
        job_ids = []
        for i in range(5):
            job = job_manager.create_job("process_data", {"value": i})
            job_ids.append(job.job_id)

        # Submit all jobs
        tasks = []
        for job_id in job_ids:
            task = await worker.submit_job(job_id)
            tasks.append(task)

        # Wait for all to complete
        results = await asyncio.gather(*tasks)

        # Verify all completed
        for i, result_job in enumerate(results):
            assert result_job.status == JobStatus.COMPLETED
            assert result_job.result == {"result": i * 2}

        # Verify persistence
        all_jobs = job_manager.list_jobs()
        completed_jobs = [j for j in all_jobs if j.status == JobStatus.COMPLETED]
        assert len(completed_jobs) == 5


class TestEndToEndIntegration:
    """Test end-to-end integration of all Sprint 2 components."""

    @pytest.fixture
    def test_config(self, tmp_path: Path) -> AppConfig:
        """Create test configuration."""
        return AppConfig(
            finnhub_api_key="test_api_key",
            storage_directory=tmp_path / "data",
            rate_limit_rpm=60,
            request_timeout=5,
            max_retries=2,
            retry_backoff_factor=1.5,
            retry_jitter=0.1,
        )

    @pytest.fixture
    def job_manager(self, tmp_path: Path) -> JobManager:
        """Create job manager."""
        return JobManager(tmp_path / "jobs")

    @pytest.fixture
    def worker(self, job_manager: JobManager) -> BackgroundWorker:
        """Create background worker."""
        return BackgroundWorker(job_manager, max_workers=3, default_timeout=10.0)

    @respx.mock
    async def test_background_api_fetch_with_model(
        self, test_config: AppConfig, job_manager: JobManager, worker: BackgroundWorker
    ):
        """Test background job that fetches API data and parses with model."""

        # Setup API mock
        quote_data = {
            "c": 150.25,
            "d": 2.50,
            "dp": 1.69,
            "h": 151.00,
            "l": 149.00,
            "o": 149.50,
            "pc": 147.75,
            "t": 1609459200,
        }

        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(200, json=quote_data)
        )

        # Define tool that uses FinnhubClient
        async def fetch_quote(symbol: str) -> dict:
            async with FinnhubClient(test_config) as client:
                response = await client.get("/quote", params={"symbol": symbol})
                quote = QuoteResponse(**response)
                return {
                    "symbol": symbol,
                    "price": quote.c,
                    "change": quote.d,
                    "timestamp": quote.t,
                }

        worker.register_tool("fetch_quote", fetch_quote)

        # Create and execute job
        job = job_manager.create_job("fetch_quote", {"symbol": "AAPL"})
        task = await worker.submit_job(job.job_id)
        result_job = await task

        # Verify result
        assert result_job.status == JobStatus.COMPLETED
        assert result_job.result["symbol"] == "AAPL"
        assert result_job.result["price"] == 150.25
        assert result_job.result["change"] == 2.50

    @respx.mock
    async def test_background_job_handles_api_errors(
        self, test_config: AppConfig, job_manager: JobManager, worker: BackgroundWorker
    ):
        """Test that background jobs properly handle API errors."""

        # Setup API mock to return 401
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(401, json={"error": "Invalid API key"})
        )

        # Define tool that uses FinnhubClient
        async def fetch_quote(symbol: str) -> dict:
            async with FinnhubClient(test_config) as client:
                response = await client.get("/quote", params={"symbol": symbol})
                return response

        worker.register_tool("fetch_quote", fetch_quote)

        # Create and execute job
        job = job_manager.create_job("fetch_quote", {"symbol": "AAPL"})
        task = await worker.submit_job(job.job_id)
        result_job = await task

        # Verify job failed
        assert result_job.status == JobStatus.FAILED
        assert "AuthenticationError" in result_job.error

    async def test_job_cleanup_after_completion(
        self, job_manager: JobManager, worker: BackgroundWorker
    ):
        """Test that old completed jobs can be cleaned up."""

        async def quick_task() -> dict:
            return {"result": "done"}

        worker.register_tool("quick_task", quick_task)

        # Create and complete multiple jobs
        for _ in range(5):
            job = job_manager.create_job("quick_task", {})
            task = await worker.submit_job(job.job_id)
            await task

        # Verify all jobs exist
        all_jobs = job_manager.list_jobs()
        assert len(all_jobs) == 5

        # Clean up jobs older than 1 hour (none should be deleted)
        deleted = job_manager.cleanup_old_jobs(older_than=timedelta(hours=1))
        assert deleted == 0

        # Clean up jobs older than -1 second (all should be deleted)
        deleted = job_manager.cleanup_old_jobs(older_than=timedelta(seconds=-1))
        assert deleted == 5

        # Verify jobs are gone
        all_jobs = job_manager.list_jobs()
        assert len(all_jobs) == 0
