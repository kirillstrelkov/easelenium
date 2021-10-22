#!/usr/bin/env python3

from os import path

from setuptools import setup

with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="easelenium",
    version="0.6.3",
    description="easelenium - Selenium-based Test Automation Framework",
    author="Kirill Strelkov",
    author_email="kirillstrelkov@users.noreply.github.com",
    url="https://github.com/kirillstrelkov/easelenium",
    packages=[
        "easelenium",
        "easelenium.ui",
        "easelenium.ui.editor",
        "easelenium.ui.generator",
        "easelenium.ui.widgets",
        "easelenium.ui.widgets.image",
        "easelenium.ui.selector_finder",
        "easelenium.ui.parser",
    ],
    python_requires=">=3.6",
    scripts=[
        "easelenium/scripts/easelenium_cli.py",
        "easelenium/scripts/easelenium_ui.py",
    ],
    requires=["wheel", "selenium", "wxPython", "pytest", "pytest_html", "loguru"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
