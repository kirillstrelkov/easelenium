# easelenium

[![Test](https://github.com/kirillstrelkov/easelenium/actions/workflows/test.yml/badge.svg?branch=master&event=push)](https://github.com/kirillstrelkov/easelenium/actions/workflows/test.yml)

Selenium WebDriver wrapper and GUI toolkit for test automation. Provides a high-level `Browser` API, the [PageObject pattern](https://selenium-python.readthedocs.io/page-objects.html), and an optional wxPython GUI for generating and running tests without writing boilerplate.

**Features:**

- Supports Firefox, Chrome, and Edge
- PageObject pattern with code generation
- Context manager and decorator APIs for browser lifecycle
- Optional wxPython GUI (Generator, Editor, Test Runner tabs)
- CI-friendly CLI wrapper around pytest
- Python 3.8+

---

## Installation

### Pip

```shell
pip install easelenium           # library only
pip install "easelenium[gui]"    # with GUI
```

### With uv

```shell
uv add easelenium           # library only
uv add "easelenium[gui]"    # with GUI
```

---

## Usage

### Direct API

```python
from easelenium.browser import Browser
from selenium.webdriver.common.by import By

browser = Browser("gc")                          # gc=Chrome, ff=Firefox, edge=Edge
browser.get("https://duckduckgo.com")
browser.type(by_name="q", text="selenium")
browser.click(by_id="search_button_homepage")
print(browser.get_text(by_css="h2.result__title"))
browser.quit()
```

Most `Browser` methods accept either a `WebElement`, `by_*=` or a `(By, selector)` tuple:

```python
search_input = (By.NAME, "q")
browser.type(search_input, text="selenium")
browser.click((By.ID, "search_button_homepage"))
```

### Context manager

```python
from easelenium.browser import browser_context

with browser_context("gc", headless=True) as browser:
    browser.get("https://duckduckgo.com")
    print(browser.get_title())
# browser.quit() called automatically; screenshot saved on exception
```

### Decorator

```python
from easelenium.browser import browser_decorator

@browser_decorator(browser_name="gc", headless=True)
def run_search(browser=None):
    browser.get("https://duckduckgo.com")
    browser.type(by_name="q", text="selenium")
```

### PageObject pattern

```python
from selenium.webdriver.common.by import By
from easelenium.base_page_object import BasePageObject

class DuckDuckGo(BasePageObject):
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.ID, "search_button_homepage")

    def search(self, text):
        self.browser.get("https://duckduckgo.com")
        self.browser.type(self.SEARCH_INPUT, text=text)
        self.browser.click(self.SEARCH_BUTTON)
```

### Test base class

```python
from easelenium.base_test import BaseTest

class MyTest(BaseTest):
    BROWSER_NAME = "gc"

    def test_title(self):
        self.browser.get("https://duckduckgo.com")
        assert "DuckDuckGo" in self.browser.get_title()
```

`BaseTest` handles browser setup/teardown and saves a screenshot on failure.

---

## GUI

Requires the `[gui]` extra. Launch with:

```shell
easelenium_ui
# or
python easelenium/scripts/easelenium_ui.py
```

| Tab             | Purpose                                            |
| --------------- | -------------------------------------------------- |
| Generator       | Open a URL, click elements, emit PageObject source |
| Editor          | Edit generated PageObject files                    |
| Selector Finder | Interactively test CSS/XPath selectors             |
| Test Runner     | Run pytest suites and view results                 |

---

## CLI (CI)

```shell
easelenium_cli --browser GC tests/
# or
python easelenium/scripts/easelenium_cli.py --browser GC tests/
```

Wraps pytest and injects the chosen browser into fixtures via a pytest plugin.

---

## Development

Requires [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just).

```shell
just init        # create .venv and install dependencies
just fmt         # ruff format
just fix         # ruff check --fix + pyright
just test        # run pytest
just bump minor  # bump version and create git tag (major / minor / patch)
```

On Linux, run tests with a virtual display:

```shell
xvfb-run --server-args="-screen 0 1366x768x24" pytest tests/
```

---

## Dependencies

| Package              | Role                               |
| -------------------- | ---------------------------------- |
| selenium             | WebDriver core                     |
| webdriver-manager    | Auto-download browser drivers      |
| loguru               | Logging                            |
| pytest / pytest-html | Test runner                        |
| wxPython             | GUI (optional — `easelenium[gui]`) |

---

## License

MIT — [easelenium/licenses/easelenium_license.txt](/easelenium/licenses/easelenium_license.txt)

---

## Tutorial

1. [Introduction](https://kirillstrelkov.blogspot.de/2016/03/test-automation-with-selenium-webdriver.html)
2. [Setup](https://kirillstrelkov.blogspot.de/2016/03/test-automation-with-selenium-webdriver_28.html)
3. [Test creation](https://kirillstrelkov.blogspot.de/2016/03/test-automation-tutorial-with-selenium.html)
4. [Continuous Integration](https://kirillstrelkov.blogspot.com/2018/04/test-automation-tutorial-with-selenium.html)

## More information

[Presentation](https://www.dropbox.com/s/4y877giru9qwx3b/present_Kirill_Strelkov.pdf?dl=0)

[Thesis which contains description of the framework](https://www.dropbox.com/s/l65o69wvzjf1bue/Kirill_Strelkov_073639_BAK.pdf?dl=0)
