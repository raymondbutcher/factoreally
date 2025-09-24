"""JSON spec building for sample data analysis.

This module contains the logic for building machine-readable JSON specs from
analyzed sample data. It takes the results of the analysis phase and converts
them into the final factory specification format.
"""

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import asdict
from typing import Any

from factoreally.analyzers import Analyzers
from factoreally.extract import ExtractedData
from factoreally.hints.base import AnalysisHint, SimpleType


def build_json_spec(
    extracted: ExtractedData,
    analyzers: Analyzers,
    *,
    progress_callback: Callable[[int], None] | None = None,
) -> dict[str, Any]:
    """Build JSON spec from extracted data and analyzers.

    Args:
        extracted: The extracted data from sample items
        analyzers: The configured analyzers after analysis is complete
        progress_callback: Optional callback to update progress (called with step count)

    Returns:
        Dict containing the complete factory spec with metadata and field definitions
    """
    # Build JSON spec structure
    json_spec: dict[str, Any] = {
        "metadata": {
            "samples_analyzed": extracted.item_count,
            "unique_fields": len(extracted.field_paths),
            "total_data_points": extracted.data_point_count,
        },
        "fields": {},
    }

    # Collect field data - only include fields with hints
    for field in sorted(extracted.field_paths):
        field_hints = {}
        for hint in _get_hints(field, extracted, analyzers):
            hint_dict = asdict(hint)
            # Filter out None values to keep only meaningful data
            filtered_hint = {k: v for k, v in hint_dict.items() if v is not None}
            # Remove 'type' from params since it becomes the key
            hint_type = filtered_hint.pop("type")
            field_hints[hint_type] = filtered_hint
        # Only include fields that have hints
        if field_hints:
            json_spec["fields"][field] = field_hints

        if progress_callback:
            progress_callback(1)

    return json_spec


def _get_hints(
    field: str,
    extracted: ExtractedData,
    az: Analyzers,
) -> Iterable[AnalysisHint]:
    """Get hints for a specific field from all analyzers.

    Args:
        field: The field name to get hints for
        extracted: The extracted data containing field information
        analyzers: The configured analyzers

    Yields:
        Analysis hints for the field
    """
    value_counts = extracted.field_value_counts.get(field, Counter())

    if array_hints := az.array_analyzer.get_hints(field, az):
        yield from array_hints
    elif object_hints := az.object_analyzer.get_hints(field, az):
        yield from object_hints
    elif value_hint := _get_value_hint(az, field, value_counts):
        yield value_hint

    if hint := az.null_analyzer.get_hint(field):
        yield hint
    if hint := az.presence_analyzer.get_hint(field):
        yield hint


def _get_value_hint(az: Analyzers, field: str, value_counts: Counter[SimpleType]) -> AnalysisHint | None:
    if hint := az.numeric_analyzer.get_hint(field):
        return hint
    if hint := az.string_pattern_analyzer.get_hint(field):
        return hint
    if hint := az.alphanumeric_analyzer.get_hint(field):
        return hint
    if hint := az.choice_analyzer.get_hint(field, value_counts):
        return hint
    return None
