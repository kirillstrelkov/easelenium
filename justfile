set shell := ["bash", "-c"]

all: fmt fix clean

fmt:
	ruff format

fix:
	ruff check --fix

clean:
	ruff clean
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .ipynb_checkpoints -exec rm -r {} +


init:
	rm -rf .venv || true
	uv sync --no-install-project

test:
    uv run pytest
