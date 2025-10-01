"""Array length analysis for realistic list generation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any

from factoreally.analyzers.base import FieldAnalyzer, FieldValueCollector
from factoreally.hints import ArrayHint

if TYPE_CHECKING:
    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class ArrayAnalyzer(FieldValueCollector, FieldAnalyzer):
    """Analyzes array lengths for factory generation."""

    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self._field_length_counts: dict[str, Counter[SimpleType]] = defaultdict(Counter)

    @property
    def array_fields(self) -> list[str]:
        return list(self._field_length_counts.keys())

    def collect_field_value(self, field: str, value: Any) -> None:
        """Collect information about a field in one item"""
        if not isinstance(value, list):
            raise TypeError(type(value))
        self._field_length_counts[field][len(value)] += 1

    def analyze_field(self, field: str) -> None:
        """Analyze all array lengths for a field across all items"""
        if field in self._field_length_counts:
            meta_field = field + "#"
            length_counts = self._field_length_counts[field]
            self._az.numeric_analyzer.analyze_field_value_counts(meta_field, length_counts)

    def get_hints(self, field: str) -> list[AnalysisHint]:
        if field in self._field_length_counts:
            meta_field = field + "#"
            if length_hint := self._az.numeric_analyzer.get_hint(meta_field):
                return [ArrayHint(), length_hint]
        return []
