import json
import random
import string
from pathlib import Path
from typing import Any

from factoreally.hints import create_hints_from_spec_format, generate_value_from_hints
from factoreally.hints.base import MISSING, NULL, AnalysisHint


class SpecValidationError(Exception):
    """Raised when factory specification is invalid or corrupted."""


ARRAY_FIELD_HINT_TYPES = {"ARRAY", "NUMBER", "NULL", "MISSING"}
OBJECT_FIELD_HINT_TYPES = {"OBJECT", "NUMBER", "NULL", "MISSING"}

Hints = list[AnalysisHint]
FieldHints = dict[str, Hints]


class FactorySpec:
    def __init__(self, field_hints: FieldHints, field_path: str = "") -> None:
        self._field_path = field_path
        self._hints, self._children = _parse_field_paths(field_hints)
        self._is_array_field = "ARRAY" in {h.type for h in self._hints}
        self._is_object_field = "OBJECT" in {h.type for h in self._hints}
        self._array_element_factory: FactorySpec | None = None
        self._object_element_factory: FactorySpec | None = None
        self._child_factories: dict[str, FactorySpec] = {}
        self._prepared = False

    def build(self) -> Any:
        if self._is_array_field:
            if not self._prepared:
                self._prepare_array()
                self._prepared = True
            return self._build_array()

        if self._is_object_field:
            if not self._prepared:
                self._prepare_dynamic_object()
                self._prepared = True
            return self._build_dynamic_object()

        if self._children:
            if not self._prepared:
                self._prepare_object()
                self._prepared = True
            return self._build_object()

        return self._build_leaf()

    def _get_fixed_length(self) -> int | None:
        for hint in self._hints:
            if hint.type == "NUMBER":
                if hint.min == hint.max:  # type: ignore[attr-defined]
                    return hint.max  # type: ignore[attr-defined,no-any-return]
                return None
        return None

    def _prepare_array(self) -> None:
        if self._get_fixed_length() == 0:
            return

        if "" not in self._children:
            msg = f"Array field '{self._field_path}' missing empty string key in children"
            raise SpecValidationError(msg)

        nested_object_field_hints: FieldHints = {}
        for field_path, hints in self._children[""].items():
            if field_path.startswith("[]"):
                # Handle array fields
                field_path = field_path.removeprefix("[]").removeprefix(".")  # noqa: PLW2901
            nested_object_field_hints[field_path] = hints

        self._array_element_factory = self.__class__(
            nested_object_field_hints,
            field_path=f"{self._field_path}[]",
        )

    def _build_array(self) -> list[Any] | None:
        """Build array field with elements."""

        array_size = generate_value_from_hints(self._hints)

        if array_size is NULL:
            return None

        if not isinstance(array_size, int):
            msg = f"unexpected generated value for array size: {array_size}"
            raise TypeError(msg)

        if array_size == 0:
            return []

        if not self._array_element_factory:
            msg = "prepare_array did not set array_element_factory"
            raise RuntimeError(msg)

        return [self._array_element_factory.build() for _ in range(array_size)]

    def _prepare_dynamic_object(self) -> None:
        if self._get_fixed_length() == 0:
            return

        if "" not in self._children:
            msg = f"Object field '{self._field_path}' missing empty string key in children"
            raise SpecValidationError(msg)

        # Create factory for object element values using {} notation
        nested_object_field_hints: FieldHints = {}
        for field_path, hints in self._children[""].items():
            if field_path.startswith("{}"):
                # Handle object fields - remove {} prefix
                field_path = field_path.removeprefix("{}").removeprefix(".")  # noqa: PLW2901
                if not field_path:  # Handle case where field_path is just "{}"
                    field_path = ""  # noqa: PLW2901
            nested_object_field_hints[field_path] = hints

        self._object_element_factory = self.__class__(
            nested_object_field_hints,
            field_path=f"{self._field_path}{{}}",
        )

    def _build_dynamic_object(self) -> dict[str, Any] | None:
        """Build dynamic object field with random keys and values."""

        object_key_count = generate_value_from_hints(self._hints)

        if object_key_count is NULL:
            return None

        if not isinstance(object_key_count, int):
            msg = f"unexpected generated value for object key count: {object_key_count}"
            raise TypeError(msg)

        if object_key_count == 0:
            return {}

        if not self._object_element_factory:
            msg = "prepare_dynamic_object did not set object_element_factory"
            raise RuntimeError(msg)

        # Generate keys using available hints and values
        result = {}

        # Get hints for key generation (exclude metadata and control hints)
        key_hints = [hint for hint in self._hints if hint.type not in {"OBJECT", "NUMBER", "NULL", "MISSING"}]

        for _ in range(object_key_count):
            for _ in range(object_key_count * 2):
                if key_hints:
                    key = generate_value_from_hints(key_hints)
                else:
                    # Fallback to random string generation
                    key = "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                if key not in result:
                    break
            else:
                # Failed to generate new unique key after so many attempts,
                # that's probably enough keys in the object then.
                break

            result[key] = self._object_element_factory.build()

        return result

    def _prepare_object(self) -> None:
        for field_path, field_path_hints in self._children.items():
            child_field_path = f"{self._field_path}.{field_path}" if self._field_path else field_path
            self._child_factories[field_path] = self.__class__(
                field_path_hints,
                field_path=child_field_path,
            )

    def _build_object(self) -> dict[str, Any] | None:
        """Build object with child fields."""

        # Check if this field has self hints
        # If so, process them first - they might return NULL
        if self._hints:
            self_value = generate_value_from_hints(self._hints)
            if self_value is NULL:
                return None

        # Otherwise, build the object.
        result: dict[str, Any] = {}
        for field_path, factory in self._child_factories.items():
            value = factory.build()
            if value is not MISSING:
                if value is NULL:
                    raise NotImplementedError(field_path, value)
                result[field_path] = value
        return result

    def _build_leaf(self) -> Any:
        """Build leaf field with no children (e.g. number, bool, string)."""
        result = generate_value_from_hints(self._hints)
        if result is NULL:
            return None
        return result


def load_factory_spec(spec: str | Path | dict[str, Any]) -> FactorySpec:
    if isinstance(spec, Path):
        spec_data = json.loads(spec.read_text())
    elif isinstance(spec, str):
        spec_data = json.loads(Path(spec).read_text())
    else:
        spec_data = spec

    # Convert spec format to field hints format
    field_hints: FieldHints = {}
    for field_path, hints_data in spec_data["fields"].items():
        field_hints[field_path] = create_hints_from_spec_format(hints_data)

    return FactorySpec(field_hints)


def _parse_field_paths(
    field_hints: FieldHints,
) -> tuple[Hints, dict[str, FieldHints]]:
    """
    Parse field paths for recursive processing.

    Args:
        field_hints: Dictionary mapping field paths to hint lists

    Returns:
        Tuple of (current_hints, children_dict) where:
        - current_hints: Hints for the current level (empty string key)
        - children_dict: Nested dict of child field hints grouped by immediate child
    """
    current = []
    children: dict[str, dict[str, list[AnalysisHint]]] = {}

    for field_path, hints in field_hints.items():
        if field_path == "":
            current.extend(hints)
        else:
            child_name, remainder = _parse_field_path_components(field_path)

            # Initialize child dict if needed
            if child_name not in children:
                children[child_name] = {}

            # Add to child's field paths
            children[child_name][remainder] = hints

    return current, children


def _parse_field_path_components(field_path: str) -> tuple[str, str]:
    """Parse a field path into child name and remainder.

    Args:
        field_path: Field path to parse

    Returns:
        Tuple of (child_name, remainder)
    """
    # Handle special cases first
    if field_path in ("[]", "{}"):
        return "", field_path

    # Find delimiter positions
    positions = _find_delimiter_positions(field_path)

    if not positions:
        return field_path, ""

    # Find the earliest position and split accordingly
    positions.sort(key=lambda x: x[0])
    _first_pos, first_type = positions[0]

    return _split_by_delimiter_type(field_path, first_type)


def _find_delimiter_positions(field_path: str) -> list[tuple[int, str]]:
    """Find positions of delimiters in field path."""
    positions = []

    dot_pos = field_path.find(".")
    if dot_pos != -1:
        positions.append((dot_pos, "dot"))

    bracket_pos = field_path.find("[]")
    if bracket_pos != -1:
        positions.append((bracket_pos, "bracket"))

    brace_pos = field_path.find("{}")
    if brace_pos != -1:
        positions.append((brace_pos, "brace"))

    return positions


def _split_by_delimiter_type(field_path: str, delimiter_type: str) -> tuple[str, str]:
    """Split field path by delimiter type."""
    if delimiter_type == "dot":
        child_name, remainder = field_path.split(".", 1)
    elif delimiter_type == "bracket":
        child_name, remainder = field_path.split("[]", 1)
        remainder = "[]" + remainder
    else:  # delimiter_type == "brace"
        child_name, remainder = field_path.split("{}", 1)
        remainder = "{}" + remainder

    return child_name, remainder
