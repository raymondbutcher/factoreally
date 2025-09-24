"""Text hint for generating lorem ipsum text with length distribution."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.number_hint import NumberHint

# Built-in lorem ipsum words
LOREM_WORDS = [
    "lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "sed",
    "do",
    "eiusmod",
    "tempor",
    "incididunt",
    "ut",
    "labore",
    "et",
    "dolore",
    "magna",
    "aliqua",
    "enim",
    "ad",
    "minim",
    "veniam",
    "quis",
    "nostrud",
    "exercitation",
    "ullamco",
    "laboris",
    "nisi",
    "aliquip",
    "ex",
    "ea",
    "commodo",
    "consequat",
    "duis",
    "aute",
    "irure",
    "in",
    "reprehenderit",
    "voluptate",
    "velit",
    "esse",
    "cillum",
    "fugiat",
    "nulla",
    "pariatur",
    "excepteur",
    "sint",
    "occaecat",
    "cupidatat",
    "non",
    "proident",
    "sunt",
    "culpa",
    "qui",
    "officia",
    "deserunt",
    "mollit",
    "anim",
    "id",
    "est",
    "laborum",
]


@dataclass(frozen=True, kw_only=True)
class TextHint(NumberHint):
    """Hint for generating lorem ipsum text with length distribution."""

    type: str = "TEXT"

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through text hint - generate lorem ipsum if no input, continue chain."""
        if value is None:
            # Get target length from NumberHint distribution
            target_length = super().process_value(None, lambda x: x)
            target_length = int(max(1, target_length))  # Ensure positive integer

            # Generate lorem ipsum text to target length
            words: list[str] = []
            current_length = 0
            word_index = 0

            while current_length < target_length:
                word = LOREM_WORDS[word_index % len(LOREM_WORDS)]
                word_index += 1

                # Add space if not first word
                if words:
                    needed_length = target_length - current_length
                    space_and_word = " " + word
                    if len(space_and_word) <= needed_length:
                        words.append(space_and_word)
                        current_length += len(space_and_word)
                    else:
                        # If adding this word would exceed target, stop
                        break
                elif len(word) <= target_length:
                    # First word, no space needed
                    words.append(word)
                    current_length += len(word)
                else:
                    # If even first word is too long, truncate it
                    words.append(word[:target_length])
                    break

            value = "".join(words)

        return call_next(value)
