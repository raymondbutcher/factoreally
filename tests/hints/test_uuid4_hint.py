"""Tests for string hint functionality."""

import uuid

from factoreally.hints import Uuid4Hint


def test_uuid4_hint() -> None:
    """Test UUID4 hint."""
    hint = Uuid4Hint()

    # Test processing with no input value (generates new UUID)
    def mock_call_next(value: str | None) -> str | None:
        return value

    generated_value = hint.process_value(None, mock_call_next)
    assert isinstance(generated_value, str)
    uuid.UUID(generated_value)  # Should not raise

    # Test processing with existing value (passes through)
    existing_value = "existing-value"
    result_value = hint.process_value(existing_value, mock_call_next)
    assert result_value == existing_value
