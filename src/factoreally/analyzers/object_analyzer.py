"""Object key analysis for dynamic object generation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any

from factoreally.analyzers.base import FieldAnalyzer, FieldValueCollector
from factoreally.hints import ObjectHint

if TYPE_CHECKING:
    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class ObjectAnalyzer(FieldValueCollector, FieldAnalyzer):
    """Analyzes object key patterns for factory generation."""

    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self._field_key_counts: dict[str, Counter[SimpleType]] = defaultdict(Counter)
        self._field_key_patterns: dict[str, list[SimpleType]] = defaultdict(list)

    @property
    def dynamic_object_fields(self) -> list[str]:
        return list(self._field_key_counts.keys())

    def collect_field_value(self, field: str, value: Any) -> None:
        if not isinstance(value, dict):
            raise TypeError(type(value))
        # Count the number of keys (object size)
        self._field_key_counts[field][len(value)] += 1
        # Also collect the actual keys for pattern analysis
        self._field_key_patterns[field].extend(value.keys())

    def analyze_field(self, field: str) -> None:
        """Analyze all keys for a field across all items"""
        if field in self._field_key_counts:
            meta_field = field + "#"
            # Analyze key counts (number of keys per object)
            self._az.numeric_analyzer.analyze_field_value_counts(meta_field, self._field_key_counts[field])
            # Analyze key patterns (the actual key strings)
            if field in self._field_key_patterns:
                key_counter = Counter(self._field_key_patterns[field])
                self._az.string_pattern_analyzer.analyze_field_value_counts(meta_field, key_counter)

    def get_hints(self, field: str) -> list[AnalysisHint]:
        if field in self._field_key_counts:
            marker_field = field + "#"
            if object_size_hint := self._az.numeric_analyzer.get_hint(marker_field):
                hints: list[AnalysisHint] = [ObjectHint(), object_size_hint]
                if key_pattern_hint := self._az.string_pattern_analyzer.get_hint(marker_field):
                    hints.append(key_pattern_hint)
                return hints
        return []
