"""Alphanumeric hint for generating alphanumeric strings."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class AlphanumericHint(AnalysisHint):
    """Hint for position-specific alphanumeric string generation."""

    type: str = "ALPHA"
    chrs: dict[str, list[int]]

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through alphanumeric hint - generate if no input, continue chain."""
        if value is None:
            # Build position-to-charset lookup
            pos_to_charset: dict[int, str] = {}
            for charset, positions in self.chrs.items():
                for pos in positions:
                    pos_to_charset[pos] = charset

            # Generate string
            positions_list = [pos for positions in self.chrs.values() for pos in positions]
            if not positions_list:
                value = ""
            else:
                max_pos = max(positions_list)
                chars = []
                for pos in range(max_pos + 1):
                    charset = pos_to_charset.get(pos, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                    chars.append(random.choice(charset))
                value = "".join(chars)
        return call_next(value)
