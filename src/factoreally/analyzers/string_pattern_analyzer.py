"""String pattern analysis combining temporal and structured pattern detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from factoreally.analyzers.base import FieldValueCountsAnalyzer
from factoreally.hints import (
    AlphanumericHint,
    Auth0IdHint,
    DateHint,
    DatetimeHint,
    DurationRangeHint,
    MacAddressHint,
    NumberStringHint,
    TextHint,
    Uuid4Hint,
    VersionHint,
)

if TYPE_CHECKING:
    from collections import Counter
    from collections.abc import Callable

    from factoreally.analyzers import Analyzers
    from factoreally.hints.base import AnalysisHint, SimpleType

# Pattern hint creators that check patterns and return hints directly
PATTERN_HINT_CREATORS: list[Callable[[list[str]], AnalysisHint | None]] = [
    DatetimeHint.create_from_values,
    DateHint.create_from_values,
    DurationRangeHint.create_from_values,
    Auth0IdHint.create_from_values,
    MacAddressHint.create_from_values,
    Uuid4Hint.create_from_values,
    VersionHint.create_from_values,
    NumberStringHint.create_from_values,
    AlphanumericHint.create_from_values,  # low priority, fixed-length strings
    TextHint.create_from_values,  # low priority, long strings with spaces
]


class StringPatternAnalyzer(FieldValueCountsAnalyzer):
    """Analyzes string patterns for factory generation."""

    def __init__(self, az: Analyzers) -> None:
        self._az = az
        self._field_hints: dict[str, AnalysisHint] = {}

    def analyze_field_value_counts(self, field: str, value_counts: Counter[SimpleType]) -> bool:
        """Analyze string values for consistent patterns across ALL values in the field."""
        # Extract all unique string values for this field
        string_values = [value for value in value_counts if isinstance(value, str)]

        if not string_values or len(string_values) != len(value_counts):
            return False

        # Check each pattern hint creator until one matches
        for create_hint in PATTERN_HINT_CREATORS:
            hint = create_hint(string_values)
            if hint:
                self._field_hints[field] = hint
                return True

        return False

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Get pattern hint for a field."""
        return self._field_hints.get(field)
