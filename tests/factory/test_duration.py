"""Tests for Factory duration functionality."""

import re
from unittest.mock import ANY

from factoreally import Factory


def test_factory_dynamic_duration_spec() -> None:
    """Test Factory with dynamic duration spec using HMS format."""
    spec = {
        "metadata": {
            "samples_analyzed": 2,
            "unique_fields": 3,
            "total_data_points": 11,
        },
        "fields": {
            "hourlyMetrics": {
                "OBJECT": {},
                "NUMBER": {"min": 3, "max": 4},
                "DURATION": {"min": 32400, "max": 54000, "avg": 43200.0, "fmt": "HMS"},
            },
            "hourlyMetrics.{}": {
                "NUMBER": {"min": 95, "max": 125},
            },
            "name": {
                "CHOICE": {
                    "choices": ["Report A", "Report B"],
                    "weights": [0.5, 0.5],
                },
            },
        },
    }
    fact = Factory(spec)

    result = fact.build()

    assert result == {
        "hourlyMetrics": ANY,
        "name": ANY,
    }

    assert len(result["hourlyMetrics"]) >= 3
    assert len(result["hourlyMetrics"]) <= 4

    for key, value in result["hourlyMetrics"].items():
        # The key should match the HMS pattern format from string_pattern_analyzer.py
        assert re.match(r"^(\d{1,2}):(\d{2}):(\d{2})$", key)
        assert value >= 95
        assert value <= 125


def test_factory_dynamic_duration_dhms_spec() -> None:
    """Test Factory with dynamic duration spec using D.HMS format."""
    spec = {
        "metadata": {
            "samples_analyzed": 2,
            "unique_fields": 3,
            "total_data_points": 11,
        },
        "fields": {
            "processMetrics": {
                "OBJECT": {},
                "NUMBER": {"min": 2, "max": 5},
                "DURATION": {"min": 93845, "max": 308720, "avg": 201282.5, "fmt": "D.HMS"},
            },
            "processMetrics.{}": {
                "NUMBER": {"min": 50, "max": 200},
            },
            "name": {
                "CHOICE": {
                    "choices": ["Process A", "Process B"],
                    "weights": [0.5, 0.5],
                },
            },
        },
    }
    fact = Factory(spec)

    result = fact.build()

    assert result == {
        "processMetrics": ANY,
        "name": ANY,
    }

    assert len(result["processMetrics"]) >= 2
    assert len(result["processMetrics"]) <= 5

    for key, value in result["processMetrics"].items():
        # The key should match the D.HMS pattern format (days.hours:minutes:seconds)
        assert re.match(r"^(\d+)\.(\d{1,2}):(\d{2}):(\d{2})$", key)
        assert value >= 50
        assert value <= 200


def test_factory_dynamic_duration_dhms_fractional_spec() -> None:
    """Test Factory with dynamic duration spec using D.HMS.F format (fractional seconds)."""
    spec = {
        "metadata": {
            "samples_analyzed": 3,
            "unique_fields": 3,
            "total_data_points": 15,
        },
        "fields": {
            "precisionMetrics": {
                "OBJECT": {},
                "NUMBER": {"min": 3, "max": 6},
                "DURATION": {"min": 127460.9074178, "max": 522720.123456, "avg": 325090.515437, "fmt": "D.HMS.F"},
            },
            "precisionMetrics.{}": {
                "NUMBER": {"min": 75, "max": 300},
            },
            "name": {
                "CHOICE": {
                    "choices": ["Precision Task A", "Precision Task B", "Precision Task C"],
                    "weights": [0.4, 0.3, 0.3],
                },
            },
        },
    }
    fact = Factory(spec)

    result = fact.build()

    assert result == {
        "precisionMetrics": ANY,
        "name": ANY,
    }

    assert len(result["precisionMetrics"]) >= 3
    assert len(result["precisionMetrics"]) <= 6

    for key, value in result["precisionMetrics"].items():
        # The key should match the D.HMS.F pattern format (days.hours:minutes:seconds.fractional)
        assert re.match(r"^(\d+)\.(\d{1,2}):(\d{2}):(\d{2})\.(\d+)$", key)
        assert value >= 75
        assert value <= 300
