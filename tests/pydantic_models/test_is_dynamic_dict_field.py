"""Tests for _is_dynamic_dict_field helper function."""

from typing import Any

from factoreally.pydantic_models import _is_dynamic_dict_field


def test_is_dynamic_dict_field_dict_str_any() -> None:
    """Test _is_dynamic_dict_field with Dict[str, Any]."""
    assert _is_dynamic_dict_field(dict[str, Any]) is True


def test_is_dynamic_dict_field_dict_str_str() -> None:
    """Test _is_dynamic_dict_field with Dict[str, str]."""
    assert _is_dynamic_dict_field(dict[str, str]) is True


def test_is_dynamic_dict_field_dict_int_str() -> None:
    """Test _is_dynamic_dict_field with Dict[int, str] (dynamic)."""
    assert _is_dynamic_dict_field(dict[int, str]) is True


def test_is_dynamic_dict_field_list() -> None:
    """Test _is_dynamic_dict_field with list type (not dynamic)."""
    assert _is_dynamic_dict_field(list[str]) is False


def test_is_dynamic_dict_field_str() -> None:
    """Test _is_dynamic_dict_field with simple str type (not dynamic)."""
    assert _is_dynamic_dict_field(str) is False


def test_is_dynamic_dict_field_none() -> None:
    """Test _is_dynamic_dict_field with None (not dynamic)."""
    assert _is_dynamic_dict_field(None) is False
