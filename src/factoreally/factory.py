"""Factory class for generating realistic test data from specifications."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from factoreally.factory_spec import FactorySpec, load_factory_spec

if TYPE_CHECKING:
    from pathlib import Path

# Type aliases for callable overrides
NoArgsCallable = Callable[[], Any]
ValueCallable = Callable[[Any], Any]
ValueObjectCallable = Callable[[Any, dict[str, Any]], Any]
KeywordCallable = Callable[..., Any]  # For keyword-only variants
OverrideValue = Any | NoArgsCallable | ValueCallable | ValueObjectCallable | KeywordCallable


class Factory:
    """Factory class for generating dictionary data based on factory spec."""

    def __init__(
        self,
        spec: str | Path | dict[str, Any] | FactorySpec,
        /,
        **overrides: OverrideValue,
    ) -> None:
        """Initialize factory with spec data and optional overrides.

        Args:
            spec: Spec data - can be a file path (str), Path object, or already loaded dict
            **overrides: Keyword arguments for field overrides. Use double underscores for nested fields.
                        E.g. metadata__id="fixed-id" sets metadata.id to "fixed-id"
                        E.g. data__0__name="value" sets data[0].name to "value"
        """
        self._factory_spec = spec if isinstance(spec, FactorySpec) else load_factory_spec(spec)
        self._overrides = self._process_overrides(overrides)

    def _process_overrides(
        self,
        override: dict[str, OverrideValue] | None = None,
        /,
        **overrides: OverrideValue,
    ) -> dict[str, OverrideValue]:
        """Convert double-underscore overrides to dot notation field paths with array support.

        Args:
            override: Dictionary with override keys that may contain double underscores
            **overrides: Additional override keyword arguments

        Returns:
            Dictionary with proper field paths as keys
        """
        processed: dict[str, OverrideValue] = {}

        for fields in (override or {}, overrides):
            for key, value in fields.items():
                # Convert double underscores to dots for nested field paths
                field_path = key.replace("__", ".")

                # Handle numeric array indexes: convert "data.0.name" to "data[0].name"
                parts = field_path.split(".")
                processed_parts: list[str] = []
                for part in parts:
                    if part.isdigit():
                        # This is a numeric index, format as array index
                        if processed_parts:
                            processed_parts[-1] = f"{processed_parts[-1]}[{part}]"
                        else:
                            # Edge case: starts with a number (shouldn't happen normally)
                            processed_parts.append(f"[{part}]")
                    else:
                        processed_parts.append(part)

                processed_field_path = ".".join(processed_parts)
                processed[processed_field_path] = value

        return processed

    def _apply_overrides(self, data: dict[str, Any], overrides: dict[str, OverrideValue]) -> dict[str, Any]:
        """Apply override values to generated data.

        Args:
            data: Generated data dictionary
            overrides: Override values to apply (can include callables)

        Returns:
            Data dictionary with overrides applied
        """
        if not overrides:
            return data

        # Create a deep copy to avoid modifying original data
        result = dict(data)

        for field_path, value in overrides.items():
            # Check if value is callable
            if callable(value):
                # Get current field value for the callable
                current_field_value = self._get_nested_value(result, field_path)
                # Resolve the callable to get the actual override value
                resolved_value = self._resolve_callable_override(value, current_field_value, result)
                self._set_nested_value(result, field_path, resolved_value)
            else:
                # Standard override behavior
                self._set_nested_value(result, field_path, value)

        return result

    def _set_nested_value_from_parts(self, data: dict[str, Any], parts: list[str | int], value: Any) -> None:  # noqa: C901,PLR0912
        """Set a nested value using pre-parsed parts list.

        Args:
            data: Target dictionary
            parts: List of path parts (strings and integers for array indices)
            value: Value to set
        """
        if not parts:
            return

        if len(parts) == 1:
            # Final part - set the value
            final_part = parts[0]
            if isinstance(final_part, int):
                if isinstance(data, list):
                    if len(data) <= final_part:
                        data.extend([None for _ in range(final_part + 1 - len(data))])
                    data[final_part] = value
            # Check if data is a list - if so, set property on all elements
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        item[final_part] = value
            elif data is not None:
                # Skip assignment if data is None
                data[final_part] = value
            return

        # Navigate to next level
        current_part = parts[0]
        remaining_parts = parts[1:]

        if isinstance(current_part, int):
            # Array index
            if not isinstance(data, list) or len(data) <= current_part:
                # Can't set array index - skip this override
                return
            if len(data) <= current_part:
                data.extend([{} for _ in range(current_part + 1 - len(data))])
            self._set_nested_value_from_parts(data[current_part], remaining_parts, value)
        else:
            # Object key
            if isinstance(data, list):
                # We hit a list - apply current part and remaining parts to all elements
                current_and_remaining = [current_part, *remaining_parts]
                for item in data:
                    if isinstance(item, dict):
                        self._set_nested_value_from_parts(item, current_and_remaining, value)
                return

            # Normal dict navigation
            # Skip navigation if data is None
            if data is None:
                return

            if current_part not in data:
                # Determine what to create based on next part
                next_part = remaining_parts[0] if remaining_parts else None
                data[current_part] = [] if isinstance(next_part, int) else {}
            self._set_nested_value_from_parts(data[current_part], remaining_parts, value)

    def _set_nested_value(self, data: dict[str, Any], field_path: str, value: Any) -> None:
        """Set a nested value in a dictionary using dot notation and array indexing.

        Args:
            data: Target dictionary
            field_path: Field path like "data.actions[0].type" or "data.actions.type" (for all elements)
            value: Value to set
        """
        if "." not in field_path and "[" not in field_path:
            # Simple top-level field
            data[field_path] = value
            return

        # Parse field path and use the helper method to handle the parsed parts
        parts = self._parse_field_path(field_path)
        self._set_nested_value_from_parts(data, parts, value)

    def _parse_field_path(self, field_path: str) -> list[str | int]:
        """Parse field path into parts, handling array indices.

        Args:
            field_path: Field path like "data.actions[0].type"

        Returns:
            List of path parts (strings and integers for array indices)
        """
        parts: list[str | int] = []
        current_part = ""
        i = 0
        while i < len(field_path):
            char = field_path[i]
            if char == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif char == "[":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # Find the closing bracket
                j = i + 1
                while j < len(field_path) and field_path[j] != "]":
                    j += 1
                if j < len(field_path):
                    index_str = field_path[i + 1 : j]
                    if index_str.isdigit():
                        parts.append(int(index_str))
                    i = j
                else:
                    current_part += char
            else:
                current_part += char
            i += 1

        if current_part:
            parts.append(current_part)

        return parts

    def _get_nested_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Get a nested value from a dictionary using dot notation and array indexing.

        Args:
            data: Source dictionary
            field_path: Field path like "data.actions[0].type" or "data.actions.type"

        Returns:
            The value at the field path, or None if path doesn't exist
        """
        if "." not in field_path and "[" not in field_path:
            # Simple top-level field
            return data.get(field_path)

        # Parse field path and traverse the data structure
        parts = self._parse_field_path(field_path)
        return self._get_nested_value_from_parts(data, parts)

    def _get_nested_value_from_parts(self, data: dict[str, Any] | list[Any] | Any, parts: list[str | int]) -> Any:
        """Get a nested value using pre-parsed parts list.

        Args:
            data: Current data structure (dict, list, or value)
            parts: List of path parts (strings and integers for array indices)

        Returns:
            The value at the path, or None if path doesn't exist
        """
        if not parts:
            return data

        if len(parts) == 1:
            # Final part - get the value
            final_part = parts[0]
            if isinstance(final_part, int) and isinstance(data, list) and 0 <= final_part < len(data):
                return data[final_part]
            if isinstance(final_part, str) and isinstance(data, dict):
                return data.get(final_part)
            return None

        # Navigate to next level
        current_part = parts[0]
        remaining_parts = parts[1:]

        # Determine next data level based on current part type
        next_data = None
        if (isinstance(current_part, int) and isinstance(data, list) and 0 <= current_part < len(data)) or (
            isinstance(current_part, str) and isinstance(data, dict) and current_part in data
        ):
            next_data = data[current_part]  # type: ignore[index]

        # Recursively process remaining parts if we found valid next data
        return self._get_nested_value_from_parts(next_data, remaining_parts) if next_data is not None else None

    def _raise_unknown_keyword_error(self, param_name: str) -> None:
        """Raise error for unknown keyword parameter.

        Args:
            param_name: Name of the unknown parameter

        Raises:
            TypeError: Always raises for unknown keyword parameter
        """
        msg = f"Unknown keyword parameter '{param_name}'. Only 'value' and 'obj' are supported."
        raise TypeError(msg)

    def _build_keyword_args(
        self,
        keyword_only_params: list[Any],
        field_value: Any,
        entire_object: dict[str, Any],
    ) -> dict[str, Any]:
        """Build keyword arguments for callable override.

        Args:
            keyword_only_params: List of keyword-only parameters
            field_value: Current value of the field being overridden
            entire_object: The entire generated object

        Returns:
            Dictionary of keyword arguments

        Raises:
            TypeError: If unknown keyword parameter found
        """
        kwargs = {}
        for param in keyword_only_params:
            if param.name == "value":
                kwargs["value"] = field_value
            elif param.name == "obj":
                kwargs["obj"] = entire_object
            else:
                self._raise_unknown_keyword_error(param.name)
        return kwargs

    def _call_with_positional_args(
        self,
        callable_override: Callable[..., Any],
        positional_count: int,
        field_value: Any,
        entire_object: dict[str, Any],
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """Call override with positional arguments.

        Args:
            callable_override: The callable to execute
            positional_count: Number of positional parameters
            field_value: Current value of the field being overridden
            entire_object: The entire generated object
            kwargs: Optional keyword arguments

        Returns:
            The computed override value

        Raises:
            TypeError: If too many positional parameters
        """
        if kwargs is None:
            kwargs = {}

        if positional_count == 0:
            return callable_override(**kwargs)
        if positional_count == 1:
            return callable_override(field_value, **kwargs)
        if positional_count == 2:  # noqa: PLR2004
            return callable_override(field_value, entire_object, **kwargs)

        msg = f"Callable override has too many positional parameters ({positional_count}). Maximum is 2."
        raise TypeError(msg)

    def _resolve_callable_override(
        self, callable_override: Callable[..., Any], field_value: Any, entire_object: dict[str, Any]
    ) -> Any:
        """Resolve callable override using standardized signature detection.

        Args:
            callable_override: The callable to execute
            field_value: Current value of the field being overridden
            entire_object: The entire generated object

        Returns:
            The computed override value

        Raises:
            TypeError: If callable has invalid signature
        """
        sig = inspect.signature(callable_override)
        params = list(sig.parameters.values())

        # Count positional parameters (exclude keyword-only)
        positional_count = sum(1 for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))
        keyword_only_params = [p for p in params if p.kind == p.KEYWORD_ONLY]

        # Handle keyword-only parameters if present
        if keyword_only_params:
            kwargs = self._build_keyword_args(keyword_only_params, field_value, entire_object)
            return self._call_with_positional_args(
                callable_override,
                positional_count,
                field_value,
                entire_object,
                kwargs,
            )

        # Handle positional-only parameters
        return self._call_with_positional_args(
            callable_override,
            positional_count,
            field_value,
            entire_object,
        )

    def build(
        self,
        override: dict[str, OverrideValue] | None = None,
        /,
        **overrides: OverrideValue,
    ) -> dict[str, Any]:
        """Generate a dictionary with realistic data and optional overrides.

        Args:
            override: Dictionary of field path overrides
            **overrides: Keyword arguments for field overrides. Use double underscores for nested fields.

        Returns:
            Generated dictionary with overrides applied
        """
        # Generate base data using FactorySpec
        data = self._factory_spec.build()

        # Process and combine all overrides
        combined_overrides = self._overrides | self._process_overrides(override, **overrides)

        # Apply overrides to the generated data
        return self._apply_overrides(data, combined_overrides)

    def copy(
        self,
        override: dict[str, OverrideValue] | None = None,
        /,
        **overrides: OverrideValue,
    ) -> Factory:
        """Create a copy of the factory with additional overrides built in.

        Args:
            override: Dictionary of field path overrides
            **overrides: Keyword arguments for field overrides. Use double underscores for nested fields.

        Returns:
            New Factory instance with combined overrides
        """
        # Create new factory with same spec but no initial overrides
        new_factory = self.__class__(self._factory_spec)

        # Combine existing overrides with new ones
        combined_overrides = self._overrides | self._process_overrides(override, **overrides)
        new_factory._overrides = combined_overrides  # noqa: SLF001

        return new_factory

    def __getitem__(self, key: Any) -> list[dict[str, Any]]:
        """Return dictionaries using slice indexing."""
        # Validate input immediately (before creating generator)
        if not isinstance(key, slice):
            msg = "Only slice indexing is supported"
            raise TypeError(msg)

        if key.stop is None:
            msg = "Slice stop value is required"
            raise TypeError(msg)

        return [self.build() for _ in range(key.start or 0, key.stop, key.step or 1)]

    def __iter__(self) -> Factory:
        """Return self as iterator for infinite generation."""
        return self

    def __next__(self) -> dict[str, Any]:
        """Generate next dictionary for iteration."""
        return self.build()
