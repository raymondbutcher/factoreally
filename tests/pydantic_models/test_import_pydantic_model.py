"""Tests for import_pydantic_model function."""

import click
import pytest

from factoreally.pydantic_models import import_pydantic_model

from .conftest import SimpleModel


def test_import_pydantic_model_valid() -> None:
    """Test importing a valid Pydantic model."""
    # Use the conftest SimpleModel as a test case
    model_path = "tests.pydantic_models.conftest.SimpleModel"
    imported_model = import_pydantic_model(model_path)

    assert imported_model == SimpleModel
    assert issubclass(imported_model, SimpleModel)


def test_import_pydantic_model_invalid_path() -> None:
    """Test importing with invalid import path format."""
    with pytest.raises(click.ClickException, match="Invalid import path"):
        import_pydantic_model("InvalidPath")


def test_import_pydantic_model_module_not_found() -> None:
    """Test importing from non-existent module."""
    with pytest.raises(click.ClickException, match="Cannot import module"):
        import_pydantic_model("nonexistent.module.Model")


def test_import_pydantic_model_class_not_found() -> None:
    """Test importing non-existent class from valid module."""
    with pytest.raises(click.ClickException, match=r"Class .* not found"):
        import_pydantic_model("tests.pydantic_models.conftest.NonExistentModel")


def test_import_pydantic_model_not_basemodel() -> None:
    """Test importing class that is not a BaseModel."""
    with pytest.raises(click.ClickException, match="not a Pydantic BaseModel"):
        # Try to import a non-BaseModel class - use str as example
        import_pydantic_model("builtins.str")
