"""Object hint for marking fields as object types with dynamic keys."""

from dataclasses import dataclass

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class ObjectHint(AnalysisHint):
    """Hint marking a field as an object type with dynamic keys."""

    type: str = "OBJECT"
