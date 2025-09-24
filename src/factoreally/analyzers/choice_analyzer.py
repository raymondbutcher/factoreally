"""Choice analysis for sample data."""

from collections import Counter

from factoreally.constants import MIN_VALUES_FOR_CHOICE_WARNING
from factoreally.hints import ChoiceHint, ConstantValueHint
from factoreally.hints.base import AnalysisHint, SimpleType


class ChoiceAnalyzer:
    def __init__(self) -> None:
        """Initialize choice analyzer."""
        self.field_presence_counts: dict[str, int] = {}
        self.fields_with_too_many_values: dict[str, int] = {}

    def set_field_presence(self, field_presence: dict[str, int]) -> None:
        """Set field presence information from ExtractedData."""
        self.field_presence_counts = field_presence

    def get_hint(self, field: str, value_counts: Counter[SimpleType]) -> AnalysisHint | None:
        """Generate structured hint for choice field factory generation."""

        if len(value_counts) >= 2:
            if len(value_counts) > MIN_VALUES_FOR_CHOICE_WARNING:
                self.fields_with_too_many_values[field] = len(value_counts)
            return ChoiceHint.create(value_counts)

        if value_counts:
            constant_value = next(iter(value_counts.keys()))
            return ConstantValueHint(val=constant_value)

        return None
