"""Tests for Factory null handling functionality."""

from factoreally import Factory


def test_build_null_hint_with_child_fields_100_percent() -> None:
    """Test that Factory with NULL hint at 100% returns None even with child fields."""
    spec_data = {
        "metadata": {
            "samples_analyzed": 10,
        },
        "fields": {
            "wand": {"NULL": {"pct": 100.0}},
            "wand.model": {"CONST": {"val": "M2000"}},
        },
    }

    factory = Factory(spec_data)

    # Test multiple times to ensure consistency with 100% null
    for _ in range(10):
        result = factory.build()
        assert "wand" in result
        assert result["wand"] is None


def test_build_null_hint_with_child_fields_mixed() -> None:
    """Test that Factory with NULL hint <100% probability works correctly with child fields."""
    spec_data = {
        "metadata": {
            "samples_analyzed": 10,
        },
        "fields": {
            "wand": {"NULL": {"pct": 50.0}},  # 50% null, 50% object
            "wand.model": {"CONST": {"val": "M2000"}},
        },
    }

    factory = Factory(spec_data)

    # Test multiple times to see both null and non-null cases
    null_count = 0
    object_count = 0

    for _ in range(100):
        result = factory.build()
        assert "wand" in result

        if result["wand"] is None:
            null_count += 1
        else:
            object_count += 1
            # When not null, should be proper object
            assert isinstance(result["wand"], dict)
            assert "model" in result["wand"]
            assert result["wand"]["model"] == "M2000"

    # Should have approximately 50% null and 50% objects (with some variance)
    assert 30 <= null_count <= 70  # Allow for randomness variance
    assert 30 <= object_count <= 70


def test_build_null_hint_with_nested_child_fields() -> None:
    """Test that Factory with NULL hint works with deeply nested child fields."""
    spec_data = {
        "metadata": {
            "samples_analyzed": 10,
        },
        "fields": {
            "device": {"NULL": {"pct": 100.0}},
            "device.settings": {"CONST": {"val": "config"}},
            "device.settings.mode": {"CONST": {"val": "auto"}},
        },
    }

    factory = Factory(spec_data)

    # Test multiple times to ensure consistency
    for _ in range(10):
        result = factory.build()
        assert "device" in result
        assert result["device"] is None
