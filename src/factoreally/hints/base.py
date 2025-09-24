"""Base class for analysis hints."""

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

SimpleType = bool | float | int | str


class Sentinel:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"<factoreally.{self.name}>"


NULL = Sentinel("NullValueMarker")
MISSING = Sentinel("MissingFieldMarker")


@dataclass(frozen=True, kw_only=True)
class AnalysisHint(ABC):
    """Base class for all analysis hints.

    All hints must provide a type. Additional fields are
    defined by specific hint subclasses.

    Each hint class is responsible for both representing hint data and
    processing itself into factory field definitions.
    """

    type: str

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through this hint using call_next pattern.

        Args:
            value: Current value being processed through the hint chain
            call_next: Callback to invoke the next hint in the chain
            field_analysis: Analysis data for the field being processed

        Returns:
            Final processed value (either from this hint or from calling next hints)
        """
        return call_next(value)
