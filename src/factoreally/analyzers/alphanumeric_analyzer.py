"""Alphanumeric pattern analysis for general string patterns."""

from collections import Counter, defaultdict

from factoreally.constants import MIN_VALUES_FOR_ALPLHANUMERIC
from factoreally.hints import AlphanumericHint
from factoreally.hints.base import AnalysisHint, SimpleType


class AlphanumericAnalyzer:
    """Analyzes general alphanumeric patterns in string data for factory generation."""

    def __init__(self) -> None:
        """Initialize alphanumeric pattern analyzer."""
        self.field_hints: dict[str, AnalysisHint] = {}

    def analyze_all(
        self,
        field: str,
        value_counts: Counter[SimpleType],
    ) -> None:
        """Analyze all values for a field across all items"""
        if len(value_counts) < MIN_VALUES_FOR_ALPLHANUMERIC:
            return

        # Get all string values
        string_values = [(v, count) for v, count in value_counts.items() if isinstance(v, str)]
        if not string_values or len(string_values) != len(value_counts):
            return

        # Check if all values are the same length
        lengths = {len(v) for v, _ in string_values}
        if len(lengths) != 1:
            return  # Exit early if not all same length

        # Continue with existing analysis for character position tracking
        char_positions: dict[int, Counter[str]] = defaultdict(Counter)
        for value, count in string_values:
            # Character position analysis
            for i, char in enumerate(value):
                char_positions[i][char] += count

        # Build efficient character set groupings
        charset_to_positions: dict[str, list[int]] = {}
        for pos, char_counter in char_positions.items():
            charset = "".join(sorted(char_counter.keys()))
            if charset not in charset_to_positions:
                charset_to_positions[charset] = []
            charset_to_positions[charset].append(pos)

        # Create and store hint
        hint = AlphanumericHint(chrs=charset_to_positions)
        self.field_hints[field] = hint

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Return stored hint for the field."""
        return self.field_hints.get(field)
