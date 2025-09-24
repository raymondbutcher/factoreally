"""Tests for base hint functionality."""

from factoreally.hints import ArrayHint, ChoiceHint, ObjectHint
from factoreally.hints.base import AnalysisHint


def test_analysis_hint_available() -> None:
    """Test that AnalysisHint class is available."""
    assert AnalysisHint is not None


def test_array_hint_basic_creation() -> None:
    """Test that ArrayHint can be created."""
    hint = ArrayHint(type="ARRAY")
    assert hint.type == "ARRAY"


def test_object_hint_basic_creation() -> None:
    """Test that ObjectHint can be created."""
    hint = ObjectHint(type="OBJECT")
    assert hint.type == "OBJECT"


def test_choice_hint_basic_creation() -> None:
    """Test that ChoiceHint can be created with choices and weights."""
    hint = ChoiceHint(type="CHOICE", choices=["A", "B"], weights=[0.5, 0.5])
    assert hint.type == "CHOICE"
    assert hint.choices == ["A", "B"]
    assert hint.weights is not None
    assert len(hint.weights) == 2


def test_choice_hint_process_value_with_none_generates_choice() -> None:
    """Test that ChoiceHint generates choice when input is None."""
    hint = ChoiceHint(type="CHOICE", choices=["X", "Y"], weights=[70.0, 30.0])

    # Test with a call_next function
    def mock_call_next(value: str) -> str:
        return value

    # The process_value should generate a choice
    result = hint.process_value(None, mock_call_next)
    assert result in ["X", "Y"]


def test_choice_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that ChoiceHint passes through existing non-None values."""
    hint = ChoiceHint(type="CHOICE", choices=["X", "Y"], weights=[70.0, 30.0])

    def mock_call_next(value: str) -> str:
        return f"processed_{value}"

    result = hint.process_value("existing_choice", mock_call_next)
    assert result == "processed_existing_choice"


def test_array_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that ArrayHint passes through existing values to call_next."""
    hint = ArrayHint(type="ARRAY")

    def mock_call_next(value: list[str]) -> list[str]:
        return value

    # Array hint should pass through to call_next
    result = hint.process_value([], mock_call_next)
    assert result == []


def test_array_hint_process_value_with_none_passes_through() -> None:
    """Test that ArrayHint passes through None values to call_next."""
    hint = ArrayHint(type="ARRAY")

    def mock_call_next(value: list[str] | None) -> list[str]:
        return [] if value is None else value

    # Array hint should pass None through to call_next
    result = hint.process_value(None, mock_call_next)
    assert result == []
