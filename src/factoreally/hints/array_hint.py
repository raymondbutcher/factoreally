"""Array hint for marking fields as array types."""

from dataclasses import dataclass

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class ArrayHint(AnalysisHint):
    """Hint marking a field as an array type."""

    type: str = "ARRAY"
