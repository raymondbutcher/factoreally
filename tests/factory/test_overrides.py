"""Tests for Factory override functionality (static and callable)."""

from typing import Any

import pytest

from factoreally import Factory


def test_build_with_overrides(simple_factory_spec: Factory) -> None:
    """Test Factory.build with override arguments."""
    factory = simple_factory_spec

    # Test build with dict override
    data1 = factory.build({"id": "override-id", "data.count": 999})
    assert data1["id"] == "override-id"
    assert data1["data"]["count"] == 999

    # Test build with keyword overrides
    data2 = factory.build(name="keyword-name", data__count=777)
    assert data2["name"] == "keyword-name"
    assert data2["data"]["count"] == 777

    # Test build with both dict and keyword overrides (keyword should take precedence)
    data3 = factory.build({"name": "dict-name"}, name="keyword-name")
    assert data3["name"] == "keyword-name"


def test_callable_override_no_args() -> None:
    """Test callable override with no arguments."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "original"}},
            "id": {"CONST": {"val": "123"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test with lambda that takes no arguments
    result = factory.build(name=lambda: "generated_value")
    assert result["name"] == "generated_value"
    assert result["id"] == "123"  # Other fields unchanged


def test_callable_override_one_arg_value() -> None:
    """Test callable override with one argument (field value)."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "john"}},
            "count": {"CONST": {"val": 42}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test with lambda that transforms the field value
    result = factory.build(name=lambda value: value.upper())
    assert result["name"] == "JOHN"
    assert result["count"] == 42

    # Test with lambda that doubles a number
    result2 = factory.build(count=lambda value: value * 2)
    assert result2["count"] == 84
    assert result2["name"] == "john"


def test_callable_override_two_args_value_obj() -> None:
    """Test callable override with two arguments (field value, entire object)."""
    spec_data = {
        "fields": {
            "first_name": {"CONST": {"val": "john"}},
            "last_name": {"CONST": {"val": "doe"}},
            "full_name": {"CONST": {"val": "placeholder"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test with lambda that uses both field value and entire object
    result = factory.build(full_name=lambda _value, obj: f"{obj['first_name']} {obj['last_name']}")
    assert result["full_name"] == "john doe"
    assert result["first_name"] == "john"
    assert result["last_name"] == "doe"

    # Test override that modifies based on both value and object
    result2 = factory.build(first_name=lambda value, obj: f"{value}_{obj['last_name']}_modified")
    assert result2["first_name"] == "john_doe_modified"


def test_callable_override_keyword_only() -> None:
    """Test callable override with keyword-only parameters."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "alice"}},
            "role": {"CONST": {"val": "admin"}},
            "display": {"CONST": {"val": "placeholder"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test with keyword-only 'value' parameter
    result = factory.build(name=lambda *, value: f"Mr. {value}")
    assert result["name"] == "Mr. alice"

    # Test with keyword-only 'obj' parameter
    result2 = factory.build(display=lambda *, obj: f"{obj['name']} ({obj['role']})")
    assert result2["display"] == "alice (admin)"

    # Test with both keyword-only parameters
    result3 = factory.build(display=lambda *, value, obj: f"{value} -> {obj['name']} as {obj['role']}")
    assert result3["display"] == "placeholder -> alice as admin"


def test_callable_override_nested_fields() -> None:
    """Test callable override with nested field paths."""
    spec_data = {
        "fields": {
            "user.name": {"CONST": {"val": "bob"}},
            "user.age": {"CONST": {"val": 30}},
            "metadata.count": {"CONST": {"val": 5}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test nested field override with callable
    result = factory.build(user__name=lambda value: f"Dr. {value}")
    assert result["user"]["name"] == "Dr. bob"
    assert result["user"]["age"] == 30

    # Test nested field using entire object
    result2 = factory.build(metadata__count=lambda value, obj: obj["user"]["age"] + value)
    assert result2["metadata"]["count"] == 35  # 30 + 5


def test_callable_override_array_elements() -> None:
    """Test callable override with array field paths."""
    spec_data = {
        "metadata": {},
        "fields": {
            "items": {
                "ARRAY": {},
                "NUMBER": {"min": 2, "max": 2},  # Exactly 2 elements
            },
            "items[].name": {"CONST": {"val": "item"}},
            "items[].value": {"CONST": {"val": 10}},
        },
    }
    factory = Factory(spec_data)

    # Test array element override with callable
    result = factory.build(items__0__name=lambda value: f"first_{value}")
    assert result["items"][0]["name"] == "first_item"
    assert result["items"][1]["name"] == "item"  # Unchanged

    # Test array element using entire object
    result2 = factory.build(items__1__value=lambda value, obj: len(obj["items"]) * value)
    assert result2["items"][1]["value"] == 20  # 2 * 10


def test_callable_override_mixed_with_static() -> None:
    """Test mix of callable and static overrides."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "original"}},
            "count": {"CONST": {"val": 1}},
            "flag": {"CONST": {"val": False}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Mix callable and static overrides
    result = factory.build(
        name=lambda value: value.upper(),
        count=100,  # Static override
        flag=lambda: True,  # Callable with no args
    )

    assert result["name"] == "ORIGINAL"
    assert result["count"] == 100
    assert result["flag"] is True


def test_callable_override_invalid_signatures() -> None:
    """Test error handling for invalid callable signatures."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "test"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test too many positional parameters
    def invalid_too_many_args(_a: Any, _b: Any, _c: Any) -> str:
        return "invalid"

    with pytest.raises(TypeError, match="too many positional parameters"):
        factory.build(name=invalid_too_many_args)

    # Test unknown keyword parameter
    def invalid_keyword_param(*, _unknown_param: Any) -> str:
        return "invalid"

    with pytest.raises(TypeError, match="Unknown keyword parameter"):
        factory.build(name=invalid_keyword_param)


def test_callable_override_copy_method() -> None:
    """Test callable overrides work with Factory.copy() method."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "base"}},
            "suffix": {"CONST": {"val": "_default"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Create copy with callable override
    factory_copy = factory.copy(name=lambda value: f"{value}_modified")
    result = factory_copy.build()

    assert result["name"] == "base_modified"
    assert result["suffix"] == "_default"

    # Original factory unchanged
    original_result = factory.build()
    assert original_result["name"] == "base"


def test_callable_override_error_handling() -> None:
    """Test error handling when callables raise exceptions."""
    spec_data = {
        "fields": {
            "name": {"CONST": {"val": "test"}},
        },
        "metadata": {},
    }
    factory = Factory(spec_data)

    # Test callable that raises exception
    def failing_callable(_value: Any) -> str:
        error_msg = "Intentional error"
        raise ValueError(error_msg)

    with pytest.raises(ValueError, match="Intentional error"):
        factory.build(name=failing_callable)


def test_override_simple_nested_fields() -> None:
    """Test overriding simple nested fields without arrays."""
    spec_data = {
        "metadata": {
            "samples_analyzed": 10,
        },
        "fields": {
            "data.patient.id": {"CONST": {"val": "pat123"}},
            "data.physician": {"CONST": {"val": "dr456"}},
        },
    }

    factory = Factory(spec_data)

    # Test generating base data
    data = factory.build()
    assert "data" in data
    assert data["data"]["patient"]["id"] == "pat123"
    assert data["data"]["physician"] == "dr456"

    # Test override nested field
    data_override = factory.build(data__patient__id="override123")
    assert data_override["data"]["patient"]["id"] == "override123"
    assert data_override["data"]["physician"] == "dr456"  # Unchanged
