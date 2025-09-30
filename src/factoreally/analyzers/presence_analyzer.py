"""Presence analysis for field presence patterns in sample data."""

from collections import defaultdict
from typing import Any

from factoreally.constants import MAX_PRECISION
from factoreally.hints import MissingHint
from factoreally.hints.base import AnalysisHint


class PresenceAnalyzer:
    """Analyzes field presence patterns in sample data."""

    def __init__(self) -> None:
        """Initialize presence analyzer."""
        self.field_counts: dict[str, int] = defaultdict(int)
        self.parent_field_counts: dict[str, int] = defaultdict(int)

    def collect_one(self, field: str, value: Any) -> None:
        """Collect information about a field in one item"""
        self.field_counts[field] += 1
        if value is not None:
            self.parent_field_counts[field] += 1

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
        parent_count = self.parent_field_counts[parent_field]

        field_count = self.field_counts[field]
        percentage = (field_count / parent_count) * 100

        # No hint needed for 100% present fields
        if percentage == 100:
            return None

        return MissingHint(pct=round(100 - percentage, MAX_PRECISION))
