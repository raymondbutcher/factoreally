"""Test duration range hint functionality."""

from unittest.mock import Mock

from factoreally.hints.duration_range_hint import DurationRangeHint


def test_duration_range_hint_basic_creation() -> None:
    """Test creating a basic DurationRangeHint."""
    hint = DurationRangeHint(fmt="HMS", min=0.0, max=3600.0, avg=1800.0)

    assert hint.type == "DURATION"
    assert hint.fmt == "HMS"
    assert hint.min == 0.0
    assert hint.max == 3600.0
    assert hint.avg == 1800.0


def test_duration_range_hint_process_value_with_none_generates_duration() -> None:
    """Test that process_value generates duration when input is None."""
    hint = DurationRangeHint(fmt="HMS", min=60.0, max=120.0, avg=90.0)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # HMS format returns formatted string
    assert isinstance(result, str)
    # Should match HH:MM:SS format
    parts = result.split(":")
    assert len(parts) == 3
    # All parts should be numeric
    hours, minutes, seconds = map(int, parts)
    assert 0 <= hours <= 23
    assert 0 <= minutes <= 59
    assert 0 <= seconds <= 59

    call_next.assert_called_once()


def test_duration_range_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = DurationRangeHint(fmt="HMS", min=0.0, max=100.0, avg=50.0)
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value(42, call_next)

    assert result == "processed_42"
    call_next.assert_called_once_with(42)


def test_duration_range_hint_different_formats() -> None:
    """Test DurationRangeHint with different format types."""
    formats = ["HMS", "MS", "S"]

    for fmt in formats:
        hint = DurationRangeHint(fmt=fmt, min=10.0, max=100.0, avg=55.0)
        call_next = Mock(side_effect=lambda x: x)

        result = hint.process_value(None, call_next)

        # HMS format returns string, others return numeric
        if fmt == "HMS":
            assert isinstance(result, str)
            assert len(result.split(":")) == 3  # HH:MM:SS format
        else:
            assert isinstance(result, (int, float))
            assert result > 0  # Duration should be positive
        assert hint.fmt == fmt


def test_duration_range_hint_respects_bounds_approximately() -> None:
    """Test that generated durations are roughly within bounds (normal distribution)."""
    hint = DurationRangeHint(fmt="S", min=10.0, max=90.0, avg=50.0)
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple durations - most should be within reasonable range
    results = [hint.process_value(None, call_next) for _ in range(20)]

    # Normal distribution should keep most values reasonably close to bounds
    # Allow some tolerance since it's a normal distribution
    for result in results:
        assert isinstance(result, (int, float))
        # Should be roughly in expected range (with some tolerance for normal distribution)
        assert 0.0 <= result <= 150.0  # Allow some deviation from strict bounds


def test_duration_range_hint_shows_variation() -> None:
    """Test that generated durations show variation."""
    hint = DurationRangeHint(fmt="S", min=1.0, max=100.0, avg=50.0)
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(15)]

    # Should have some variation (not all identical)
    unique_values = set(results)
    assert len(unique_values) > 1


def test_duration_range_hint_hms_format_processing() -> None:
    """Test that HMS format processing works correctly."""
    hint = DurationRangeHint(fmt="HMS", min=3600.0, max=7200.0, avg=5400.0)  # 1-2 hours
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # HMS format returns formatted time string
    assert isinstance(result, str)
    # Should match HH:MM:SS format for 1-2 hours
    parts = result.split(":")
    assert len(parts) == 3
    hours, _minutes, _seconds = map(int, parts)
    assert 1 <= hours <= 2  # Should be 1-2 hours given the range
    call_next.assert_called_once()
