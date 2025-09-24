"""Tests for Factory integration and complex scenarios."""

from datetime import date
from typing import Any

from pydantic import BaseModel

from factoreally import Factory
from factoreally.create_spec import create_spec


def test_integration_all_features(simple_factory_spec: Factory) -> None:
    """Integration test using all Factory features together."""
    # Create base factory with overrides
    base_factory = simple_factory_spec
    factory_with_base = base_factory.copy(name="base")

    # Create copy with additional overrides
    copy_factory = factory_with_base.copy(id="copy-id")

    # Use slice to generate multiple items
    items = copy_factory[0:3]

    # Verify all features work together
    assert len(items) == 3
    for item in items:
        assert item["name"] == "base"  # Base override
        assert item["id"] == "copy-id"  # Copy override
        assert isinstance(item["data"]["count"], int)  # Generated field

    # Use iterator to generate more items
    iterator_items = []
    for i, item in enumerate(copy_factory):
        iterator_items.append(item)
        if i >= 1:
            break

    assert len(iterator_items) == 2
    for item in iterator_items:
        assert item["name"] == "base"
        assert item["id"] == "copy-id"


def test_pydantic_model_integration() -> None:
    """Test integration of Pydantic model analysis with create_spec."""

    class Nested(BaseModel):
        height: int

    class ElementModel(BaseModel):
        age: int

    class TestModel(BaseModel):
        name: str
        dynamic: dict[str, str] | None  # Dynamic object field
        nested: Nested | None  # Static object field
        elements: list[ElementModel] | None  # Dynamic array field

    # Sample data matching the model structure
    sample_data: list[dict[str, Any]] = [
        {
            "name": "Alice",
            "dynamic": {
                "e4275a86-217f-4c61-ac95-351cb3b5e7fc": "value1",
                "95fb5453-90db-4b24-a126-8bc71eb1a26a": "value2",
            },
            "nested": {"height": 160},
            "elements": [{"age": 20}, {"age": 25}],
        },
        {
            "name": "Bob",
            "dynamic": {
                "6b172048-eab7-492d-a29f-c187288a387d": "value3",
                "7decd856-c6c4-420a-9504-4bd873dee0da": "value4",
                "17673e9d-feb8-4951-8f45-c1721dca1a8d": "value5",
            },
            "nested": {"height": 170},
            "elements": [{"age": 22}, {"age": 26}],
        },
        {
            "name": "Carol",
        },
        {
            "name": "Jan",
            "dynamic": None,
            "nested": None,
            "elements": None,
        },
    ]

    # Create spec with Pydantic model
    spec = create_spec(sample_data, model=TestModel)

    # Assert the complete spec structure
    expected_spec = {
        "fields": {
            "dynamic": {
                "OBJECT": {},
                "NUMBER": {"min": 2, "max": 3},
                "UUID4": {},
                "NULL": {"pct": 33.333},
                "MISSING": {"pct": 25.0},
            },
            "dynamic.{}": {
                "CHOICE": {
                    "choices": ["value1", "value2", "value3", "value4", "value5"],
                    "weights": [0.2, 0.2, 0.2, 0.2, 0.2],
                },
            },
            "elements": {
                "ARRAY": {},
                "NUMBER": {"min": 2, "max": 2},
                "NULL": {"pct": 33.333},
                "MISSING": {"pct": 25.0},
            },
            "elements[].age": {"NUMBER": {"min": 20, "max": 26}},
            "name": {"CHOICE": {"choices": ["Alice", "Bob", "Carol", "Jan"], "weights": [0.25, 0.25, 0.25, 0.25]}},
            "nested": {"NULL": {"pct": 33.333}, "MISSING": {"pct": 25.0}},
            "nested.height": {"NUMBER": {"min": 160, "max": 170}},
        },
        "metadata": {
            "samples_analyzed": 4,
            "total_data_points": 24,
            "unique_fields": 7,
        },
    }

    assert spec == expected_spec

    # Additional specific assertions for clarity
    dynamic_field_spec = spec["fields"]["dynamic"]

    # Dynamic field should have OBJECT hint (marker), NUMBER hint (for key count), NULL and MISSING hints
    assert "OBJECT" in dynamic_field_spec
    assert "NUMBER" in dynamic_field_spec
    assert "NULL" in dynamic_field_spec  # Jan has explicit None
    assert "MISSING" in dynamic_field_spec  # Carol is missing the field

    # The NUMBER hint should reflect the key count distribution (2-3 keys)
    dynamic_number_spec = dynamic_field_spec["NUMBER"]
    assert dynamic_number_spec["min"] == 2
    assert dynamic_number_spec["max"] == 3


def test_dynamic_object_with_date_string_keys() -> None:
    """Test dynamic objects where keys are dates and spec contains '{}' suffix."""

    class DailyMetrics(BaseModel):
        total_users: int

    class TestModel(BaseModel):
        name: str
        daily_metrics: dict[str, DailyMetrics]  # Dynamic object with date keys

    # Sample data with date keys
    sample_data = [
        {
            "name": "Report A",
            "daily_metrics": {
                "2025-01-05": {"total_users": 100},
                "2025-01-06": {"total_users": 120},
                "2025-01-07": {"total_users": 110},
            },
        },
        {
            "name": "Report B",
            "daily_metrics": {
                "2025-01-08": {"total_users": 95},
                "2025-01-09": {"total_users": 105},
                "2025-01-10": {"total_users": 125},
                "2025-01-11": {"total_users": 115},
            },
        },
    ]

    # Create spec with the model
    spec = create_spec(sample_data, model=TestModel)

    # Assert the complete spec structure
    expected_spec = {
        "metadata": {
            "samples_analyzed": 2,
            "unique_fields": 4,
            "total_data_points": 18,
        },
        "fields": {
            "daily_metrics": {
                "OBJECT": {},
                "NUMBER": {"min": 3, "max": 4},
                "DATE": {"min": "2025-01-05", "max": "2025-01-11"},
            },
            "daily_metrics.{}.total_users": {
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

    assert spec == expected_spec


def test_dynamic_object_with_date_keys() -> None:
    """Test dynamic objects where keys are dates using dict[date, T] annotation."""

    class DailyMetrics(BaseModel):
        total_users: int

    class TestModel(BaseModel):
        name: str
        daily_metrics: dict[date, DailyMetrics]  # Dynamic object with date keys, using date type annotation

    # Sample data with date keys
    sample_data = [
        {
            "name": "Report A",
            "daily_metrics": {
                "2025-01-05": {"total_users": 100},
                "2025-01-06": {"total_users": 120},
                "2025-01-07": {"total_users": 110},
            },
        },
        {
            "name": "Report B",
            "daily_metrics": {
                "2025-01-08": {"total_users": 95},
                "2025-01-09": {"total_users": 105},
                "2025-01-10": {"total_users": 125},
                "2025-01-11": {"total_users": 115},
            },
        },
    ]

    # Create spec with the model
    spec = create_spec(sample_data, model=TestModel)

    # Assert the complete spec structure
    expected_spec = {
        "metadata": {
            "samples_analyzed": 2,
            "unique_fields": 4,
            "total_data_points": 18,
        },
        "fields": {
            "daily_metrics": {
                "OBJECT": {},
                "NUMBER": {"min": 3, "max": 4},
                "DATE": {"min": "2025-01-05", "max": "2025-01-11"},
            },
            "daily_metrics.{}.total_users": {
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

    assert spec == expected_spec


def test_complex_nested_dynamic_date_keys_with_aliases() -> None:
    """Test complex nested structures with dynamic date keys and model aliases."""

    class UserProfile(BaseModel):
        name: str
        age: int

    class ActionData(BaseModel):
        action_type: str = "default"
        timestamp: str = "2024-01-01T00:00:00Z"

    class TestModel(BaseModel):
        user: UserProfile
        daily_actions: dict[str, list[ActionData]]  # Dynamic date keys with arrays

    # Sample data with complex nested dynamic structure
    sample_data = [
        {
            "user": {"name": "Alice", "age": 30},
            "daily_actions": {
                "2025-01-05": [
                    {"action_type": "login", "timestamp": "2025-01-05T09:00:00Z"},
                    {"action_type": "view", "timestamp": "2025-01-05T09:15:00Z"},
                ],
                "2025-01-06": [
                    {"action_type": "logout", "timestamp": "2025-01-06T17:00:00Z"},
                ],
            },
        },
        {
            "user": {"name": "Bob", "age": 25},
            "daily_actions": {
                "2025-01-07": [
                    {"action_type": "login", "timestamp": "2025-01-07T08:30:00Z"},
                    {"action_type": "edit", "timestamp": "2025-01-07T10:00:00Z"},
                    {"action_type": "save", "timestamp": "2025-01-07T10:05:00Z"},
                ],
            },
        },
    ]

    # Create spec with the model
    spec = create_spec(sample_data, model=TestModel)

    # Verify the dynamic object structure is correctly identified
    daily_actions_spec = spec["fields"]["daily_actions"]
    assert "OBJECT" in daily_actions_spec  # Dynamic object marker
    assert "NUMBER" in daily_actions_spec  # Key count
    assert "DATE" in daily_actions_spec  # Date pattern for keys

    # Verify the nested array structure within dynamic keys
    assert "daily_actions.{}[].action_type" in spec["fields"]
    assert "daily_actions.{}[].timestamp" in spec["fields"]

    # Check the generated factory works
    factory = Factory(spec)
    result = factory.build()

    assert "user" in result
    assert "daily_actions" in result
    assert isinstance(result["daily_actions"], dict)

    # Check that keys follow date pattern and values are arrays
    for key, value in result["daily_actions"].items():
        assert isinstance(key, str)  # Date string
        assert isinstance(value, list)  # Array of actions
        if value:  # If not empty
            assert "action_type" in value[0]
            assert "timestamp" in value[0]
