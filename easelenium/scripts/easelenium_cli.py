#!/usr/bin/env python3

"""Easelenium command line tool."""

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append((Path(__file__).parent / "../..").as_posix())

from easelenium.browser import Browser  # noqa: E402


class EaseleniumPlugin:
    """easelenium pytest plugin."""

    def pytest_addoption(self, parser: Any) -> None:  # noqa: D102, ANN401
        group = parser.getgroup("easelenium")
        group.addoption(
            "--browser",
            dest="BROWSER",
            help="Specify browser by using initials. "
            "If value was not passed then 'ff' will be used. ",
            choices=Browser.get_supported_browsers(),
        )

    def pytest_configure(self, config: Any) -> None:  # noqa: D102, ANN401
        Browser.DEFAULT_BROWSER = config.option.BROWSER


def main() -> None:
    """Run pytest with easelenium plugin."""
    sys.exit(pytest.main(plugins=[EaseleniumPlugin()]))


if __name__ == "__main__":
    main()
