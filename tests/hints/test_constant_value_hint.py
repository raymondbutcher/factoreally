"""Test constant value hint functionality."""

from unittest.mock import Mock

from factoreally.hints.constant_value_hint import ConstantValueHint


def test_constant_value_hint_basic_creation() -> None:
    """Test creating a basic ConstantValueHint."""
    hint = ConstantValueHint(val="test_value")

    assert hint.type == "CONST"
    assert hint.val == "test_value"


def test_constant_value_hint_process_value_with_none_returns_constant() -> None:
    """Test that process_value returns constant when input is None."""
    hint = ConstantValueHint(val="constant")
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert result == "constant"
    call_next.assert_called_once_with("constant")


def test_constant_value_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = ConstantValueHint(val="constant")
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("existing", call_next)

    assert result == "processed_existing"
    call_next.assert_called_once_with("existing")


def test_constant_value_hint_with_different_types() -> None:
    """Test ConstantValueHint with different value types."""
    # String constant
    string_hint = ConstantValueHint(val="text")
    call_next = Mock(side_effect=lambda x: x)

    result = string_hint.process_value(None, call_next)
    assert result == "text"

    # Integer constant
    int_hint = ConstantValueHint(val=42)
    result = int_hint.process_value(None, call_next)
    assert result == 42

    # List constant
    list_hint = ConstantValueHint(val=[1, 2, 3])
    result = list_hint.process_value(None, call_next)
    assert result == [1, 2, 3]

    # Dict constant
    dict_hint = ConstantValueHint(val={"key": "value"})
    result = dict_hint.process_value(None, call_next)
    assert result == {"key": "value"}


def test_constant_value_hint_with_none_value() -> None:
    """Test ConstantValueHint with None as the constant value."""
    hint = ConstantValueHint(val=None)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert result is None
    call_next.assert_called_once_with(None)


def test_constant_value_hint_consistency() -> None:
    """Test that ConstantValueHint returns the same value consistently."""
    hint = ConstantValueHint(val="consistent")
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple times
    results = [hint.process_value(None, call_next) for _ in range(10)]

    # All should be the same
    assert all(result == "consistent" for result in results)
    assert call_next.call_count == 10
