"""Data extraction and traversal for sample data analysis."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from factoreally.hints.base import SimpleType
from factoreally.pydantic_models import analyze_pydantic_model

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic import BaseModel

    from factoreally.analyzers import Analyzers


@dataclass
class ExtractedData:
    """Structured data extracted from sample analysis."""

    item_count: int = 0
    data_point_count: int = 0
    field_paths: set[str] = field(default_factory=set)
    field_value_counts: dict[str, Counter[SimpleType]] = field(default_factory=lambda: defaultdict(Counter))
    dynamic_object_fields: set[str] = field(default_factory=set)


def extract_data(
    items: Iterable[dict[str, Any]],
    *,
    az: Analyzers,
    model: type[BaseModel] | None,
) -> ExtractedData:
    """Extract structured data from sample items for analysis.

    Args:
        items: Iterable of dictionary items to analyze
        model: Pydantic model for guidance on dynamic object fields

    Returns:
        ExtractedData containing extracted fields, values, and presence information
    """

    # Analyze Pydantic model if provided to detect dynamic object fields
    dynamic_object_fields: set[str] = analyze_pydantic_model(model) if model else set()

    # Create ExtractedData instance with defaults
    extracted_data = ExtractedData(dynamic_object_fields=dynamic_object_fields)

    for item in items:
        extracted_data.item_count += 1
        # Analyze the complete object structure recursively
        extracted_data.data_point_count += _extract_value(
            field="",
            value=item,
            ed=extracted_data,
            az=az,
        )

    return extracted_data


def _extract_value(
    field: str,
    value: Any,
    ed: ExtractedData,
    az: Analyzers,
) -> int:
    """Extract data from object with reduced complexity."""

    data_point_count = 0

    az.presence_analyzer.collect_field_value(field, value)

    if field:
        ed.field_paths.add(field)
        az.null_analyzer.collect_field_value(field, value)

    if isinstance(value, dict):
        if field.replace("[]", "") in ed.dynamic_object_fields:
            # For dynamic objects with patterns, create a {} field to capture value patterns
            az.object_analyzer.collect_field_value(field, value)
            data_point_count += len(value.keys())
            child_field = field + ".{}"
            for child_value in value.values():
                data_point_count += _extract_value(child_field, child_value, ed, az)
        else:
            for child_key, child_value in value.items():
                child_field = f"{field}.{child_key}" if field else child_key
                data_point_count += _extract_value(child_field, child_value, ed, az)

    elif isinstance(value, list):
        az.array_analyzer.collect_field_value(field, value)
        child_field = field + "[]"
        for child_value in value:
            data_point_count += _extract_value(child_field, child_value, ed, az)

    elif isinstance(value, SimpleType):
        ed.field_value_counts[field][value] += 1
        data_point_count += 1

    elif value is None:
        data_point_count += 1

    return data_point_count
