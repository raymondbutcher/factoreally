"""Main entry point for the factoreally package."""

import warnings

from factoreally.cli import cli

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    cli()
