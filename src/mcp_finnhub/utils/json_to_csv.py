"""JSON to CSV converter utility."""

from __future__ import annotations

import csv
import io
from typing import Any


class JSONToCSVConverter:
    """Converts JSON data to CSV format."""

    def convert(self, data: list[dict[str, Any]] | dict[str, Any]) -> str:
        """Convert JSON data to CSV string.

        Args:
            data: JSON data as list of dicts or single dict

        Returns:
            CSV formatted string
        """
        if not data:
            return ""

        # Normalize to list of dicts
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            return ""

        # Get all unique keys from all records
        fieldnames = []
        for record in data:
            if isinstance(record, dict):
                for key in record:
                    if key not in fieldnames:
                        fieldnames.append(key)

        if not fieldnames:
            return ""

        # Write to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in data:
            if isinstance(record, dict):
                writer.writerow(record)

        return output.getvalue()


__all__ = ["JSONToCSVConverter"]
