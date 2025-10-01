"""Null value analysis for field nullability patterns in sample data."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from factoreally.analyzers.base import FieldValueCollector
from factoreally.constants import MAX_PRECISION
from factoreally.hints import NullHint

if TYPE_CHECKING:
    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint


class NullAnalyzer(FieldValueCollector):
    """Analyzes field nullability patterns in sample data."""

    def __init__(self, az: Analyzers) -> None:
        """Initialize null analyzer."""
        self._az = az
        self._field_null_counts: dict[str, int] = defaultdict(int)
        self._field_presence_counts: dict[str, int] = defaultdict(int)

    def collect_field_value(self, field: str, value: Any) -> None:
        self._field_presence_counts[field] += 1
        if value is None:
            self._field_null_counts[field] += 1

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Generate nullability hint for factory generation."""
        if null_count := self._field_null_counts.get(field, 0):
            present_count = self._field_presence_counts[field]
            null_percentage = (null_count / present_count) * 100
            return NullHint(pct=round(null_percentage, MAX_PRECISION))
        return None
