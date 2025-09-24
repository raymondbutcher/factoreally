"""Object key analysis for dynamic object generation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING

from factoreally.hints import ObjectHint

if TYPE_CHECKING:
    from collections.abc import KeysView

    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class ObjectAnalyzer:
    """Analyzes object key patterns for factory generation."""

    def __init__(self) -> None:
        self.field_key_counts: dict[str, Counter[SimpleType]] = defaultdict(Counter)
        self.field_key_patterns: dict[str, list[SimpleType]] = defaultdict(list)

    def collect_one(
        self,
        field: str,
        keys: KeysView[SimpleType],
    ) -> None:
        # Count the number of keys (object size)
        self.field_key_counts[field][len(keys)] += 1
        # Also collect the actual keys for pattern analysis
        self.field_key_patterns[field].extend(keys)

    def analyze_all(self, field: str, az: Analyzers) -> None:
        """Analyze all keys for a field across all items"""
        if field in self.field_key_counts:
            meta_field = field + "#"
            # Analyze key counts (number of keys per object)
            az.numeric_analyzer.analyze_all(meta_field, self.field_key_counts[field])
            # Analyze key patterns (the actual key strings)
            if field in self.field_key_patterns:
                key_counter = Counter(self.field_key_patterns[field])
                az.string_pattern_analyzer.analyze_all(meta_field, key_counter)

    def get_hints(self, field: str, az: Analyzers) -> list[AnalysisHint]:
        if field in self.field_key_counts:
            marker_field = field + "#"
            if object_size_hint := az.numeric_analyzer.get_hint(marker_field):
                hints: list[AnalysisHint] = [ObjectHint(), object_size_hint]
                if key_pattern_hint := az.string_pattern_analyzer.get_hint(marker_field):
                    hints.append(key_pattern_hint)
                return hints
        return []
