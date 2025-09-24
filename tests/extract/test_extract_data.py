"""Tests for extract_data function."""

from typing import Any

from factoreally.analyzers import Analyzers
from factoreally.extract import extract_data


def test_extract_data_empty_input() -> None:
    """Test extraction from empty data."""
    result = extract_data([], az=Analyzers(), model=None)

    assert result.item_count == 0
    assert result.data_point_count == 0
    assert len(result.field_paths) == 0
    assert len(result.field_presence) == 0


def test_extract_data_simple_objects() -> None:
    """Test extraction from simple dictionary objects."""
    items: list[dict[str, Any]] = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie"},  # Missing age
    ]

    result = extract_data(items, az=Analyzers(), model=None)

    assert result.item_count == 3
    assert result.data_point_count > 0
    assert "name" in result.field_paths
    assert "age" in result.field_paths
    assert result.field_presence["name"] == 3  # Present in all items
    assert result.field_presence["age"] == 2  # Present in 2 items


def test_extract_data_nested_objects() -> None:
    """Test extraction from nested dictionary objects."""
    items: list[dict[str, Any]] = [
        {"user": {"name": "Alice", "profile": {"age": 30}}},
        {"user": {"name": "Bob"}},  # Missing nested profile
    ]

    result = extract_data(items, az=Analyzers(), model=None)

    assert result.item_count == 2
    assert "user" in result.field_paths
    assert "user.name" in result.field_paths
    assert "user.profile" in result.field_paths
    assert "user.profile.age" in result.field_paths
    assert result.field_presence["user"] == 2
    assert result.field_presence["user.name"] == 2
    assert result.field_presence["user.profile.age"] == 1


def test_extract_data_with_arrays() -> None:
    """Test extraction from objects containing arrays."""
    items: list[dict[str, Any]] = [
        {"tags": ["python", "testing"]},
        {"tags": ["javascript"]},
        {"tags": []},  # Empty array
    ]

    az = Analyzers()
    result = extract_data(items, az=az, model=None)

    assert result.item_count == 3
    assert "tags" in result.field_paths
    assert result.field_presence["tags"] == 3
    # Array lengths are now tracked by the ArrayAnalyzer
    assert "tags" in az.array_analyzer.field_length_counts
    assert 2 in az.array_analyzer.field_length_counts["tags"]  # Length 2 array
    assert 1 in az.array_analyzer.field_length_counts["tags"]  # Length 1 array
    assert 0 in az.array_analyzer.field_length_counts["tags"]  # Length 0 array


def test_extract_data_value_counting() -> None:
    """Test that values are counted correctly."""
    items = [
        {"status": "active"},
        {"status": "active"},
        {"status": "inactive"},
    ]

    result = extract_data(items, az=Analyzers(), model=None)

    assert "status" in result.field_value_counts
    status_counts = result.field_value_counts["status"]
    assert status_counts["active"] == 2
    assert status_counts["inactive"] == 1
