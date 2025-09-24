"""Test number string hint functionality."""

from unittest.mock import Mock

from factoreally.hints.number_string_hint import NumberStringHint


def test_number_string_hint_basic_creation() -> None:
    """Test creating a basic NumberStringHint."""
    hint = NumberStringHint(min=1, max=100)

    assert hint.type == "NUMSTR"
    assert hint.min == 1
    assert hint.max == 100


def test_number_string_hint_process_value_with_none_generates_string() -> None:
    """Test that process_value generates number string when input is None."""
    hint = NumberStringHint(min=10, max=99)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    assert result.isdigit() or (result.startswith("-") and result[1:].isdigit())

    # Should be within bounds when converted back to number
    if result.lstrip("-").isdigit():
        number_value = int(result)
        assert 10 <= number_value <= 99

    call_next.assert_called_once()


def test_number_string_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = NumberStringHint(min=1, max=10)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value("42", call_next)

    # Should pass through as-is since it's already a non-None value
    assert result == "42"
    call_next.assert_called_once_with("42")


def test_number_string_hint_converts_numbers_to_strings() -> None:
    """Test that NumberStringHint converts numeric values to strings."""
    hint = NumberStringHint(min=5, max=15)

    # Use identity call_next to get the generated value
    def identity_call_next(value: int | None) -> int:
        return value if value is not None else 0

    result = hint.process_value(None, identity_call_next)

    # Should be a string representation of a number within the range
    assert isinstance(result, str)
    # Should be parseable as a number within the range
    numeric_value = int(result)
    assert 5 <= numeric_value <= 15


def test_number_string_hint_handles_float_conversion() -> None:
    """Test that NumberStringHint converts numeric values to strings."""
    hint = NumberStringHint(min=1, max=5)

    # Use identity call_next to see the generated value
    def identity_call_next(value: float | None) -> float:
        return value if value is not None else 0

    result = hint.process_value(None, identity_call_next)

    # Should be a string representation of a number within the range
    assert isinstance(result, str)
    # Should be parseable as a number
    numeric_value = float(result)
    assert 1 <= numeric_value <= 5


def test_number_string_hint_single_value_range() -> None:
    """Test NumberStringHint with min equals max."""
    hint = NumberStringHint(min=777, max=777)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    # Should be the single value as string
    if result.isdigit():
        assert int(result) == 777


def test_number_string_hint_shows_variation() -> None:
    """Test that generated number strings show variation within range."""
    hint = NumberStringHint(min=1, max=50)
    call_next = Mock(side_effect=lambda x: x)

    # Generate many values
    results = [hint.process_value(None, call_next) for _ in range(30)]

    # Should have some variation
    unique_values = set(results)
    assert len(unique_values) > 1  # Should generate different values

    # All should be strings
    assert all(isinstance(result, str) for result in results)


def test_number_string_hint_inherits_from_number_hint() -> None:
    """Test that NumberStringHint properly inherits NumberHint behavior."""
    hint = NumberStringHint(min=100, max=200)

    # Should have NumberHint attributes
    assert hasattr(hint, "min")
    assert hasattr(hint, "max")
    assert hint.min == 100
    assert hint.max == 200

    # But should have different type
    assert hint.type == "NUMSTR"
