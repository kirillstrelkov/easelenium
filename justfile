set shell := ["bash", "-c"]

all: fmt fix clean

fmt:
	uv run ruff format

fix:
	uv run ruff check --fix
	uv run pyright

clean:
	uv run ruff clean
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .ipynb_checkpoints -exec rm -r {} +

init:
	rm -rf .venv || true
	uv sync --no-install-project

test:
    uv run pytest
