"""Constant value hint for generating fixed values."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class ConstantValueHint(AnalysisHint):
    """Hint for constant value generation."""

    type: str = "CONST"

    val: Any

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through constant value hint - generate if no input, continue chain."""
        if value is None:
            value = self.val
        return call_next(value)
