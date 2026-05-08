set shell := ["bash", "-c"]

all: fmt fix clean

fmt:
	ruff format

fix:
	ruff check --fix --unsafe-fixes

clean:
	ruff clean
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .ipynb_checkpoints -exec rm -r {} +


init:
	env | grep PYTHON
	rm -rf .venv || true
	uv venv --no-project
	source .venv/bin/activate
	which python
	uv pip install -r requirements.txt

test:
    uv run pytest
