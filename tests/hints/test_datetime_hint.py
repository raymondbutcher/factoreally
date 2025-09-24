"""Tests for temporal hint functionality."""

from factoreally.hints import DatetimeHint


def test_datetime_hint() -> None:
    """Test datetime hint."""
    hint = DatetimeHint(
        min="2023-01-01T00:00:00Z",
        max="2024-01-01T00:00:00Z",
    )

    # Test processing with no input value (generates new datetime)
    def mock_call_next(value: str | None) -> str | None:
        return value

    generated_value = hint.process_value(None, mock_call_next)
    assert isinstance(generated_value, str)
    assert "T" in generated_value  # Basic ISO format check

    # Test processing with existing value (passes through)
    existing_value = "2023-06-15T12:00:00Z"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value
