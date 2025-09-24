# Factoreally Development Guidelines

This document contains development guidelines and best practices for the Factoreally project - a Python data factory generator based on real data analysis.

## Project Overview

Factoreally is a sophisticated data factory system that analyzes real datasets to automatically generate realistic test data. It uses statistical analysis and pattern recognition to create factories that produce data matching the characteristics of your source data.

## Project Structure

### Directory Structure

```
factoreally/
├── analyzers/                  # Data pattern analyzers
│   ├── array_analyzer.py           # Array structure analysis
│   ├── choice_analyzer.py           # Categorical value analysis
│   ├── alphanumeric_analyzer.py     # String pattern analysis
│   ├── number_analyzer.py           # Numeric distribution analysis
│   ├── temporal_pattern_analyzer.py # Date/time pattern analysis
│   ├── structured_pattern_analyzer.py # Complex structure analysis
│   ├── presence_analyzer.py         # Null/missing value analysis
│   └── null_analyzer.py             # Null value distribution
├── hints/                      # Value generation hints
│   ├── choice_hints.py              # Categorical value generators
│   ├── string_hints.py              # String pattern generators
│   ├── numeric_hints.py             # Number generators
│   ├── temporal_hints.py            # Date/time generators
│   ├── common_values_hint.py        # Common value generators
│   └── length_hint.py               # Length-based generators
├── spec/                       # Factory specification management
│   ├── create.py                    # Spec creation from analysis
│   ├── load.py                      # Spec loading and parsing
│   ├── extract.py                   # Data extraction utilities
│   └── build.py                     # Spec-based factory building
└── build.py                   # Main Factory class (public API)

tests/                         # Test suite
├── analyzers/                     # Analyzer tests
├── builder/                       # Factory builder tests
├── hints/                         # Hint generator tests
├── spec/                          # Spec management tests
└── test_minimal_array.py          # Integration tests

.github/                       # CI/CD workflows and GitHub config
```

### Architecture Principles

1. **Separation of Concerns**: Analyzers examine data, hints generate values, specs define structure
2. **Composability**: Components can be mixed and matched for different use cases
3. **Type Safety**: Strong typing throughout with mypy strict mode
4. **Statistical Accuracy**: Generated data maintains statistical properties of source data

## Python Coding Standards

### Naming Conventions

1. **Function Names**: Use clear action words
   ```python
   # Avoid - unclear purpose
   def telemetry_middleware(app: FastAPI) -> None:

   # Better - clear action
   def add_telemetry_middleware(app: FastAPI) -> None:
   ```

2. **Module Names**: Use descriptive names that indicate purpose
   ```python
   # Good examples from this project
   temporal_pattern_analyzer.py  # Analyzes temporal patterns
   choice_hints.py              # Provides choice-based hints
   ```

### Code Organization

1. **Try Blocks**: Keep try blocks focused and minimal
   ```python
   # Prefer - single operation
   try:
       data = json.loads(raw_data)
   except json.JSONDecodeError:
       return default_data

   # Avoid - multiple operations that could fail differently
   try:
       data = json.loads(raw_data)
       processed = transform_data(data)
       result = validate_data(processed)
   except Exception:
       return None
   ```

2. **Import Organization**: All imports at top, organized by Ruff
   ```python
   # Standard library
   from __future__ import annotations
   from typing import TYPE_CHECKING, Any

   # Third party
   import numpy as np
   from scipy import stats

   # Local imports
   from factoreally import Factory

   # TYPE_CHECKING imports
   if TYPE_CHECKING:
       from pathlib import Path
   ```

## Type Safety

### Core Principles

- Maximize type safety using validated, typed data structures everywhere except at external boundaries
- Use `mypy --strict` mode to enforce complete type coverage
- Prefer dataclasses over dictionaries for structured data

### Guidelines

1. **Generic Types**: Be specific with type parameters
   ```python
   # Avoid - too generic
   def process_data(items: list) -> dict:
       pass

   # Better - specific types
   def process_data(items: list[AnalysisResult]) -> dict[str, float]:
       pass
   ```

## Testing Strategy

### Framework and Structure

- **pytest** for all tests with strict coverage requirements
- Test structure mirrors source code organization
- Focus on unit tests

### Test Organization

```
tests/
├── analyzers/
│   ├── test_array_analyzer.py
│   ├── test_choice_analyzer.py
│   └── test_temporal_pattern_analyzer.py
├── builder/
│   ├── test_build_factory.py
│   ├── test_factory_enhancements.py
│   └── test_implicit.py
├── hints/
│   ├── test_choice_hints.py
│   ├── test_string_hints.py
│   └── test_temporal_hints.py
└── spec/
    └── test_spec.py
```

### Testing Best Practices

1. **Assertion Patterns**: Test complete objects, not individual properties
   ```python
   # Prefer - complete object assertion
   expected_result = AnalysisResult(
       pattern_type="temporal",
       confidence=0.95,
       metadata={"format": "ISO8601"}
   )
   assert analyzer.analyze(data) == expected_result

   # Avoid - fragmented assertions
   result = analyzer.analyze(data)
   assert result.pattern_type == "temporal"
   assert result.confidence == 0.95
   assert "format" in result.metadata
   ```

2. **Test Data**: Use realistic test data that represents actual use cases
   ```python
   # Good - realistic medical device data
   test_device_data = [
       {"serial": "1234", "model": "ModelA", "status": "active"},
       {"serial": "5678", "model": "ModelB", "status": "maintenance"}
   ]
   ```

## Data Analysis Architecture

### Hint Generation

Hints translate analysis results into value generators:

```python
@dataclass
class Hint:
    generator_type: str
    parameters: dict[str, Any]
    confidence: float

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through this hint using call_next pattern."""
        return call_next(value)
```

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Code Quality
```bash
# Type checking (strict mode enabled)
poetry run mypy .

# Linting (comprehensive ruleset)
poetry run ruff check .

# Format code
poetry run ruff format .
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=factoreally --cov-report=html

# Run specific test module
poetry run pytest tests/analyzers/test_array_analyzer.py

# Run tests matching pattern
poetry run pytest -k "test_temporal"
```

### Development Workflow
```bash
# Complete development check
poetry run mypy . && poetry run ruff check . && poetry run pytest
```

# Additional instructions
- Imports should be at the top of the file, not inside functions.
- Don't put imports inside functions! Put them at the top of the file.
- Always choose to clean up and remove old code, there is never a need to keep old code for backwards compatibility.
- Never add backwards compatibility, always prioritize clean code.
- When asked to add a test, and the test reveals a bug, investigate the bug and propose a fix. Don't alter the test to avoid the bug.
- Tests must be named according to the convention "test_<function>_<scenario>"
- Tests must be located in the right file. The test structure should mirror the source code structure, so if the test's primary function being tested is `build_json_spec` in `factoreally/spec/build.py` then the test should be located in `tests/spec/build/test_build_json_spec.py`
- Don't export names in `__init__.py` unless explicitly requested by the user.
- Do not create unnecessary small functions that are only called once or twice
- Follow the YAGNI principle

# Code quality gate

- Always run `make fmt test` after making code changes.
- Always check mypy, ruff, and pytest for the whole project, not just files you modified.
- All mypy and ruff issues must be addressed. All of them. There are no exceptions.
- Never add ruff rules to the ignore list in pyproject.toml.

If ruff/mypy show existing issues unrelated to your changes:
- You MUST fix them anyway
- You CANNOT proceed with "these were already there"
- The codebase must be clean after every change

CRITICAL: Before marking any task complete, you MUST run and PASS `make fmt test` with zero issues. If that command fails, the task is NOT complete. Fix ALL issues before proceeding. It does not matter if the error appears unrelated to your changes. It is never acceptable for `make fmt test` to fail. NEVER IGNORE THIS.

# Test Failure Policy - ZERO TOLERANCE

NEVER, under ANY circumstances, consider a task complete if ANY tests are failing.

## Forbidden Rationalizations
- ❌ "These test failures are expected due to my changes"
- ❌ "These are integration tests, not related to my work"
- ❌ "The behavior change is correct, so failures are acceptable"
- ❌ "These were failing before I started" (YOU MUST FIX THEM ANYWAY)

## Required Actions for ANY Test Failure
1. STOP immediately - task is NOT complete
2. Analyze each failing test to understand why it's failing
3. Choose ONE of these options:
   - Update test expectations if behavior change is intentional and correct
   - Fix your code if behavior change is unintentional
   - Fix pre-existing bugs revealed by your changes
4. Re-run `make fmt test` until ZERO failures
5. Only then consider task complete

## Accountability Reminder
YOU are responsible for the entire codebase's health, not just your specific changes. Every failing test is YOUR responsibility to resolve before completion.
