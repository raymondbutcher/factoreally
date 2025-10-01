"""Alphanumeric hint for generating alphanumeric strings."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.constants import MIN_VALUES_FOR_ALPLHANUMERIC
from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class AlphanumericHint(AnalysisHint):
    """Hint for position-specific alphanumeric string generation."""

    type: str = "ALPHA"
    chrs: dict[str, list[int]]

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create AlphanumericHint for fixed-length alphanumeric patterns."""
        if len(values) < MIN_VALUES_FOR_ALPLHANUMERIC:
            return None

        # Check if all values are the same length
        lengths = {len(v) for v in values}
        if len(lengths) != 1:
            return None

        # Collect characters at each position
        char_positions: dict[int, set[str]] = defaultdict(set)
        for value in values:
            for i, char in enumerate(value):
                char_positions[i].add(char)

        # Build efficient character set groupings
        charset_to_positions: dict[str, list[int]] = {}
        for pos, char_set in char_positions.items():
            charset = "".join(sorted(char_set))
            if charset not in charset_to_positions:
                charset_to_positions[charset] = []
            charset_to_positions[charset].append(pos)

        return cls(chrs=charset_to_positions)

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
