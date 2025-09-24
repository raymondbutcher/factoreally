"""Test null hint functionality."""

from unittest.mock import Mock

from factoreally.hints.base import NULL
from factoreally.hints.null_hint import NullHint


def test_null_hint_basic_creation() -> None:
    """Test creating a basic NullHint."""
    hint = NullHint(pct=50.0)

    assert hint.type == "NULL"
    assert hint.pct == 50.0


def test_null_hint_100_percent_always_returns_null() -> None:
    """Test NullHint with 100% probability always returns NULL."""
    hint = NullHint(pct=100.0)
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Should always return NULL
    for _ in range(10):
        result = hint.process_value("test_value", call_next)
        assert result is NULL

    # call_next should never be called
    call_next.assert_not_called()


def test_null_hint_0_percent_never_returns_null() -> None:
    """Test NullHint with 0% probability never returns NULL."""
    hint = NullHint(pct=0.0)
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Should never return NULL
    for _ in range(10):
        result = hint.process_value("test_value", call_next)
        assert result == "processed_test_value"

    # call_next should be called every time
    assert call_next.call_count == 10


def test_null_hint_probability_distribution() -> None:
    """Test NullHint probability distribution over many samples."""
    hint = NullHint(pct=25.0)  # 25% chance of null
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    # Test with many samples to get statistical significance
    null_count = 0
    total_samples = 1000

    for _ in range(total_samples):
        result = hint.process_value("test", call_next)
        if result is NULL:
            null_count += 1

    # Should be approximately 25% null (allow some variance)
    null_percentage = (null_count / total_samples) * 100
    assert 20.0 <= null_percentage <= 30.0  # Allow 5% variance


def test_null_hint_with_none_input() -> None:
    """Test NullHint behavior with None input value."""
    hint = NullHint(pct=50.0)
    call_next = Mock(side_effect=lambda x: x if x is not None else "default")

    # Run multiple times to test both paths
    results = [hint.process_value(None, call_next) for _ in range(20)]

    # Some should be NULL, some should be processed None
    null_results = [r for r in results if r is NULL]
    processed_results = [r for r in results if r == "default"]

    # Should have both types of results
    assert len(null_results) > 0
    assert len(processed_results) > 0
    assert len(null_results) + len(processed_results) == 20


def test_null_hint_different_percentages() -> None:
    """Test NullHint with different percentage values."""
    percentages = [10.0, 33.33, 66.67, 90.0]

    for pct in percentages:
        hint = NullHint(pct=pct)
        call_next = Mock(side_effect=lambda _: "processed")

        null_count = 0
        total_samples = 300

        for _ in range(total_samples):
            result = hint.process_value("test", call_next)
            if result is NULL:
                null_count += 1

        actual_pct = (null_count / total_samples) * 100
        # Allow reasonable variance (±10%)
        assert pct - 10 <= actual_pct <= pct + 10


def test_null_hint_returns_null_constant() -> None:
    """Test that NullHint returns the NULL constant, not None."""
    hint = NullHint(pct=100.0)
    call_next = Mock()

    result = hint.process_value("test", call_next)

    # Should return the NULL constant, not None
    assert result is NULL
    assert result is not None
