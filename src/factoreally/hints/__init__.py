"""Strongly typed hint classes for factory generation analysis."""

from collections.abc import Callable
from typing import Any

# Import individual hint classes from their own files
from factoreally.hints.alphanumeric_hint import AlphanumericHint
from factoreally.hints.array_hint import ArrayHint
from factoreally.hints.auth0_id_hint import Auth0IdHint

# Import base class
from factoreally.hints.base import AnalysisHint
from factoreally.hints.choice_hint import ChoiceHint
from factoreally.hints.constant_value_hint import ConstantValueHint
from factoreally.hints.date_hint import DateHint
from factoreally.hints.datetime_hint import DatetimeHint
from factoreally.hints.duration_range_hint import DurationRangeHint
from factoreally.hints.mac_address_hint import MacAddressHint
from factoreally.hints.missing_hint import MissingHint
from factoreally.hints.null_hint import NullHint
from factoreally.hints.number_hint import NumberHint
from factoreally.hints.number_string_hint import NumberStringHint
from factoreally.hints.object_hint import ObjectHint
from factoreally.hints.text_hint import TextHint
from factoreally.hints.uuid4_hint import Uuid4Hint
from factoreally.hints.version_hint import VersionHint

# Explicitly export all classes
__all__ = [
    "HINT_TYPE_MAP",
    "AlphanumericHint",
    "AnalysisHint",
    "ArrayHint",
    "Auth0IdHint",
    "ChoiceHint",
    "ConstantValueHint",
    "DateHint",
    "DatetimeHint",
    "DurationRangeHint",
    "MacAddressHint",
    "MissingHint",
    "NullHint",
    "NumberHint",
    "NumberStringHint",
    "ObjectHint",
    "TextHint",
    "Uuid4Hint",
    "VersionHint",
    "create_hint_from_data",
    "create_hint_from_spec_format",
    "create_hints_from_spec_format",
    "generate_value_from_hints",
]

# Simple mapping from hint type strings to hint classes
HINT_TYPE_MAP: dict[str, type[AnalysisHint]] = {
    "ALPHA": AlphanumericHint,
    "ARRAY": ArrayHint,
    "AUTH0_ID": Auth0IdHint,
    "CHOICE": ChoiceHint,
    "CONST": ConstantValueHint,
    "DATE": DateHint,
    "DATETIME": DatetimeHint,
    "DURATION": DurationRangeHint,
    "MAC": MacAddressHint,
    "MISSING": MissingHint,
    "NULL": NullHint,
    "NUMBER": NumberHint,
    "NUMSTR": NumberStringHint,
    "OBJECT": ObjectHint,
    "TEXT": TextHint,
    "UUID4": Uuid4Hint,
    "VERSION": VersionHint,
}


def create_hint_from_data(hint_data: dict[str, Any]) -> AnalysisHint:
    """Create hint instance from analysis data dictionary."""
    # Do not fail silently, we expect data to be valid and would prefer scripts
    # or tests to break if stop when encountering invalid data.
    hint_type = hint_data["type"]
    hint_class = HINT_TYPE_MAP[hint_type]
    return hint_class(**hint_data)


def create_hint_from_spec_format(hint_type: str, hint_params: dict[str, Any]) -> AnalysisHint:
    """Create hint instance from spec format (type as key, params as dict)."""
    hint_class = HINT_TYPE_MAP[hint_type]
    # Add type to params for the hint class constructor
    full_params = {"type": hint_type, **hint_params}
    return hint_class(**full_params)


def create_hints_from_spec_format(hints_data: dict[str, dict[str, Any]]) -> list[AnalysisHint]:
    """Create hints from spec format where hint types are keys and params are values."""
    return [create_hint_from_spec_format(hint_type, params) for hint_type, params in hints_data.items()]


def generate_value_from_hints(hints: list[AnalysisHint]) -> Any:
    chain = _create_hint_chain(hints)
    return chain(None)


def _create_hint_chain(remaining_hints: list[AnalysisHint]) -> Callable[[Any], Any]:
    if not remaining_hints:
        # Base case: no more hints to process, return the value as-is
        return lambda value: value

    # Get the next hint and create a chain for the remaining hints
    current_hint = remaining_hints[0]
    next_chain = _create_hint_chain(remaining_hints[1:])

    # Return a function that applies the current hint
    return lambda value: current_hint.process_value(value, next_chain)
