"""Implement the `finnhub_job_status` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from mcp_finnhub.server import ServerContext


SUPPORTED_OPERATIONS = ["get"]


def _unknown_operation(operation: str) -> dict[str, Any]:
    """Return error response for unknown operation."""
    return {
        "error": {
            "code": "UNKNOWN_OPERATION",
            "message": f"Unknown operation: {operation}. Supported: {', '.join(SUPPORTED_OPERATIONS)}",
            "details": {"operation": operation, "supported": SUPPORTED_OPERATIONS},
        }
    }


def _missing_parameter(param: str) -> dict[str, Any]:
    """Return error response for missing required parameter."""
    return {
        "error": {
            "code": "MISSING_PARAMETER",
            "message": f"Missing required parameter: {param}",
            "details": {"parameter": param},
        }
    }


def _job_not_found(job_id: str) -> dict[str, Any]:
    """Return error response for job not found."""
    return {
        "error": {
            "code": "JOB_NOT_FOUND",
            "message": f"Job not found: {job_id}",
            "details": {"job_id": job_id},
        }
    }


async def finnhub_job_status(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Get the status of a background job.

    Retrieves detailed information about a background job including its
    current status, progress, result (if completed), and error (if failed).

    Args:
        context: Server context with job manager
        operation: Must be "get"
        **kwargs: Tool arguments including:
            job_id (str): Job identifier (required)

    Returns:
        Success response with job details or error

    Supported Operations:
        get: Get job status by ID

    Example:
        >>> await finnhub_job_status(context, "get", job_id="abc-123")
        {
            "job_id": "abc-123",
            "status": "COMPLETED",
            "progress": 100.0,
            "created_at": "2025-11-18T10:30:00Z",
            "updated_at": "2025-11-18T10:35:00Z",
            "result": {"rows": 1000, "file": "data.csv"}
        }
    """
    job_id_value = kwargs.get("job_id")

    if operation != "get":
        return _unknown_operation(operation)

    if job_id_value is None:
        return _missing_parameter("job_id")

    job_id = str(job_id_value)
    if not job_id:
        return _missing_parameter("job_id")

    # Get job from manager
    job = context.job_manager.get_job(job_id)
    if job is None:
        return _job_not_found(job_id)

    # Build response from job model
    response = {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }

    # Add result if completed
    if job.result is not None:
        response["result"] = job.result

    # Add error if failed
    if job.error is not None:
        response["error"] = job.error

    # Add metadata if present
    if job.metadata:
        response["metadata"] = job.metadata

    return response


__all__ = ["finnhub_job_status"]
