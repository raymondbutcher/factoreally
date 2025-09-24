"""Command line interface for Factoreally."""

import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import click

from factoreally.create_spec import create_spec
from factoreally.pydantic_models import import_pydantic_model


@click.group()
def cli() -> None:
    """Factoreally - Generate realistic test data from production patterns."""


@cli.command()
@click.option(
    "--in",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the JSON data file to analyze",
)
@click.option(
    "--out",
    "output_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Path for the generated JSON factory spec file",
)
@click.option(
    "--model",
    type=str,
    help="Python import path for Pydantic model (e.g., 'mypackage.models.MyModel')",
)
def create(input_path: Path, output_path: Path, model: str | None = None) -> None:
    """Create a factory specification from sample data.

    Loads sample data, runs analysis, and writes the
    generated factory spec to the specified output file.
    """
    # Load sample data from JSON file
    file_size_mb = input_path.stat().st_size / (1024 * 1024)
    click.secho(f"Loading {input_path.name} ({file_size_mb:.1f}MB)", fg="blue")

    with input_path.open() as f:
        items = json.load(f)

    # Import Pydantic model if provided
    pydantic_model = None
    if model is not None:
        pydantic_model = import_pydantic_model(model)
        click.secho(f"Using model: {model}", fg="blue")

    # Run analysis on the loaded items
    start_time = time.time()
    json_spec = create_spec(items, model=pydantic_model)

    # Display analysis results (CLI-specific)
    _display_analysis_results(json_spec, start_time, len(items))

    # Write the spec to file
    click.echo()
    click.echo("Writing factory specification file...")
    output_path.write_text(json.dumps(json_spec, indent=2, default=_json_serializer))

    # Calculate file size of the generated spec file
    output_file_size_mb = output_path.stat().st_size / (1024 * 1024)
    click.secho(f"Saved to: {output_path.name} ({output_file_size_mb:.1f}MB)", fg="green", bold=True)


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for complex objects (same logic as SpecGenerator)."""
    if isinstance(obj, Counter | defaultdict):
        return dict(obj)
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def _display_analysis_results(json_spec: dict[str, Any], start_time: float, item_count: int) -> None:
    """Display analysis results and performance metrics."""
    # Calculate performance metrics
    end_time = time.time()
    total_time = end_time - start_time
    items_per_sec = item_count / total_time if total_time > 0 else 0

    # Get stats from the spec
    metadata = json_spec.get("metadata", {})
    unique_fields = metadata.get("unique_fields", 0)
    total_data_points = metadata.get("total_data_points", 0)
    samples_analyzed = metadata.get("samples_analyzed", item_count)

    click.echo()
    click.secho("=" * 60, fg="green")
    click.secho("ANALYSIS COMPLETE", fg="green", bold=True)
    click.secho("=" * 60, fg="green")

    # Core metrics
    click.secho(f"Items analyzed: {samples_analyzed:,}", fg="cyan")
    click.secho(f"Unique fields: {unique_fields:,}", fg="cyan")
    click.secho(f"Total data points: {total_data_points:,}", fg="cyan")

    # Performance metrics
    click.echo()
    click.secho("Performance Metrics:", fg="magenta", bold=True)
    click.secho(f"  • Total processing time: {total_time:.2f}s", fg="yellow")
    click.secho(f"  • Processing rate: {items_per_sec:.1f} items/sec", fg="yellow")
    if unique_fields > 0:
        fields_per_sec = unique_fields / total_time if total_time > 0 else 0
        click.secho(f"  • Field analysis rate: {fields_per_sec:.1f} fields/sec", fg="yellow")


if __name__ == "__main__":
    cli()
