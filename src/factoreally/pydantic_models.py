"""Pydantic model analysis for dynamic field detection."""

from __future__ import annotations

import importlib
import inspect
from typing import Any, ForwardRef, get_args, get_origin

import click
from pydantic import BaseModel


def analyze_pydantic_model(model_class: type[BaseModel]) -> set[str]:
    """Analyze a Pydantic model to detect fields with dynamic keys.

    Identifies fields that are dict types with any key type,
    which indicate dynamic object keys that should use ObjectHint.

    Args:
        model_class: Pydantic BaseModel class to analyze

    Returns:
        Set of field paths that should be treated as dynamic objects
    """
    dynamic_fields: set[str] = set()

    # Get the model fields
    model_fields = model_class.model_fields

    for field_name, field_info in model_fields.items():
        field_annotation = field_info.annotation

        json_field_name = field_info.alias or field_name

        # Check if this field is a dictionary type with string keys
        if _is_dynamic_dict_field(field_annotation):
            dynamic_fields.add(json_field_name)

        # Handle nested models recursively
        nested_model_class = _resolve_nested_model(field_annotation, model_class)
        if nested_model_class:
            nested_dynamic_fields = analyze_pydantic_model(nested_model_class)
            for nested_field in nested_dynamic_fields:
                dynamic_fields.add(f"{json_field_name}.{nested_field}")

    return dynamic_fields


def _is_dynamic_dict_field(annotation: Any) -> bool:
    """Check if a field annotation represents a dynamic dictionary.

    Args:
        annotation: Type annotation to check

    Returns:
        True if the annotation represents any dict type or RootModel with dict root type
    """
    origin = get_origin(annotation)

    # Any dict type should be considered dynamic
    if origin is dict:
        return True

    # Check for Union types (e.g., dict[str, str] | None)
    if origin is not None:
        args = get_args(annotation)
        for arg in args:
            # Skip None type in Union
            if arg is type(None):
                continue
            # Recursively check if any Union argument is a dynamic dict
            if _is_dynamic_dict_field(arg):
                return True

    # Check for RootModel with dynamic dict root type
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        # Check if it's a RootModel (has 'root' field)
        if hasattr(annotation, "model_fields") and "root" in annotation.model_fields:
            root_field = annotation.model_fields["root"]
            root_annotation = root_field.annotation
            # Recursively check if root type is a dynamic dict
            return _is_dynamic_dict_field(root_annotation)

    # Check for Dict from typing module
    return hasattr(annotation, "__name__") and annotation.__name__ == "Dict"


def _resolve_nested_model(annotation: Any, parent_model: type[BaseModel]) -> type[BaseModel] | None:
    """Resolve a nested model type from annotation.

    Args:
        annotation: Type annotation which might be a BaseModel
        parent_model: Parent model class for resolving forward references

    Returns:
        BaseModel class if annotation represents a nested model, None otherwise
    """
    # Direct type reference
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation

    # Handle Union types (e.g., BaseModel | None)
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        for arg in args:
            # Skip None type in Union
            if arg is type(None):
                continue
            # Recursively check if any Union argument is a BaseModel
            nested_model = _resolve_nested_model(arg, parent_model)
            if nested_model:
                return nested_model

    # Handle ForwardRef objects
    if isinstance(annotation, ForwardRef):
        forward_ref_str = annotation.__forward_arg__
        return _resolve_nested_model(forward_ref_str, parent_model)

    # Forward reference as string
    if isinstance(annotation, str):
        return _resolve_string_reference(annotation, parent_model)

    return None


def _resolve_string_reference(annotation: str, parent_model: type[BaseModel]) -> type[BaseModel] | None:
    """Resolve a string annotation to a BaseModel type.

    Args:
        annotation: String name of the model class
        parent_model: Parent model class for context

    Returns:
        BaseModel class if found, None otherwise
    """
    # Try to resolve from parent model's module
    resolved_type = _resolve_from_module(annotation, parent_model)
    if resolved_type:
        return resolved_type

    # Try to resolve from calling frame globals (for testing)
    return _resolve_from_frame_globals(annotation)


def _resolve_from_module(annotation: str, parent_model: type[BaseModel]) -> type[BaseModel] | None:
    """Resolve annotation from parent model's module."""
    if not hasattr(parent_model, "__annotations__"):
        return None

    model_module = parent_model.__module__
    if model_module in globals():
        module_globals = globals()[model_module]
    else:
        try:
            module = importlib.import_module(model_module)
            module_globals = vars(module)
        except ImportError:
            return None

    if annotation in module_globals:
        resolved_type = module_globals[annotation]
        if isinstance(resolved_type, type) and issubclass(resolved_type, BaseModel):
            return resolved_type

    return None


def _resolve_from_frame_globals(annotation: str) -> type[BaseModel] | None:
    """Resolve annotation from calling frame globals (mainly for testing)."""
    try:
        # Get the calling frame (skip this function and the one that called it)
        for frame_info in inspect.stack()[2:4]:  # Check 2 frames up
            frame_globals = frame_info.frame.f_globals
            if annotation in frame_globals:
                resolved_type = frame_globals[annotation]
                if isinstance(resolved_type, type) and issubclass(resolved_type, BaseModel):
                    return resolved_type
    except (AttributeError, TypeError, IndexError):
        pass
    return None


def import_pydantic_model(import_path: str) -> type[BaseModel]:
    """Import a Pydantic model from a Python import path.

    Args:
        import_path: Python import path in format 'module.path.ClassName'

    Returns:
        The imported Pydantic BaseModel class

    Raises:
        click.ClickException: If import fails or class is not a valid Pydantic model
    """
    # Minimum number of parts required for a valid import path
    min_import_path_parts = 2

    try:
        # Split the import path to separate module from class name
        module_parts = import_path.split(".")
        if len(module_parts) < min_import_path_parts:
            msg = f"Invalid import path '{import_path}'. Expected format: 'module.path.ClassName'"
            raise click.ClickException(msg)  # noqa: TRY301

        class_name = module_parts[-1]
        module_path = ".".join(module_parts[:-1])

        # Import the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            msg = f"Cannot import module '{module_path}': {e}"
            raise click.ClickException(msg) from e

        # Get the class from the module
        try:
            model_class = getattr(module, class_name)
        except AttributeError as e:
            msg = f"Class '{class_name}' not found in module '{module_path}': {e}"
            raise click.ClickException(msg) from e

        # Validate that it's a Pydantic BaseModel
        if isinstance(model_class, type) and issubclass(model_class, BaseModel):
            return model_class

        msg = f"'{import_path}' is not a Pydantic BaseModel class"
        raise click.ClickException(msg)  # noqa: TRY301

    except click.ClickException:
        # Re-raise click exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        msg = f"Unexpected error importing '{import_path}': {e}"
        raise click.ClickException(msg) from e
