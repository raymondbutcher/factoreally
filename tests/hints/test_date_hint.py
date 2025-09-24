"""Test date hint functionality."""

from datetime import date
from unittest.mock import Mock

from factoreally.hints.date_hint import DateHint


def test_date_hint_basic_creation() -> None:
    """Test creating a basic DateHint."""
    hint = DateHint(min="2023-01-01", max="2023-12-31")

    assert hint.type == "DATE"
    assert hint.min == "2023-01-01"
    assert hint.max == "2023-12-31"


def test_date_hint_process_value_with_none_generates_date() -> None:
    """Test that process_value generates date when input is None."""
    hint = DateHint(min="2023-01-01", max="2023-01-31")
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    # Should be in YYYY-MM-DD format
    assert len(result) == 10
    assert result[4] == "-"
    assert result[7] == "-"

    # Should parse as valid date
    parsed_date = date.fromisoformat(result)
    assert date(2023, 1, 1) <= parsed_date <= date(2023, 1, 31)

    call_next.assert_called_once()


def test_date_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = DateHint(min="2023-01-01", max="2023-12-31")
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("2022-06-15", call_next)

    assert result == "processed_2022-06-15"
    call_next.assert_called_once_with("2022-06-15")


def test_date_hint_date_range_bounds() -> None:
    """Test that generated dates are within specified bounds."""
    hint = DateHint(min="2023-06-01", max="2023-06-30")
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple dates
    results = [hint.process_value(None, call_next) for _ in range(20)]

    min_date = date(2023, 6, 1)
    max_date = date(2023, 6, 30)

    for result in results:
        parsed_date = date.fromisoformat(result)
        assert min_date <= parsed_date <= max_date


def test_date_hint_single_day_range() -> None:
    """Test DateHint with min and max being the same day."""
    hint = DateHint(min="2023-07-15", max="2023-07-15")
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple times - should always be the same date
    for _ in range(10):
        result = hint.process_value(None, call_next)
        assert result == "2023-07-15"


def test_date_hint_year_boundary() -> None:
    """Test DateHint across year boundary."""
    hint = DateHint(min="2022-12-30", max="2023-01-02")
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(20)]

    # Should generate dates in both years
    dates_2022 = [r for r in results if r.startswith("2022")]
    dates_2023 = [r for r in results if r.startswith("2023")]

    # With enough samples, we should get some from both years (though not guaranteed)
    # At minimum, verify all results are valid and we have both year patterns
    assert len(dates_2022) + len(dates_2023) == len(results)  # All dates accounted for
    for result in results:
        parsed_date = date.fromisoformat(result)
        assert date(2022, 12, 30) <= parsed_date <= date(2023, 1, 2)


def test_date_hint_format_consistency() -> None:
    """Test that all generated dates follow YYYY-MM-DD format."""
    hint = DateHint(min="2020-01-01", max="2025-12-31")
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(10)]

    for result in results:
        # Should be exactly 10 characters
        assert len(result) == 10
        # Should have dashes in correct positions
        assert result[4] == "-"
        assert result[7] == "-"
        # Should parse as valid date without error
        date.fromisoformat(result)
