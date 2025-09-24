"""Tests for Factory array-related functionality."""

import pytest

from factoreally import Factory
from factoreally.hints.base import NULL


def test_array_override_bug_nested_field_setting() -> None:
    """Test bug where overriding nested fields under an array fails.

    This reproduces the bug described in the root cause analysis:
    - Override path: "data__actions__data__patient__id"
    - Data structure: data.actions is an array
    - Expected behavior: Set data.patient.id on all elements in the actions array
    - Actual behavior: TypeError: list indices must be integers or slices, not str
    """
    # Create spec data that matches the bug scenario
    spec_data = {
        "metadata": {
            "generated": "2024-01-01T00:00:00Z",
            "samples_analyzed": 100,
        },
        "fields": {
            "data.actions": {
                "ARRAY": {},
                "NUMBER": {"min": 2, "max": 2},  # Always 2 elements
            },
            "data.actions[].data.patient.id": {"UUID4": {}},
            "data.actions[].data.patient.name": {"ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5]}}},
            "data.actions[].type": {"CONST": {"val": "action"}},
        },
    }

    factory = Factory(spec_data)

    # This should work without the bug - setting on all array elements
    # The bug occurs because _set_nested_value tries to do current["data"]
    # where current is the actions array (a list), not a dict

    # Generate base data first to see what we're working with
    base_data = factory.build()
    assert "data" in base_data
    assert "actions" in base_data["data"]
    assert isinstance(base_data["data"]["actions"], list)
    assert len(base_data["data"]["actions"]) == 2

    # Verify the structure exists before override
    for action in base_data["data"]["actions"]:
        assert "data" in action
        assert "patient" in action["data"]
        assert "id" in action["data"]["patient"]
        assert "name" in action["data"]["patient"]
        assert "type" in action

    # This should set patient.id to "fixed-id" on ALL elements in the actions array
    # But currently fails with: TypeError: list indices must be integers or slices, not str
    override_data = factory.build(data__actions__data__patient__id="fixed-id")

    # If the bug is fixed, this should work and set the ID on all action elements
    assert "data" in override_data
    assert "actions" in override_data["data"]
    assert isinstance(override_data["data"]["actions"], list)
    assert len(override_data["data"]["actions"]) == 2

    # Both actions should have the overridden patient ID
    for action in override_data["data"]["actions"]:
        assert action["data"]["patient"]["id"] == "fixed-id"
        # Other fields should still be generated normally
        assert action["data"]["patient"]["name"] != "fixed-id"
        assert action["type"] == "action"


def test_array_override_multiple_nested_fields() -> None:
    """Test setting multiple nested fields under an array to verify comprehensive fix."""
    spec_data = {
        "metadata": {
            "generated": "2024-01-01T00:00:00Z",
            "samples_analyzed": 100,
        },
        "fields": {
            "data.actions": {
                "ARRAY": {},
                "NUMBER": {"min": 1, "max": 2},
            },
            "data.actions[].data.patient.id": {"UUID4": {}},
            "data.actions[].data.patient.name": {"ALPHA": {"chrs": {"ABCDEFGHIJKLMNOPQRSTUVWXYZ": [0, 1, 2, 3, 4, 5]}}},
            "data.actions[].data.device.model": {"CONST": {"val": "M2000"}},
            "data.actions[].type": {"CONST": {"val": "action"}},
        },
    }

    factory = Factory(spec_data)

    # This should set multiple nested fields on all array elements
    override_data = factory.build(
        data__actions__data__patient__id="patient-123",
        data__actions__data__patient__name="John Doe",
        data__actions__data__device__model="M3000",
    )

    # Verify all overrides applied to all array elements
    for action in override_data["data"]["actions"]:
        assert action["data"]["patient"]["id"] == "patient-123"
        assert action["data"]["patient"]["name"] == "John Doe"
        assert action["data"]["device"]["model"] == "M3000"
        assert action["type"] == "action"  # Non-overridden field


def test_array_nested_override_with_null_values() -> None:
    """Test array override behavior with None values in nested structures.

    This test reproduces the TypeError that occurs when trying to set a nested value
    through an array using double underscore notation (data__actions__data__patient__id)
    when some array elements have None values in the nested structure.

    The bug manifests when:
    1. An array exists (data.actions)
    2. Array elements have nested None values (data.actions[].data = None)
    3. An override tries to set a value deeper in the structure (data__actions__data__patient__id)

    This should gracefully handle None values by skipping assignment.
    """
    # Minimal spec that reproduces the exact bug scenario
    spec_data = {
        "fields": {
            "data.actions": {
                "ARRAY": {},
                "NUMBER": {"min": 1, "max": 1},  # Exactly 1 element for reproducibility
            },
            "data.actions[].data": {
                "NULL": {"pct": 99.9999999999999999}  # Practically always None - this triggers the bug
            },
            "data.actions[].data.id": {"CONST": {"val": "test"}},
        }
    }

    factory = Factory(spec_data)

    # This should gracefully handle None values by skipping assignment
    # rather than throwing TypeError
    result = factory.build(data__actions__data__id="ABC")

    # Verify the structure is correct and override was gracefully skipped
    assert "data" in result
    assert "actions" in result["data"]
    assert len(result["data"]["actions"]) == 1
    # The data field should be None (due to NULL hint), so override should be skipped
    assert result["data"]["actions"][0]["data"] is None


def test_build_null_hint_with_child_fields_in_array() -> None:
    """Test that Factory with NULL hint works correctly with child fields inside array elements."""
    spec_data = {
        "metadata": {
            "samples_analyzed": 10,
        },
        "fields": {
            "data.actions": {"ARRAY": {}, "NUMBER": {"min": 1, "max": 1}},
            "data.actions[].data.wand": {"NULL": {"pct": 100.0}},
            "data.actions[].data.wand.model": {"CONST": {"val": "M2000"}},
        },
    }

    factory = Factory(spec_data)

    # Test multiple times to ensure consistency
    for _ in range(10):
        result = factory.build()
        assert "data" in result
        assert "actions" in result["data"]
        assert len(result["data"]["actions"]) == 1

        action = result["data"]["actions"][0]
        assert "data" in action
        assert "wand" in action["data"]
        assert action["data"]["wand"] is None


def test_build_null_dynamic_object() -> None:
    """Test Factory build with null hint on dynamic object field."""
    spec = {
        "metadata": {},
        "fields": {
            "dynamic_object": {
                "OBJECT": {},
                "NUMBER": {"min": 100, "max": 100},
                "DURATION": {"fmt": "HMS", "min": 0, "max": 82800, "avg": 41400.0},
                "NULL": {"pct": 50.0},
            },
            "dynamic_object.{}": {"CONST": {"val": 0}},
        },
    }
    factory = Factory(spec)

    # The null hint on "dynamic_object" means it will sometimes be null,
    # in which case we won't be able to see the bug. Loop until we get
    # a case where it is not null, and then we'll see the bug.
    for _ in range(100):
        result = factory.build()
        if result["dynamic_object"] is not None:
            break
    else:
        pytest.skip("did not trigger the bug this time")

    # Now we should be able to see the bug. There will be a 50% chance when
    # generating a key that it is the factoreally.hints.base.NULL sentinel.
    # This is a bug because the NULL hint was on the dynamic_object field
    # itself, not on the value hint. The NULL hint on the dynamic_object
    # field should only be used to make dynamic_object sometimes null.
    # It should not be used when generating dynamic keys.
    assert NULL not in result["dynamic_object"]
