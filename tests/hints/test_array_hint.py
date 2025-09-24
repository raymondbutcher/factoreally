"""Test array hint functionality."""

import pytest

from factoreally.hints.array_hint import ArrayHint


def test_array_hint_basic_creation() -> None:
    """Test creating a basic ArrayHint."""
    hint = ArrayHint()

    assert hint.type == "ARRAY"


def test_array_hint_is_frozen() -> None:
    """Test that ArrayHint is immutable (frozen)."""
    hint = ArrayHint()

    # Should not be able to modify the hint after creation
    try:
        hint.type = "MODIFIED"  # type: ignore[misc]
        pytest.fail("Should not be able to modify frozen hint")
    except AttributeError:
        pass  # Expected behavior for frozen dataclass


def test_array_hint_equality() -> None:
    """Test ArrayHint equality comparison."""
    hint1 = ArrayHint()
    hint2 = ArrayHint()

    assert hint1 == hint2
    assert hint1 is not hint2  # Different instances


def test_array_hint_repr() -> None:
    """Test ArrayHint string representation."""
    hint = ArrayHint()

    repr_str = repr(hint)
    assert "ArrayHint" in repr_str
    assert "type='ARRAY'" in repr_str
