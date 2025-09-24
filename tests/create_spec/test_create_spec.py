"""Tests for create_spec function."""

from datetime import UTC, datetime, timedelta
from typing import Any

from factoreally.create_spec import create_spec


def test_create_spec_empty_list() -> None:
    """Test create_spec with empty list data."""
    sample_data: list[dict[Any, Any]] = [
        {"timestamps": []},
    ]

    spec_data = create_spec(sample_data)

    assert spec_data == {
        "metadata": {
            "samples_analyzed": 1,
            "total_data_points": 1,
            "unique_fields": 1,
        },
        "fields": {
            "timestamps": {
                "ARRAY": {},
                "NUMBER": {"min": 0, "max": 0},
            },
        },
    }


def test_create_spec_list_timestamps() -> None:
    """Test create_spec with timestamp list data."""
    start = datetime.now(tz=UTC)
    middle = start + timedelta(days=1)
    end = middle + timedelta(days=1)

    sample_data = [
        {"timestamps": [start.isoformat(), middle.isoformat(), end.isoformat()]},
        {"timestamps": [start.isoformat(), end.isoformat()]},
        {},
    ]

    spec_data = create_spec(sample_data)

    assert spec_data == {
        "metadata": {
            "samples_analyzed": 3,
            "total_data_points": 2,
            "unique_fields": 2,
        },
        "fields": {
            "timestamps": {
                "ARRAY": {},
                "NUMBER": {
                    "min": 2,
                    "max": 3,
                },
                "MISSING": {
                    "pct": 33.333,
                },
            },
            "timestamps[]": {
                "DATETIME": {
                    "min": start.isoformat(),
                    "max": end.isoformat(),
                },
            },
        },
    }


def test_create_spec_nested_objects() -> None:
    """Test create_spec with nested object data."""
    sample_data: list[dict[str, Any]] = [
        {},
        {"data": None},
        {"data": {}},
        {"data": {"topList": None}},
        {"data": {"topList": []}},
        {"data": {"topList": [{}]}},
        {"data": {"topList": [{"nestedList": None}]}},
        {"data": {"topList": [{"nestedList": []}]}},
    ]

    spec_data = create_spec(sample_data)

    assert spec_data == {
        "metadata": {
            "samples_analyzed": 8,
            "total_data_points": 14,
            "unique_fields": 3,
        },
        "fields": {
            "data": {
                "NULL": {"pct": 14.286},
                "MISSING": {"pct": 12.5},
            },
            "data.topList": {
                "ARRAY": {},
                "NUMBER": {"min": 0, "max": 1},
                "NULL": {"pct": 20.0},
                "MISSING": {"pct": 16.667},
            },
            "data.topList[].nestedList": {
                "ARRAY": {},
                "NUMBER": {"min": 0, "max": 0},
                "NULL": {"pct": 50.0},
                "MISSING": {"pct": 33.333},
            },
        },
    }
