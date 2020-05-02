#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="easyselenium",
    version="0.4",
    description="Easy Selenium - Selenium-based Test Automation Framework",
    author="Kirill Strelkov",
    author_email="kirillstrelkov@users.noreply.github.com",
    url="https://github.com/kirillstrelkov/easyselenium",
    packages=[
        "easyselenium",
        "easyselenium.ui",
        "easyselenium.ui.editor",
        "easyselenium.ui.generator",
        "easyselenium.ui.widgets",
        "easyselenium.ui.widgets.image",
        "easyselenium.ui.selector_finder",
        "easyselenium.ui.parser",
    ],
    python_requires=">=3.6",
    scripts=[
        "easyselenium/scripts/easyselenium_cli.py",
        "easyselenium/scripts/easyselenium_ui.py",
    ],
    requires=["selenium", "wxPython", "pytest", "pytest_html"],
)
