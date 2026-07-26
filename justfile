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

test-ci:
	xvfb-run --server-args="-screen 0 1366x768x24" uv run pytest --retries 10 tests

bump part="patch":
    uv version --bump {{part}}
    git tag "$(uv version --short)"

install-wx-u24:
	uv pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-24.04 wxPython
