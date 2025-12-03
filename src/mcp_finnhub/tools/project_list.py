"""Implement the `finnhub_project_list` MCP tool."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from pathlib import Path

    from mcp_finnhub.server import ServerContext


SUPPORTED_OPERATIONS = ["list"]


def _unknown_operation(operation: str) -> dict[str, Any]:
    """Return error response for unknown operation."""
    return {
        "error": {
            "code": "UNKNOWN_OPERATION",
            "message": f"Unknown operation: {operation}. Supported: {', '.join(SUPPORTED_OPERATIONS)}",
            "details": {"operation": operation, "supported": SUPPORTED_OPERATIONS},
        }
    }


def _count_files(directory: Path) -> int:
    """Count files in a directory recursively."""
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.rglob("*") if _.is_file())


def _get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes."""
    if not directory.exists():
        return 0
    return sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


async def finnhub_project_list(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """List all project workspaces with metadata and statistics.

    Scans the storage directory for project directories (those containing
    .project.json metadata files) and returns information about each project.

    Args:
        context: Server context with path resolver
        operation: Must be "list"
        **kwargs: Tool arguments (none required)

    Returns:
        Success response with projects list or error

    Supported Operations:
        list: List all projects with statistics

    Example:
        >>> await finnhub_project_list(context, "list")
        {
            "projects": [
                {
                    "name": "my-analysis",
                    "path": "/path/to/my-analysis",
                    "created_at": "2025-11-18T10:30:00Z",
                    "subdirectories": ["candles", "quotes", ...],
                    "file_counts": {"candles": 5, "quotes": 10, ...},
                    "total_files": 15,
                    "total_size": "1.2 MB"
                }
            ],
            "total_projects": 1
        }
    """
    if operation != "list":
        return _unknown_operation(operation)

    root = context.path_resolver.storage_dir
    if not root.exists():
        return {"projects": [], "total_projects": 0}

    projects = []

    # Scan for directories with .project.json
    for project_dir in root.iterdir():
        if not project_dir.is_dir():
            continue

        metadata_path = project_dir / ".project.json"
        if not metadata_path.exists():
            continue

        # Read metadata
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Skip projects with invalid metadata
            continue

        # Get file counts per subdirectory
        subdirectories = metadata.get("subdirectories", [])
        file_counts = {}
        total_files = 0

        for subdir in subdirectories:
            subdir_path = project_dir / subdir
            count = _count_files(subdir_path)
            file_counts[subdir] = count
            total_files += count

        # Get total size
        total_size_bytes = _get_directory_size(project_dir)

        projects.append(
            {
                "name": metadata.get("project", project_dir.name),
                "path": str(project_dir),
                "created_at": metadata.get("created_at"),
                "subdirectories": subdirectories,
                "file_counts": file_counts,
                "total_files": total_files,
                "total_size": _format_size(total_size_bytes),
                "total_size_bytes": total_size_bytes,
            }
        )

    # Sort by created_at (newest first)
    projects.sort(key=lambda p: p.get("created_at") or "", reverse=True)

    return {"projects": projects, "total_projects": len(projects)}


__all__ = ["finnhub_project_list"]
