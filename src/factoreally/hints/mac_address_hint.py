"""MAC address hint for generating MAC address patterns."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class MacAddressHint(AnalysisHint):
    """Hint for MAC address pattern generation."""

    type: str = "MAC"

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create MacAddressHint from sample values if they match MAC address pattern."""
        if not all(re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", v) for v in values):
            return None
        return cls()

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through MAC address hint - generate if no input, continue chain."""
        if value is None:
            hex_chars = "0123456789ABCDEF"
            octets = ["".join(random.choice(hex_chars) for _ in range(2)) for _ in range(6)]
            value = ":".join(octets)
        return call_next(value)
