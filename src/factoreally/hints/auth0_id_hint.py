"""Auth0 ID hint for generating Auth0 identifier patterns."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class Auth0IdHint(AnalysisHint):
    """Hint for Auth0 ID pattern generation."""

    type: str = "AUTH0_ID"

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create Auth0IdHint from sample values if they match Auth0 ID pattern."""
        if not all(v.startswith("auth0|") for v in values):
            return None
        return cls()

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through Auth0 ID hint - generate if no input, continue chain."""
        if value is None:
            hex_string = "".join(random.choice("0123456789abcdef") for _ in range(24))
            value = f"auth0|{hex_string}"
        return call_next(value)
