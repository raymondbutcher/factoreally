"""Tests for _parse_field_paths function."""

from typing import TYPE_CHECKING

from factoreally.factory_spec import _parse_field_paths
from factoreally.hints import ArrayHint, ChoiceHint, NumberHint

if TYPE_CHECKING:
    from factoreally.hints.base import AnalysisHint


def test_parse_field_paths_simple_arrays() -> None:
    """Test parsing of simple array fields (Option A: direct hints on array element)."""
    field_path_hints: dict[str, list[AnalysisHint]] = {
        "actions": [ArrayHint(type="ARRAY"), NumberHint(type="NUMBER", min=1, max=3)],
        "actions[]": [ChoiceHint(type="CHOICE", choices=["A", "B"], weights=[0.5, 0.5])],
    }

    current, children = _parse_field_paths(field_path_hints)

    # Should have no current level hints
    assert len(current) == 0

    # Should group all under 'actions'
    assert len(children) == 1
    assert "actions" in children

    actions_children = children["actions"]
    assert "" in actions_children  # Direct field hints (ARRAY + NUMBER)
    assert "[]" in actions_children  # Array element hints (CHOICE)

    # Verify the hint types
    assert len([h for h in actions_children[""] if h.type == "ARRAY"]) == 1
    assert len([h for h in actions_children[""] if h.type == "NUMBER"]) == 1
    assert len([h for h in actions_children["[]"] if h.type == "CHOICE"]) == 1


def test_parse_field_paths_object_arrays() -> None:
    """Test parsing of object array fields (Option B: hints on nested fields)."""
    field_path_hints: dict[str, list[AnalysisHint]] = {
        "actions": [ArrayHint(type="ARRAY"), NumberHint(type="NUMBER", min=1, max=3)],
        "actions[].type": [ChoiceHint(type="CHOICE", choices=["X", "Y"], weights=[0.5, 0.5])],
        "actions[].id": [NumberHint(type="NUMBER", min=100, max=999)],
    }

    current, children = _parse_field_paths(field_path_hints)

    # Should have no current level hints
    assert len(current) == 0

    # Should group all under 'actions'
    assert len(children) == 1
    assert "actions" in children

    actions_children = children["actions"]
    assert "" in actions_children  # Direct field hints (ARRAY + NUMBER)
    assert "[].type" in actions_children  # Array element property hints
    assert "[].id" in actions_children  # Array element property hints

    # Verify the hint types
    assert len([h for h in actions_children[""] if h.type == "ARRAY"]) == 1
    assert len([h for h in actions_children[""] if h.type == "NUMBER"]) == 1
    assert len([h for h in actions_children["[].type"] if h.type == "CHOICE"]) == 1
    assert len([h for h in actions_children["[].id"] if h.type == "NUMBER"]) == 1
