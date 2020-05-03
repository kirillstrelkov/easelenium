#!/usr/bin/env python3

from os import path
from setuptools import setup


with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="easyselenium",
    version="0.4.2",
    description="easyselenium - Selenium-based Test Automation Framework",
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
    long_description=long_description,
    long_description_content_type="text/markdown",
)
