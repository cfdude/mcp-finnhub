"""Job models for background task management.

Provides data models for tracking long-running background jobs with
persistence and status management.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(BaseModel):
    """Background job model.

    Attributes:
        job_id: Unique job identifier
        tool_name: Name of tool being executed
        params: Tool parameters
        status: Current job status
        created_at: Job creation timestamp
        started_at: Job start timestamp (if started)
        completed_at: Job completion timestamp (if completed)
        result: Job result (if completed)
        error: Error message (if failed)
        progress: Progress percentage (0-100)
        message: Status message for user
        metadata: Additional metadata
        updated_at: Most recent update timestamp (computed property)
    """

    job_id: str = Field(description="Unique job identifier")
    tool_name: str = Field(description="Name of tool being executed")
    params: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    started_at: datetime | None = Field(default=None, description="Start time")
    completed_at: datetime | None = Field(default=None, description="Completion time")
    result: dict[str, Any] | None = Field(default=None, description="Job result")
    error: str | None = Field(default=None, description="Error message")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: str = Field(default="", description="Status message")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def updated_at(self) -> datetime:
        """Get the most recent update timestamp."""
        return self.completed_at or self.started_at or self.created_at

    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }

    @property
    def duration_seconds(self) -> float | None:
        """Calculate job duration in seconds (if started)."""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    def mark_running(self, message: str = "") -> None:
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.message = message or "Job started"

    def mark_completed(self, result: dict[str, Any], message: str = "") -> None:
        """Mark job as completed successfully."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
        self.progress = 100
        self.message = message or "Job completed successfully"

    def mark_failed(self, error: str, message: str = "") -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error
        self.message = message or f"Job failed: {error}"

    def mark_cancelled(self, message: str = "") -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.message = message or "Job cancelled"

    def update_progress(self, progress: int, message: str = "") -> None:
        """Update job progress."""
        self.progress = max(0, min(100, progress))
        if message:
            self.message = message


__all__ = ["Job", "JobStatus"]
