"""Version hint for generating semantic version strings."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class VersionHint(AnalysisHint):
    """Hint for version string generation."""

    type: str = "VERSION"

    examples: list[str] | None = None
    pattern_type: str

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through version hint - generate if no input, continue chain."""
        if value is None:
            # Try to learn from examples if available
            if self.examples:
                major_range = [1, 5]
                minor_range = [0, 20]
                patch_range = [0, 50]

                try:
                    # Parse examples to learn realistic ranges
                    parsed_versions = []
                    for example in self.examples:
                        parts = example.split(".")
                        if len(parts) >= 2:  # noqa: PLR2004
                            major = int(parts[0])
                            minor = int(parts[1])
                            patch = int(parts[2]) if len(parts) > 2 else 0  # noqa: PLR2004
                            parsed_versions.append((major, minor, patch))

                    if parsed_versions:
                        # Learn ranges from examples
                        majors = [v[0] for v in parsed_versions]
                        minors = [v[1] for v in parsed_versions]
                        patches = [v[2] for v in parsed_versions]

                        major_range = [min(majors), max(majors) + 1]  # +1 for potential growth
                        minor_range = [min(minors), max(minors) + 5]  # Allow some growth
                        patch_range = [min(patches), max(patches) + 10]  # Allow patch growth

                except (ValueError, IndexError):
                    # Fall back to default ranges if parsing fails
                    pass

                # Generate version within learned ranges
                major = random.randint(max(1, major_range[0]), max(major_range[1], major_range[0] + 1))
                minor = random.randint(minor_range[0], max(minor_range[1], minor_range[0] + 1))

                # Generate based on pattern type
                if self.pattern_type == "Version_Short":
                    value = f"{major}.{minor}"
                else:
                    patch = random.randint(patch_range[0], max(patch_range[1], patch_range[0] + 1))
                    value = f"{major}.{minor}.{patch}"
            else:
                # Default generation when no examples available
                major = random.randint(1, 5)
                minor = random.randint(0, 20)

                if self.pattern_type == "Version_Short":
                    value = f"{major}.{minor}"
                else:
                    patch = random.randint(0, 50)
                    value = f"{major}.{minor}.{patch}"

        return call_next(value)
