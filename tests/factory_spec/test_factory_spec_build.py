"""Tests for FactorySpec.build method."""

from typing import TYPE_CHECKING

from factoreally.factory_spec import FactorySpec
from factoreally.hints import ArrayHint, ChoiceHint, ConstantValueHint, NumberHint

if TYPE_CHECKING:
    from factoreally.hints.base import AnalysisHint


def test_factory_spec_build_simple() -> None:
    """Test building simple values from FactorySpec."""
    field_hints: dict[str, list[AnalysisHint]] = {
        "name": [ConstantValueHint(val="Alice")],
    }

    factory_spec = FactorySpec(field_hints)
    result = factory_spec.build()

    assert result == {"name": "Alice"}


def test_factory_spec_build_with_choice() -> None:
    """Test building with choice hints."""
    field_hints: dict[str, list[AnalysisHint]] = {
        "status": [ChoiceHint(type="CHOICE", choices=["A", "B"], weights=[50.0, 50.0])],
    }

    factory_spec = FactorySpec(field_hints)
    result = factory_spec.build()

    assert "status" in result
    assert result["status"] in ["A", "B"]


def test_factory_spec_build_nested_object() -> None:
    """Test building nested objects."""
    field_hints: dict[str, list[AnalysisHint]] = {
        "user.name": [ConstantValueHint(val="Alice")],
        "user.age": [ConstantValueHint(val=30)],
    }

    factory_spec = FactorySpec(field_hints)
    result = factory_spec.build()

    assert result == {"user": {"name": "Alice", "age": 30}}


def test_factory_spec_build_empty_fields() -> None:
    """Test FactorySpec with no fields."""
    field_hints: dict[str, list[AnalysisHint]] = {}

    factory_spec = FactorySpec(field_hints)
    result = factory_spec.build()

    assert result is None


def test_factory_spec_build_minimal_array() -> None:
    """Test that a minimal array field with element definition can be created without recursion."""
    field_path_hints: dict[str, list[AnalysisHint]] = {
        "actions": [ArrayHint(type="ARRAY"), NumberHint(type="NUMBER", min=1, max=3)],
        "actions[]": [ChoiceHint(type="CHOICE", choices=["A", "B"], weights=[0.5, 0.5])],
    }

    # Should create without recursion
    spec = FactorySpec(field_path_hints)
    assert spec is not None

    # The parsing logic should work correctly - we can test that building works
    result = spec.build()
    assert result is not None


def test_factory_spec_build_minimal_array_no_recursion() -> None:
    """Test that a minimal array field can be built without infinite recursion."""
    field_path_hints: dict[str, list[AnalysisHint]] = {
        "actions": [ArrayHint(type="ARRAY"), NumberHint(type="NUMBER", min=1, max=3)],
        "actions[]": [ChoiceHint(type="CHOICE", choices=["A", "B"], weights=[0.5, 0.5])],
    }

    spec = FactorySpec(field_path_hints)

    # Should build without recursion
    result = spec.build()

    # Should have actions as a key
    assert list(result.keys()) == ["actions"]

    # Actions should be a list (since it's an array field)
    actions = result["actions"]
    assert isinstance(actions, list)
    assert len(actions) >= 1  # At least 1 element (could be 1, 2, or 3)
    assert len(actions) <= 3  # At most 3 elements

    # Each element should be one of the choices
    for action in actions:
        assert action in ["A", "B"]
