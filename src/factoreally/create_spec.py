"""Sample data analysis for factory spec generation.

This module analyzes sample data to generate detailed statistical specifications
that enable the creation of realistic test data factories.

The analysis examines field presence rates, value distributions, patterns, and
statistical properties to create factory specifications.
"""

from collections.abc import Iterable
from typing import Any

import click
from pydantic import BaseModel

from factoreally.analyzers import Analyzers
from factoreally.extract import extract_data
from factoreally.json_spec import build_json_spec


def create_spec(items: Iterable[dict[str, Any]], *, model: type[BaseModel] | None = None) -> dict[str, Any]:
    """Create a factory spec from sample data.

    Orchestrates sample data analysis using specialized analyzers
    to perform analysis of sample data and generate realistic
    factory specifications.

    Args:
        items: List of sample data items to analyze
        model: Optional Pydantic model to detect dynamic object fields

    Returns:
        Dict containing the complete factory spec with metadata and field definitions
    """

    # Convert items to list if it's not already to get length for progress bar
    if not isinstance(items, list):
        items = list(items)

    az = Analyzers()

    with click.progressbar(
        items,
        label="(1/3) Processing items",
        show_eta=True,
        show_percent=True,
        show_pos=True,
    ) as progress_items:
        extracted = extract_data(progress_items, az=az, model=model)

    with click.progressbar(
        length=(
            len(extracted.field_value_counts)
            + len(az.array_analyzer.array_fields)
            + len(az.object_analyzer.dynamic_object_fields)
        ),
        label="(2/3) Analysis",
        show_eta=True,
        show_percent=True,
        show_pos=True,
    ) as bar:
        for field in az.object_analyzer.dynamic_object_fields:
            az.object_analyzer.analyze_field(field)
            bar.update(1)

        for field in az.array_analyzer.array_fields:
            az.array_analyzer.analyze_field(field)
            bar.update(1)

        for field, value_counts in extracted.field_value_counts.items():
            if not az.numeric_analyzer.analyze_field_value_counts(field, value_counts):
                az.string_pattern_analyzer.analyze_field_value_counts(field, value_counts)
            bar.update(1)

    field_count = len(extracted.field_paths)
    with click.progressbar(
        length=field_count,
        label="(3/3) Building spec",
        show_eta=True,
        show_percent=True,
        show_pos=True,
    ) as bar:
        return build_json_spec(extracted, az, progress_callback=bar.update)
