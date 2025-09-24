.PHONY: all
all: install fmt test

.PHONY: fmt
fmt:
	uv run ruff format .
	uv run ruff check . --fix
	uv run mypy .
	uv run ruff check .

.PHONY: install
install:
	uv sync --all-extras --dev

.PHONY: test
test:
	uv run pytest -vv
