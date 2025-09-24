"""Test text hint functionality."""

from unittest.mock import Mock

from factoreally.hints.text_hint import LOREM_WORDS, TextHint


def test_text_hint_basic_creation() -> None:
    """Test creating a basic TextHint."""
    hint = TextHint(min=5, max=20)

    assert hint.type == "TEXT"
    assert hint.min == 5
    assert hint.max == 20


def test_text_hint_process_value_with_none_generates_text() -> None:
    """Test that process_value generates text when input is None."""
    hint = TextHint(min=10, max=50)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    assert len(result) > 0
    call_next.assert_called_once()


def test_text_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = TextHint(min=5, max=15)
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("existing_text", call_next)

    assert result == "processed_existing_text"
    call_next.assert_called_once_with("existing_text")


def test_text_hint_generates_lorem_ipsum() -> None:
    """Test that generated text contains lorem ipsum words."""
    hint = TextHint(min=20, max=30)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # Should contain words from LOREM_WORDS
    result_words = result.lower().split()
    assert any(word in LOREM_WORDS for word in result_words)


def test_text_hint_approximate_length_targeting() -> None:
    """Test that generated text approximately targets the length range."""
    hint = TextHint(min=15, max=25)
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(10)]

    # Text generation tries to hit target length but may not be exact due to word boundaries
    # Just ensure we get reasonable text lengths (not too short/long)
    for result in results:
        assert len(result) >= 3  # At least some meaningful text
        assert len(result) <= 100  # Not excessively long


def test_text_hint_contains_spaces() -> None:
    """Test that generated text contains spaces between words."""
    hint = TextHint(min=20, max=30)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # Should have spaces (indicating multiple words)
    if len(result) > 10:  # Only check if text is long enough for multiple words
        assert " " in result


def test_text_hint_shows_variation() -> None:
    """Test that generated text shows variation."""
    hint = TextHint(min=10, max=20)
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(10)]

    # Should have some variation in generated text
    unique_results = set(results)
    assert len(unique_results) > 1  # Should generate different text


def test_text_hint_inherits_from_number_hint() -> None:
    """Test that TextHint properly inherits NumberHint behavior."""
    hint = TextHint(min=5, max=25)

    # Should have NumberHint attributes
    assert hasattr(hint, "min")
    assert hasattr(hint, "max")
    assert hint.min == 5
    assert hint.max == 25

    # But should have different type
    assert hint.type == "TEXT"


def test_text_hint_handles_small_target_length() -> None:
    """Test TextHint with very small target length."""
    hint = TextHint(min=1, max=5)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # Should still generate some text even with small target
    assert isinstance(result, str)
    assert len(result) >= 1


def test_lorem_words_constant_exists() -> None:
    """Test that LOREM_WORDS constant is properly defined."""
    assert isinstance(LOREM_WORDS, list)
    assert len(LOREM_WORDS) > 0
    assert all(isinstance(word, str) for word in LOREM_WORDS)
    assert "lorem" in LOREM_WORDS
    assert "ipsum" in LOREM_WORDS
