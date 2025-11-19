"""Implement the `finnhub_project_create` MCP tool."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from mcp_finnhub.server import ServerContext


SUPPORTED_OPERATIONS = ["create"]
VALID_NAME = re.compile(r"^[A-Za-z0-9_-]+$")
SUBDIRECTORIES = ["candles", "quotes", "news", "fundamentals", "technical", "jobs"]


def _invalid_project_name(name: str) -> dict[str, Any]:
    """Return error response for invalid project name."""
    return {
        "error": {
            "code": "INVALID_PROJECT_NAME",
            "message": "Project names must use letters, numbers, hyphens, or underscores only.",
            "details": {"project": name},
        }
    }


def _project_exists(name: str) -> dict[str, Any]:
    """Return error response for existing project."""
    return {
        "error": {
            "code": "PROJECT_EXISTS",
            "message": f"Project '{name}' already exists.",
            "details": {"project": name},
        }
    }


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


async def finnhub_project_create(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Create a new project workspace with directory structure.

    Creates a project directory with subdirectories for organizing different
    types of Finnhub data (candles, quotes, news, fundamentals, technical, jobs).

    Args:
        context: Server context with path resolver
        operation: Must be "create"
        **kwargs: Tool arguments including:
            project (str): Project name (required)

    Returns:
        Success response with project details or error

    Supported Operations:
        create: Create a new project directory

    Example:
        >>> await finnhub_project_create(context, "create", project="my-analysis")
        {
            "project": "my-analysis",
            "path": "/path/to/finnhub-data/my-analysis",
            "metadata_file": "/path/to/finnhub-data/my-analysis/.project.json",
            "subdirectories": ["candles", "quotes", ...]
        }
    """
    project_value = kwargs.get("project")

    if operation != "create":
        return _unknown_operation(operation)

    if project_value is None:
        return _missing_parameter("project")

    project_name = str(project_value)
    if not project_name:
        return _invalid_project_name(project_name)

    if not VALID_NAME.fullmatch(project_name):
        return _invalid_project_name(project_name)

    root = context.path_resolver.storage_dir
    project_dir = root / project_name
    if project_dir.exists():
        return _project_exists(project_name)

    # Create directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    for subdir in SUBDIRECTORIES:
        (project_dir / subdir).mkdir(exist_ok=True)

    # Create metadata
    metadata = {
        "project": project_name,
        "created_at": datetime.now(UTC).isoformat(),
        "subdirectories": SUBDIRECTORIES,
    }
    metadata_path = project_dir / ".project.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "project": project_name,
        "path": str(project_dir),
        "metadata_file": str(metadata_path),
        "subdirectories": SUBDIRECTORIES,
        "created_at": metadata["created_at"],
    }


__all__ = ["finnhub_project_create"]
