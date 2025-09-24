"""Test Auth0 ID hint functionality."""

from unittest.mock import Mock

from factoreally.hints.auth0_id_hint import Auth0IdHint


def test_auth0_id_hint_basic_creation() -> None:
    """Test creating a basic Auth0IdHint."""
    hint = Auth0IdHint()

    assert hint.type == "AUTH0_ID"


def test_auth0_id_hint_process_value_with_none_generates_id() -> None:
    """Test that process_value generates Auth0 ID when input is None."""
    hint = Auth0IdHint()
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    assert result.startswith("auth0|")
    assert len(result) == 30  # "auth0|" (6) + 24 hex chars

    # Verify it's a valid hex string after "auth0|"
    hex_part = result[6:]
    assert len(hex_part) == 24
    assert all(c in "0123456789abcdef" for c in hex_part)

    call_next.assert_called_once()


def test_auth0_id_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = Auth0IdHint()
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("existing_id", call_next)

    assert result == "processed_existing_id"
    call_next.assert_called_once_with("existing_id")


def test_auth0_id_hint_generates_unique_ids() -> None:
    """Test that generated Auth0 IDs are unique."""
    hint = Auth0IdHint()
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple IDs
    ids = [hint.process_value(None, call_next) for _ in range(10)]

    # All should be different
    assert len(set(ids)) == 10

    # All should follow Auth0 pattern
    for auth0_id in ids:
        assert auth0_id.startswith("auth0|")
        assert len(auth0_id) == 30


def test_auth0_id_hint_format_validation() -> None:
    """Test that generated Auth0 IDs follow correct format."""
    hint = Auth0IdHint()
    call_next = Mock(side_effect=lambda x: x)

    for _ in range(5):
        result = hint.process_value(None, call_next)

        # Check format: "auth0|" followed by 24 hex characters
        assert result.startswith("auth0|")
        hex_part = result[6:]
        assert len(hex_part) == 24

        # Verify each character is valid hex
        for char in hex_part:
            assert char in "0123456789abcdef"
