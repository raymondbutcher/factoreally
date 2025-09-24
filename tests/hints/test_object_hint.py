"""Test object hint functionality."""

from factoreally.hints.object_hint import ObjectHint


def test_object_hint_basic_creation() -> None:
    """Test creating a basic ObjectHint."""
    hint = ObjectHint()

    assert hint.type == "OBJECT"


def test_object_hint_is_analysis_hint() -> None:
    """Test that ObjectHint is an AnalysisHint."""
    hint = ObjectHint()

    # Should have type field like all AnalysisHints
    assert hasattr(hint, "type")
    assert hint.type == "OBJECT"


def test_object_hint_equality() -> None:
    """Test ObjectHint equality comparison."""
    hint1 = ObjectHint()
    hint2 = ObjectHint()

    assert hint1 == hint2
    assert hint1 is not hint2  # Different instances


def test_object_hint_repr() -> None:
    """Test ObjectHint string representation."""
    hint = ObjectHint()

    repr_str = repr(hint)
    assert "ObjectHint" in repr_str
    assert "type='OBJECT'" in repr_str
