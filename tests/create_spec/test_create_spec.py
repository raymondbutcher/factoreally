"""Tests for create_spec function."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import ANY

from factoreally import Factory
from factoreally.cli import _json_serializer
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
            "data_points": 0,
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
            "data_points": 5,
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
            "data_points": 3,
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


def test_create_spec_normal_distribution() -> None:
    """Test create_spec with numeric data that gets fitted to a distribution."""
    sample_data = [
        {"value": 85},
        {"value": 92},
        {"value": 88},
        {"value": 105},
        {"value": 110},
        {"value": 95},
        {"value": 100},
        {"value": 98},
        {"value": 102},
        {"value": 107},
        {"value": 93},
        {"value": 97},
        {"value": 103},
        {"value": 90},
        {"value": 108},
        {"value": 96},
        {"value": 101},
        {"value": 94},
        {"value": 99},
        {"value": 104},
    ]

    spec_data = create_spec(sample_data)
    normalized_spec = json.loads(json.dumps(spec_data, default=_json_serializer))

    assert normalized_spec == {
        "metadata": {
            "samples_analyzed": 20,
            "data_points": 20,
        },
        "fields": {
            "value": {
                "NUMBER": {
                    "min": 80,
                    "max": 118,
                    "weibull": [3.815, 76.118, 24.643],
                },
            },
        },
    }

    factory = Factory(normalized_spec)
    result = factory.build()

    assert result == {"value": ANY}
