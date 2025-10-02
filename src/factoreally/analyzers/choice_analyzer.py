"""Choice analysis for sample data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from factoreally.constants import MIN_VALUES_FOR_CHOICE_WARNING
from factoreally.hints import ChoiceHint, ConstantValueHint

if TYPE_CHECKING:
    from collections import Counter

    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType


class ChoiceAnalyzer:
    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self.fields_with_too_many_values: dict[str, int] = {}

    def get_hint(self, field: str, value_counts: Counter[SimpleType]) -> AnalysisHint | None:
        """Generate structured hint for choice field factory generation."""

        if len(value_counts) >= 2:  # noqa: PLR2004
            if len(value_counts) > MIN_VALUES_FOR_CHOICE_WARNING:
                self.fields_with_too_many_values[field] = len(value_counts)
            return ChoiceHint.create(value_counts)

        if value_counts:
            constant_value = next(iter(value_counts.keys()))
            return ConstantValueHint(val=constant_value)

        return None
