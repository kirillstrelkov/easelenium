# easelenium

[![Test](https://github.com/kirillstrelkov/easelenium/actions/workflows/test.yml/badge.svg?branch=master&event=push)](https://github.com/kirillstrelkov/easelenium/actions/workflows/test.yml)

Framework based on Selenium WebDriver. Contains wrapper around Selenium WebDriver functionaly and UI to facilitate in development.

Features:

- Supports Firefox, Chrome, IE, Opera and PhantomJS.
- Supports [PageObject pattern](https://code.google.com/p/selenium/wiki/PageObjects)
- Supports Continuous Integration
- Suits for novice users.
- Supports only Python 3.8+(for older python versions check [0.3](https://github.com/kirillstrelkov/easelenium/releases/tag/0.3) tag)

Framework can be used as standalone framework with UI and/or as a library.
Supportive classes:

- [browser.py](/easelenium/browser.py)
- [base_page_object.py](/easelenium/base_page_object.py)
- [base_test.py](/easelenium/base_test.py)

GUI [easelenium_ui](/easelenium/scripts/easelenium_ui.py):

- Generator
- Editor
- Test runner

## Dependencies

1. Python
2. wxPython
3. Selenium WebDriver
4. pytest
5. pytest-html
6. pytest-dotenv
7. loguru

## Simple usage

Most of `Browser` functions support both `WebElement` object and tuple/list which represents html element. This tuple/list object should contain selector/locator as first element and value as a second element. Example: `input = (By.NAME, 'q')`

Here is simple example:

```python
>>> from easelenium.browser import Browser

>>> browser = Browser('gc') # create browser

>>> browser.get('https://www.duckduckgo.com') # go to page

>>> browser.type(by_name='q', text='selenium') # type 'selenium' into search field

>>> browser.click(by_id='search_button_homepage') # click search button

>>> browser.get_text(by_css='h2.result__title') # get first result title
'SeleniumHQ Browser Automation'

>>> browser.quit() # close browser
```

Check [browser_test.py](/easelenium/test/browser_test.py) for more examples.

## Continuous Integration

Done via command line script [easelenium_cli](/easelenium/scripts/easelenium_cli.py)

## Installation

### Using `pip`

```shell
pip install easelenium
```

### Manual

1. Download latest code from GitHub
2. Extract it
3. Open terminal or command line console
4. Navigate to extracted folder
5. Install all required libraries

   ```shell
   python -m pip install -r requirements.txt
   ```

6. Go to `easelenium` folder and install with command:

   ```shell
   python setup.py install
   ```

## License

MIT License [easelenium_license.txt](/easelenium/licenses/easelenium_license.txt)

## Tutorial

1. [Introduction](https://kirillstrelkov.blogspot.de/2016/03/test-automation-with-selenium-webdriver.html)
2. [Setup](https://kirillstrelkov.blogspot.de/2016/03/test-automation-with-selenium-webdriver_28.html)
3. [Test creation](https://kirillstrelkov.blogspot.de/2016/03/test-automation-tutorial-with-selenium.html)
4. [Continuous Integration](https://kirillstrelkov.blogspot.com/2018/04/test-automation-tutorial-with-selenium.html)

## More information

[Presentation](https://www.dropbox.com/s/4y877giru9qwx3b/present_Kirill_Strelkov.pdf?dl=0)

[Thesis which contains description of the framework](https://www.dropbox.com/s/l65o69wvzjf1bue/Kirill_Strelkov_073639_BAK.pdf?dl=0)
