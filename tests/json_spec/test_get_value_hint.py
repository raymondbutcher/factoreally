"""Tests for _get_value_hint function."""

from collections import Counter
from typing import TYPE_CHECKING

from factoreally.analyzers import Analyzers
from factoreally.json_spec import _get_value_hint

if TYPE_CHECKING:
    from factoreally.hints.base import SimpleType


def test_get_value_hint_no_match() -> None:
    """Test _get_value_hint returns None when no analyzers match."""
    analyzers = Analyzers()
    value_counts: Counter[SimpleType] = Counter()

    hint = _get_value_hint(analyzers, "unknown_field", value_counts)

    assert hint is None
