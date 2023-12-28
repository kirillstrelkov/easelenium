#!/usr/bin/env python3

import os
import sys

from pytest import main

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from easelenium.browser import Browser


class easeleniumPlugin:
    def pytest_addoption(self, parser):
        group = parser.getgroup("easelenium")
        group.addoption(
            "--browser",
            dest="BROWSER",
            help="Specify browser by using initials. If value was not passed then 'ff' will be used. ",
            choices=Browser.get_supported_browsers(),
        )

    def pytest_configure(self, config):
        Browser.DEFAULT_BROWSER = config.option.BROWSER


if __name__ == "__main__":
    sys.exit(main(plugins=[easeleniumPlugin()]))
