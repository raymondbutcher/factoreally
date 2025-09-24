"""Test MAC address hint functionality."""

from unittest.mock import Mock

from factoreally.hints.mac_address_hint import MacAddressHint


def test_mac_address_hint_basic_creation() -> None:
    """Test creating a basic MacAddressHint."""
    hint = MacAddressHint()

    assert hint.type == "MAC"


def test_mac_address_hint_process_value_with_none_generates_mac() -> None:
    """Test that process_value generates MAC address when input is None."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: x)

    result = hint.process_value(None, call_next)

    assert isinstance(result, str)
    # Should be in MAC address format (e.g., "01:23:45:67:89:AB")
    parts = result.split(":")
    assert len(parts) == 6
    assert all(len(part) == 2 for part in parts)
    assert all(all(c in "0123456789ABCDEF" for c in part) for part in parts)

    call_next.assert_called_once()


def test_mac_address_hint_process_value_with_existing_value_passes_through() -> None:
    """Test that process_value passes through existing non-None values."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: f"processed_{x}")

    result = hint.process_value("00:11:22:33:44:55", call_next)

    assert result == "processed_00:11:22:33:44:55"
    call_next.assert_called_once_with("00:11:22:33:44:55")


def test_mac_address_hint_generates_valid_mac_format() -> None:
    """Test that generated MAC addresses follow correct format."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple MAC addresses
    results = [hint.process_value(None, call_next) for _ in range(10)]

    for mac_address in results:
        # Should have exactly 5 colons
        assert mac_address.count(":") == 5

        # Should be exactly 17 characters (12 hex + 5 colons)
        assert len(mac_address) == 17

        # Each octet should be 2 hex digits
        octets = mac_address.split(":")
        assert len(octets) == 6
        for octet in octets:
            assert len(octet) == 2
            assert all(c in "0123456789ABCDEF" for c in octet)


def test_mac_address_hint_generates_unique_addresses() -> None:
    """Test that generated MAC addresses show variation."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: x)

    # Generate multiple MAC addresses
    addresses = [hint.process_value(None, call_next) for _ in range(20)]

    # Should generate different addresses
    unique_addresses = set(addresses)
    assert len(unique_addresses) > 1  # Should generate different MACs


def test_mac_address_hint_uppercase_hex() -> None:
    """Test that generated MAC addresses use uppercase hex digits."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(5)]

    for mac_address in results:
        # Remove colons and check all characters are valid uppercase hex
        hex_chars = mac_address.replace(":", "")
        assert all(c in "0123456789ABCDEF" for c in hex_chars)
        # Should not contain lowercase hex letters
        assert all(c not in "abcdef" for c in hex_chars)


def test_mac_address_hint_format_consistency() -> None:
    """Test that all generated MAC addresses follow consistent format."""
    hint = MacAddressHint()
    call_next = Mock(side_effect=lambda x: x)

    results = [hint.process_value(None, call_next) for _ in range(10)]

    for mac_address in results:
        # Should not start or end with colon
        assert not mac_address.startswith(":")
        assert not mac_address.endswith(":")
        # Should not have consecutive colons
        assert "::" not in mac_address
        # Should match expected pattern exactly
        octets = mac_address.split(":")
        assert len(octets) == 6
        assert all(len(octet) == 2 and all(c in "0123456789ABCDEF" for c in octet) for octet in octets)
