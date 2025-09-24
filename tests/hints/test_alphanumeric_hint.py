"""Test alphanumeric hint functionality."""

from unittest.mock import Mock

from factoreally.hints.alphanumeric_hint import AlphanumericHint


def test_alphanumeric_hint_basic_creation() -> None:
    """Test creating a basic AlphanumericHint."""
    hint = AlphanumericHint(chrs={"ABC": [0, 2], "123": [1]})

    assert hint.type == "ALPHA"
    assert hint.chrs == {"ABC": [0, 2], "123": [1]}


def test_alphanumeric_hint_process_value_with_none_generates_string() -> None:
    """Test that process_value generates string when input is None."""
    hint = AlphanumericHint(chrs={"AB": [0], "12": [1], "XY": [2]})
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    assert len(result) == 3  # positions 0, 1, 2
    call_next.assert_called_once()


def test_alphanumeric_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = AlphanumericHint(chrs={"AB": [0]})
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("existing", call_next)

    assert result == "processed_existing"
    call_next.assert_called_once_with("existing")


def test_alphanumeric_hint_generates_correct_positions() -> None:
    """Test that generated string uses correct charset for each position."""
    hint = AlphanumericHint(chrs={"A": [0], "1": [1], "Z": [2]})
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple times to check consistency
    results = [hint.process_value(None, call_next) for _ in range(10)]

    for result in results:
        assert len(result) == 3
        assert result[0] == "A"  # Position 0 only has 'A'
        assert result[1] == "1"  # Position 1 only has '1'
        assert result[2] == "Z"  # Position 2 only has 'Z'


def test_alphanumeric_hint_handles_missing_positions() -> None:
    """Test that missing positions use default charset."""
    hint = AlphanumericHint(chrs={"A": [0], "B": [2]})  # Skip position 1
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert len(result) == 3
    assert result[0] == "A"
    # Position 1 should use default charset
    assert result[1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    assert result[2] == "B"


def test_alphanumeric_hint_empty_charset_positions() -> None:
    """Test behavior with empty charset dict."""
    hint = AlphanumericHint(chrs={})
    call_next = Mock(side_effect=lambda x: x)

    # This should not generate anything since there are no positions
    # The max position calculation should handle empty case
    result = hint.process_value(None, call_next)

    # When there are no positions defined, no string should be generated
    assert result == ""
    call_next.assert_called_once_with("")
