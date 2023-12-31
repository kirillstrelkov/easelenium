"""Setup tools."""
from pathlib import Path

from setuptools import setup

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="easelenium",
    version="0.7.0",
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
    requires=[
        "wheel",
        "selenium",
        "attrdict3",
        "wxPython",
        "pytest",
        "pytest_html",
        "loguru",
        "webdriver-manager",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
