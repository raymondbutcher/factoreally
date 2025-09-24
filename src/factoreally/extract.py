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
    field_presence: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    field_value_counts: dict[str, Counter[SimpleType]] = field(default_factory=lambda: defaultdict(Counter))
    field_null_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    parent_presence: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    dynamic_object_fields: set[str] = field(default_factory=set)


def extract_data(items: Iterable[dict[str, Any]], *, az: Analyzers, model: type[BaseModel] | None) -> ExtractedData:
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
        extracted_data.data_point_count += _extract_object_data(
            item,
            parent_path="",
            ed=extracted_data,
            az=az,
        )

    return extracted_data


def _extract_object_data(
    obj: dict[str, Any],
    parent_path: str,
    ed: ExtractedData,
    az: Analyzers,
) -> int:
    """Extract data from object with reduced complexity."""
    data_point_count = 0

    for key, value in obj.items():
        current_path = f"{parent_path}.{key}" if parent_path else key
        data_point_count += _process_object_value(current_path, value, ed, az)

    return data_point_count


def _process_object_value(
    current_path: str,
    value: Any,
    ed: ExtractedData,
    az: Analyzers,
) -> int:
    """Process a single object value and return data point count."""
    # Track this field
    ed.field_paths.add(current_path)
    ed.field_presence[current_path] += 1
    data_point_count = 1

    if value is None:
        ed.field_null_counts[current_path] += 1
    elif isinstance(value, SimpleType):
        ed.field_value_counts[current_path][value] += 1
    elif isinstance(value, dict):
        data_point_count += _process_dict_value(current_path, value, ed, az)
    elif isinstance(value, list):
        data_point_count += _process_list_value(current_path, value, ed, az)

    return data_point_count


def _process_dict_value(
    current_path: str,
    value: dict[str, Any],
    ed: ExtractedData,
    az: Analyzers,
) -> int:
    """Process a dictionary value."""
    # Track that this parent object is present (non-null)
    ed.parent_presence[current_path] += 1

    # Check if this is a dynamic object field with detectable patterns
    if current_path.replace("[]", "") in ed.dynamic_object_fields:
        # For dynamic objects with patterns, create a {} field to capture value patterns
        az.object_analyzer.collect_one(current_path, value.keys())
        dynamic_children_path = current_path + ".{}"
        data_point_count = 0
        for obj_value in value.values():
            data_point_count += _process_object_value(dynamic_children_path, obj_value, ed, az)
        return data_point_count

    # For static objects, recursively analyze nested objects normally
    return _extract_object_data(value, current_path, ed, az)


def _process_list_value(
    current_path: str,
    value: list[Any],
    ed: ExtractedData,
    az: Analyzers,
) -> int:
    """Process a list value."""

    az.array_analyzer.collect_one(current_path, len(value))

    item_path = f"{current_path}[]"
    data_point_count = 0

    for item in value:
        data_point_count += _process_list_item(item_path, item, ed, az)

    return data_point_count


def _process_list_item(item_path: str, item: Any, ed: ExtractedData, az: Analyzers) -> int:
    """Process a single list item."""
    if isinstance(item, dict):
        # Track that this parent path (list item) contains objects
        ed.parent_presence[item_path] += 1
        return _extract_object_data(item, item_path, ed, az)

    # For non-object lists, track the item values
    ed.field_paths.add(item_path)
    if item is None:
        ed.field_null_counts[item_path] += 1
    elif isinstance(item, SimpleType):
        ed.field_value_counts[item_path][item] += 1
    ed.field_presence[item_path] += 1
    return 0  # Don't count list items as separate data points
