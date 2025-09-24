"""Presence analysis for field presence patterns in sample data."""

from dataclasses import dataclass

from factoreally.constants import MAX_PRECISION
from factoreally.hints import MissingHint
from factoreally.hints.base import AnalysisHint


@dataclass
class FieldPresence:
    presence_percentage: float
    presence_count: int
    total_records: int


class PresenceAnalyzer:
    """Analyzes field presence patterns in sample data."""

    def __init__(self) -> None:
        """Initialize presence analyzer."""
        self.field_counts: dict[str, int] = {}
        self.total_records = 0
        self.parent_presence: dict[str, int] = {}

    def calculate(
        self,
        field_presences: dict[str, int],
        total_items: int,
        discovered_fields: set[str],
        parent_presence: dict[str, int] | None = None,
    ) -> None:
        self.parent_presence = parent_presence or {}

        presence_percentages = calculate_presence_percentages(
            field_presences,
            total_items,
            discovered_fields,
        )
        for field in discovered_fields:
            if field_presence := presence_percentages.get(field):
                self.field_counts[field] = field_presence.presence_count
        self.total_records = total_items

    def _get_parent_path(self, field_path: str) -> str | None:
        """Get the parent path of a nested field for conditional presence analysis."""
        if "." in field_path:
            return ".".join(field_path.split(".")[:-1])
        return None

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Generate presence-based hint for factory generation."""

        # Skip presence analysis for array element fields (those ending with [])
        # Array elements represent individual values within arrays, not optional fields
        if field.endswith("[]"):
            return None

        # Skip presence analysis for dynamic object key template fields (those ending with {})
        # These represent key patterns within dynamic objects, not optional fields
        if field.endswith("{}"):
            return None

        parent_path = self._get_parent_path(field)
        if parent_path and parent_path in self.parent_presence:
            # Use conditional presence for nested fields
            # Only calculate presence percentage when the parent is non-null
            total_records = self.parent_presence[parent_path]  # Use parent count as denominator
        else:
            # Default behavior for top-level fields
            total_records = self.total_records  # Use all records as denominator

        field_count = self.field_counts.get(field, 0)
        percentage = (field_count / total_records) * 100

        # Make the field optional if it is not 100% present in the sample data.
        # No hint needed for 100% present fields - they are assumed required by default.
        if percentage == 100:
            return None
        return MissingHint(pct=round(100 - percentage, MAX_PRECISION))


def calculate_presence_percentages(
    field_presence: dict[str, int],
    total_records: int,
    discovered_fields: set[str],
) -> dict[str, FieldPresence]:
    """Calculate field presence percentages for factory generation."""
    percentages: dict[str, FieldPresence] = {}
    for field in sorted(discovered_fields):
        presence_count = field_presence.get(field, 0)
        percentage = (presence_count / total_records) * 100 if total_records > 0 else 0
        percentages[field] = FieldPresence(
            presence_percentage=percentage,
            presence_count=presence_count,
            total_records=total_records,
        )
    return percentages
