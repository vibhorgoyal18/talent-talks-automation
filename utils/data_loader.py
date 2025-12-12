from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonDataLoader:
    """Lightweight helper that exposes JSON-based test data as dictionaries."""

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)
        if not self._path.exists():
            raise FileNotFoundError(f"JSON file not found at {self._path}")
        with open(self._path, "r", encoding="utf-8") as f:
            self._data: dict[str, list[dict[str, Any]]] = json.load(f)

    def rows(self, section_name: str) -> list[dict[str, Any]]:
        """Get all rows from a section (equivalent to Excel sheet)."""
        if section_name not in self._data:
            raise KeyError(f"Section '{section_name}' not found in {self._path}")
        return self._data[section_name]

    def find_by_key(self, section_name: str, key_column: str, key_value: str) -> dict[str, Any]:
        """Find a row by matching a key column value."""
        for row in self.rows(section_name):
            if str(row.get(key_column)) == key_value:
                return row
        raise KeyError(f"No data found in {section_name} for {key_column}={key_value}")
