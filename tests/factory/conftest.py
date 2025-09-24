"""Shared fixtures for factory tests."""

from typing import Any

import pytest

from factoreally import Factory


@pytest.fixture
def mock_spec_data() -> dict[str, Any]:
    """Create mock spec data for testing."""
    return {
        "metadata": {
            "generated": "2024-01-01T00:00:00Z",
            "samples_analyzed": 100,
        },
        "fields": {
            "id": {"UUID4": {}},
            "name": {
                "MISSING": {"pct": 85.0},
                "ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5, 6, 7]}},
            },
            "count": {"MISSING": {"pct": 90.0}, "NUMBER": {"min": 1, "max": 100}},
            "data.id": {"UUID4": {}},
            "data.name": {"ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5]}}},
            "data.count": {"NUMBER": {"min": 10, "max": 50}},
        },
    }


@pytest.fixture
def simple_spec_data() -> dict[str, Any]:
    """Create simple spec data for testing."""
    return {
        "metadata": {
            "generated": "2024-01-01T00:00:00Z",
            "samples_analyzed": 100,
        },
        "fields": {
            "id": {"UUID4": {}},
            "name": {"ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5, 6, 7]}}},
            "data.count": {"NUMBER": {"min": 1, "max": 100}},
        },
    }


@pytest.fixture
def factory_spec(mock_spec_data: dict[str, Any]) -> Factory:
    """Create Factory instance for testing."""
    return Factory(mock_spec_data)


@pytest.fixture
def simple_factory_spec(simple_spec_data: dict[str, Any]) -> Factory:
    """Create simple Factory instance for testing."""
    return Factory(simple_spec_data)


@pytest.fixture
def mock_spec_with_array_hint() -> dict[str, Any]:
    """Create mock spec data with ArrayHint and NumberHint for array field."""
    return {
        "metadata": {
            "generated": "2024-01-01T00:00:00Z",
            "samples_analyzed": 100,
        },
        "fields": {
            "name": {"ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5, 6, 7]}}},
            "items": {
                "ARRAY": {},
                "NUMBER": {
                    "min": 3,
                    "max": 3,  # Constant length of 3
                },
            },
            "items[].id": {"UUID4": {}},
            "items[].value": {"NUMBER": {"min": 10, "max": 20}},
        },
    }


@pytest.fixture
def factory_spec_with_array_hints(mock_spec_with_array_hint: dict[str, Any]) -> Factory:
    """Create Factory instance with ArrayHint and NumberHint."""
    return Factory(mock_spec_with_array_hint)
