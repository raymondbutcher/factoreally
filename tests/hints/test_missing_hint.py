"""Test missing hint functionality."""

from unittest.mock import Mock

from factoreally.hints.base import MISSING
from factoreally.hints.missing_hint import MissingHint


def test_missing_hint_basic_creation() -> None:
    """Test creating a basic MissingHint."""
    hint = MissingHint(pct=30.0)

    assert hint.type == "MISSING"
    assert hint.pct == 30.0


def test_missing_hint_100_percent_never_returns_missing() -> None:
    """Test MissingHint with 100% presence never returns MISSING."""
    hint = MissingHint(pct=100.0)  # 100% present = never missing
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Should never return MISSING (field is always present)
    for _ in range(10):
        result = hint.process_value("test_value", call_next)
        assert result == "processed_test_value"

    # call_next should be called every time
    assert call_next.call_count == 10


def test_missing_hint_0_percent_always_returns_missing() -> None:
    """Test MissingHint with 0% presence always returns MISSING."""
    hint = MissingHint(pct=0.0)  # 0% present = always missing
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Should always return MISSING
    for _ in range(10):
        result = hint.process_value("test_value", call_next)
        assert result is MISSING

    # call_next should never be called
    call_next.assert_not_called()


def test_missing_hint_probability_distribution() -> None:
    """Test MissingHint probability distribution over many samples."""
    hint = MissingHint(pct=60.0)  # 60% present = 40% missing
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Test with many samples to get statistical significance
    missing_count = 0
    total_samples = 500

    for _ in range(total_samples):
        result = hint.process_value("test", call_next)
        if result is MISSING:
            missing_count += 1

    # Should be approximately 40% missing (allow some variance)
    missing_percentage = (missing_count / total_samples) * 100
    assert 35.0 <= missing_percentage <= 45.0  # Allow 5% variance


def test_missing_hint_returns_missing_constant() -> None:
    """Test that MissingHint returns the MISSING constant."""
    hint = MissingHint(pct=0.0)  # 0% present = always missing
    call_next = Mock()

    result = hint.process_value("test", call_next)

    # Should return the MISSING constant
    assert result is MISSING
    assert result is not None
