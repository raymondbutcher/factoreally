"""Array length analysis for realistic list generation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING

from factoreally.hints import ArrayHint

if TYPE_CHECKING:
    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class ArrayAnalyzer:
    """Analyzes array lengths for factory generation."""

    def __init__(self) -> None:
        self.field_length_counts: dict[str, Counter[SimpleType]] = defaultdict(Counter)

    def collect_one(
        self,
        field: str,
        array_size: int,
    ) -> None:
        """Collect information about a field in one item"""
        self.field_length_counts[field][array_size] += 1

    def analyze_all(self, field: str, az: Analyzers) -> None:
        """Analyze all array lengths for a field across all items"""
        if field in self.field_length_counts:
            meta_field = field + "#"
            length_counts = self.field_length_counts[field]
            az.numeric_analyzer.analyze_all(meta_field, length_counts)

    def get_hints(self, field: str, az: Analyzers) -> list[AnalysisHint]:
        if field in self.field_length_counts:
            meta_field = field + "#"
            if length_hint := az.numeric_analyzer.get_hint(meta_field):
                return [ArrayHint(), length_hint]
        return []
