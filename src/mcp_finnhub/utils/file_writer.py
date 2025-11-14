"""File writing utilities for JSON and CSV exports.

Provides safe file writing with error handling for permissions and disk space.
Supports streaming CSV writes for large datasets.
"""

from __future__ import annotations

import csv
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class FileWriter:
    """Write JSON and CSV files with error handling.

    Example:
        >>> writer = FileWriter()
        >>> writer.write_json({"key": "value"}, Path("/data/output.json"))
        >>> writer.write_csv([{"a": 1, "b": 2}], Path("/data/output.csv"))
    """

    def write_json(self, data: dict[str, Any] | list[Any], filepath: Path, indent: int = 2) -> None:
        """Write data to JSON file with formatting.

        Args:
            data: Data to write (dict or list)
            filepath: Path to output file
            indent: JSON indentation (default: 2)

        Raises:
            OSError: If write fails (permissions, disk space, etc.)
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    def write_csv(
        self,
        data: list[dict[str, Any]],
        filepath: Path,
        include_headers: bool = True,
    ) -> None:
        """Write list of dicts to CSV file.

        Args:
            data: List of dictionaries with consistent keys
            filepath: Path to output file
            include_headers: Whether to write header row (default: True)

        Raises:
            ValueError: If data is empty or has inconsistent keys
            OSError: If write fails
        """
        if not data:
            raise ValueError("Cannot write empty data to CSV")

        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Get field names from first row
        fieldnames = list(data[0].keys())

        with filepath.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if include_headers:
                writer.writeheader()
            writer.writerows(data)

    def append_csv(self, data: list[dict[str, Any]], filepath: Path) -> None:
        """Append rows to existing CSV file.

        Args:
            data: List of dictionaries to append
            filepath: Path to existing CSV file

        Raises:
            ValueError: If data is empty
            OSError: If write fails
        """
        if not data:
            raise ValueError("Cannot append empty data to CSV")

        fieldnames = list(data[0].keys())

        with filepath.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(data)


__all__ = ["FileWriter"]
