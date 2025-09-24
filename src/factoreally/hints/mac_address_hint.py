"""MAC address hint for generating MAC address patterns."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class MacAddressHint(AnalysisHint):
    """Hint for MAC address pattern generation."""

    type: str = "MAC"

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through MAC address hint - generate if no input, continue chain."""
        if value is None:
            hex_chars = "0123456789ABCDEF"
            octets = ["".join(random.choice(hex_chars) for _ in range(2)) for _ in range(6)]
            value = ":".join(octets)
        return call_next(value)
