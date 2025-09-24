"""Tests for choice hint functionality."""

from factoreally.hints import ChoiceHint


def test_choice_hint_weighted() -> None:
    """Test choice hint with weights (weighted mode)."""
    hint = ChoiceHint(
        choices=["A", "B", "C"],
        weights=[50, 30, 20],
    )

    # Test processing with no input value (generates new choice)
    def mock_call_next(value: str | None) -> str | None:
        return value

    for _ in range(10):
        generated_value = hint.process_value(None, mock_call_next)
        assert generated_value in ["A", "B", "C"]

    # Test processing with existing value (passes through)
    existing_value = "existing-choice"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value


def test_choice_hint_simple() -> None:
    """Test choice hint without weights (simple mode)."""
    hint = ChoiceHint(
        choices=["X", "Y", "Z"],
    )

    # Test processing with no input value (generates new choice)
    def mock_call_next(value: str | None) -> str | None:
        return value

    for _ in range(10):
        generated_value = hint.process_value(None, mock_call_next)
        assert generated_value in ["X", "Y", "Z"]

    # Test processing with existing value (passes through)
    existing_value = "existing-choice"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value


def test_choice_hint_weighted_frequency_data() -> None:
    """Test choice hint with weighted frequency data."""
    hint = ChoiceHint(
        choices=["active", "inactive", "pending"],
        weights=[60.0, 30.0, 10.0],
    )

    # Test processing with no input value (generates weighted choice)
    def mock_call_next(value: str | None) -> str | None:
        return value

    for _ in range(10):
        generated_value = hint.process_value(None, mock_call_next)
        assert generated_value in ["active", "inactive", "pending"]

    # Test processing with existing value (passes through)
    existing_value = "existing-status"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value


def test_choice_hint_defaults_mode() -> None:
    """Test choice hint with simple default values."""
    hint = ChoiceHint(
        choices=["default", "N/A", "unknown"],
    )

    # Test processing with no input value (generates simple choice)
    def mock_call_next(value: str | None) -> str | None:
        return value

    for _ in range(10):
        generated_value = hint.process_value(None, mock_call_next)
        assert generated_value in ["default", "N/A", "unknown"]

    # Test processing with existing value (passes through)
    existing_value = "existing-category"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value


def test_choice_hint_single_weighted_value() -> None:
    """Test that choice hint with weights works correctly."""
    hint = ChoiceHint(
        choices=["weighted"],
        weights=[100.0],
    )

    def mock_call_next(value: str | None) -> str | None:
        return value

    # Should use weighted mode, not defaults mode
    for _ in range(10):
        generated_value = hint.process_value(None, mock_call_next)
        assert generated_value == "weighted"


def test_choice_hint_empty_choices() -> None:
    """Test choice hint behavior when no choices are provided."""
    hint = ChoiceHint(
        choices=[],  # Empty choices
    )

    def mock_call_next(value: str | None) -> str | None:
        return value

    # Should pass through None without generating anything
    result = hint.process_value(None, mock_call_next)
    assert result is None

    # Should pass through existing values
    result = hint.process_value("existing", mock_call_next)
    assert result == "existing"
