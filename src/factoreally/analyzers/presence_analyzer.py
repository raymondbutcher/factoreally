"""Presence analysis for field presence patterns in sample data."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from factoreally.analyzers.base import FieldValueCollector
from factoreally.constants import MAX_PRECISION
from factoreally.hints import MissingHint

if TYPE_CHECKING:
    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint


class PresenceAnalyzer(FieldValueCollector):
    """Analyzes field presence patterns in sample data."""

    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self._field_counts: dict[str, int] = defaultdict(int)
        self._parent_field_counts: dict[str, int] = defaultdict(int)

    def collect_field_value(self, field: str, value: Any) -> None:
        """Collect information about a field in one item"""
        self._field_counts[field] += 1
        if value is not None:
            self._parent_field_counts[field] += 1

    def _get_parent_path(self, field_path: str) -> str:
        """Get the parent path of a nested field for conditional presence analysis."""
        if "." in field_path:
            return ".".join(field_path.split(".")[:-1])
        return ""

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Generate presence-based hint for factory generation."""

        # Skip presence analysis for array element fields (those ending with [])
        # Array elements represent individual values within arrays, not optional fields
        if field.endswith("[]"):
            return None

        # Skip presence analysis for dynamic object key template fields (those ending with {})
        # These represent key patterns within dynamic objects, not optional fields
        if field.endswith("{}"):
            return None

        parent_field = self._get_parent_path(field)
        parent_count = self._parent_field_counts[parent_field]

        field_count = self._field_counts[field]
        percentage = (field_count / parent_count) * 100

        # No hint needed for 100% present fields
        if percentage == 100:  # noqa: PLR2004
            return None

        return MissingHint(pct=round(100 - percentage, MAX_PRECISION))
