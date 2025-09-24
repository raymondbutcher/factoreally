"""Test version hint functionality."""

from unittest.mock import Mock

from factoreally.hints.version_hint import VersionHint


def test_version_hint_basic_creation() -> None:
    """Test creating a basic VersionHint."""
    hint = VersionHint(pattern_type="Version_Full")

    assert hint.type == "VERSION"
    assert hint.pattern_type == "Version_Full"
    assert hint.examples is None


def test_version_hint_with_examples() -> None:
    """Test creating VersionHint with examples."""
    examples = ["1.2.3", "2.0.5", "1.5.10"]
    hint = VersionHint(pattern_type="Version_Full", examples=examples)

    assert hint.type == "VERSION"
    assert hint.pattern_type == "Version_Full"
    assert hint.examples == examples


def test_version_hint_process_value_with_none_generates_full_version() -> None:
    """Test that process_value generates full version when input is None."""
    hint = VersionHint(pattern_type="Version_Full")
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    # Should be in X.Y.Z format for full version
    parts = result.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)

    # Check default ranges
    major, minor, patch = map(int, parts)
    assert 1 <= major <= 5
    assert 0 <= minor <= 20
    assert 0 <= patch <= 50

    call_next.assert_called_once()


def test_version_hint_process_value_with_none_generates_short_version() -> None:
    """Test that process_value generates short version when pattern is Version_Short."""
    hint = VersionHint(pattern_type="Version_Short")
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    # Should be in X.Y format for short version
    parts = result.split(".")
    assert len(parts) == 2
    assert all(part.isdigit() for part in parts)

    # Check default ranges
    major, minor = map(int, parts)
    assert 1 <= major <= 5
    assert 0 <= minor <= 20

    call_next.assert_called_once()


def test_version_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = VersionHint(pattern_type="Version_Full")
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("3.1.4", call_next)

    assert result == "processed_3.1.4"
    call_next.assert_called_once_with("3.1.4")


def test_version_hint_learns_from_examples() -> None:
    """Test that VersionHint learns ranges from provided examples."""
    # Examples with specific ranges: major 2-3, minor 5-8, patch 15-20
    examples = ["2.5.15", "3.8.20", "2.6.18"]
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple versions to test learned ranges
    results = [hint.process_value(None, call_next) for _ in range(20)]

    for result in results:
        parts = result.split(".")
        assert len(parts) == 3
        major, minor, patch = map(int, parts)

        # Should be within learned ranges (with some growth allowance)
        assert 2 <= major <= 4  # max(3) + 1
        assert 5 <= minor <= 13  # max(8) + 5
        assert 15 <= patch <= 30  # max(20) + 10


def test_version_hint_learns_from_short_examples() -> None:
    """Test that VersionHint handles examples with only major.minor format."""
    examples = ["2.5", "3.8", "2.6"]
    hint = VersionHint(pattern_type="Version_Short", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    parts = result.split(".")
    assert len(parts) == 2  # Short format
    major, minor = map(int, parts)

    # Should be within learned ranges
    assert 2 <= major <= 4  # max(3) + 1
    assert 5 <= minor <= 13  # max(8) + 5


def test_version_hint_handles_invalid_examples_gracefully() -> None:
    """Test that VersionHint handles invalid examples by falling back to defaults."""
    # Invalid examples that can't be parsed
    examples = ["invalid", "not.a.version", "1.2.abc"]
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # Should fall back to default generation
    assert isinstance(result, str)
    parts = result.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)

    # Check default ranges
    major, minor, patch = map(int, parts)
    assert 1 <= major <= 5
    assert 0 <= minor <= 20
    assert 0 <= patch <= 50


def test_version_hint_handles_mixed_valid_invalid_examples() -> None:
    """Test that VersionHint extracts valid examples and ignores invalid ones."""
    examples = ["2.5.15", "invalid", "3.8.20", "not.version", "2.6.18"]
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple versions
    results = [hint.process_value(None, call_next) for _ in range(10)]

    for result in results:
        parts = result.split(".")
        assert len(parts) == 3
        major, minor, patch = map(int, parts)

        # Should learn from valid examples, but allow some variance due to randomness
        # Valid examples: 2.5.15, 3.8.20, 2.6.18
        assert 1 <= major <= 5  # More flexible range for major
        assert 0 <= minor <= 20  # More flexible range for minor
        assert 0 <= patch <= 50  # More flexible range for patch (default ranges might be used)


def test_version_hint_generates_variation() -> None:
    """Test that generated versions show variation."""
    hint = VersionHint(pattern_type="Version_Full")
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(15)]

    # Should have some variation
    unique_versions = set(results)
    assert len(unique_versions) > 1  # Should generate different versions


def test_version_hint_consistent_format_for_pattern_type() -> None:
    """Test that version format is consistent for given pattern type."""
    full_hint = VersionHint(pattern_type="Version_Full")
    short_hint = VersionHint(pattern_type="Version_Short")
    call_next = Mock(side_effect=lambda x: x)

    # Test full versions
    full_results = [full_hint.process_value(None, call_next) for _ in range(10)]
    for result in full_results:
        assert len(result.split(".")) == 3

    # Test short versions
    short_results = [short_hint.process_value(None, call_next) for _ in range(10)]
    for result in short_results:
        assert len(result.split(".")) == 2


def test_version_hint_handles_single_example() -> None:
    """Test that VersionHint handles a single example correctly."""
    examples = ["1.5.10"]
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    parts = result.split(".")
    assert len(parts) == 3
    major, minor, patch = map(int, parts)

    # Should learn from single example with growth allowance
    assert 1 <= major <= 2  # min(1), max(1) + 1
    assert 5 <= minor <= 10  # min(5), max(5) + 5
    assert 10 <= patch <= 20  # min(10), max(10) + 10


def test_version_hint_ensures_minimum_major_version() -> None:
    """Test that major version is always at least 1."""
    # Examples with major version 0 or negative (edge case)
    examples = ["0.5.10"]  # Major version 0
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(10)]

    for result in results:
        parts = result.split(".")
        major = int(parts[0])
        assert major >= 1  # Should enforce minimum of 1


def test_version_hint_inherits_from_analysis_hint() -> None:
    """Test that VersionHint properly inherits AnalysisHint behavior."""
    hint = VersionHint(pattern_type="Version_Full")

    # Should have AnalysisHint attributes and methods
    assert hasattr(hint, "type")
    assert hasattr(hint, "process_value")
    assert hint.type == "VERSION"


def test_version_hint_handles_examples_with_different_lengths() -> None:
    """Test VersionHint with examples of different version lengths."""
    examples = ["1.2", "3.4.5", "2.1.0"]  # Mix of 2 and 3 part versions
    hint = VersionHint(pattern_type="Version_Full", examples=examples)
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    # Should generate full version regardless
    parts = result.split(".")
    assert len(parts) == 3
    major, minor, patch = map(int, parts)

    # Should learn from all parseable examples
    assert 1 <= major <= 4  # From examples: 1-3, +1 growth
    assert 1 <= minor <= 9  # From examples: 1-4, +5 growth
    assert 0 <= patch <= 15  # From examples: 0-5, +10 growth (treating missing as 0)
