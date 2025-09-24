"""Null value analysis for field nullability patterns in sample data."""

from collections import defaultdict

from factoreally.constants import MAX_PRECISION
from factoreally.hints import NullHint
from factoreally.hints.base import AnalysisHint


class NullAnalyzer:
    """Analyzes field nullability patterns in sample data."""

    def __init__(self) -> None:
        """Initialize null analyzer."""
        self.field_null_counts: dict[str, int] = defaultdict(int)
        self.field_presence_counts: dict[str, int] = defaultdict(int)

    def set_field_presence(self, field_presence: dict[str, int]) -> None:
        """Set field presence information from ExtractedData."""
        self.field_presence_counts = field_presence

    def set_field_null_counts(self, field_null_counts: dict[str, int]) -> None:
        """Set field null counts from ExtractedData."""
        self.field_null_counts = field_null_counts

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Generate nullability hint for factory generation."""
        if null_count := self.field_null_counts.get(field, 0):
            present_count = self.field_presence_counts[field]
            null_percentage = (null_count / present_count) * 100
            return NullHint(pct=round(null_percentage, MAX_PRECISION))
        return None
