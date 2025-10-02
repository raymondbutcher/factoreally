"""Numeric analysis for sample data including statistical distribution analysis."""

from __future__ import annotations

from typing import TYPE_CHECKING

from factoreally.analyzers.base import FieldValueCountsAnalyzer
from factoreally.hints.number_hint import NumberHint

if TYPE_CHECKING:
    from collections import Counter

    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class NumericAnalyzer(FieldValueCountsAnalyzer):
    """Analyzes numeric data for factory generation including statistical distributions."""

    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self._field_hints: dict[str, AnalysisHint] = {}

    def analyze_field_value_counts(
        self,
        field: str,
        value_counts: Counter[SimpleType],
    ) -> bool:
        """Analyze all values for a field across all items."""

        if not value_counts:
            return False

        values: list[int | float] = []

        for value, count in value_counts.items():
            if type(value) is float or type(value) is int:
                values.extend(value for _ in range(count))
            else:
                return False

        if hint := NumberHint.create_from_values(values):
            self._field_hints[field] = hint
            return True

        return False

    def get_hint(self, field: str) -> AnalysisHint | None:
        return self._field_hints.get(field)
