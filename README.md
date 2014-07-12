easyselenium
============
Simple selenium wrapper for most of selenium command.
Supports Firefox, Chrome, IE and Opera.
Suits for novice users.

Usage
-----
```python
>>> from selenium.webdriver.common.by import By
>>> from easyselenium.browser import Browser
>>> browser = Browser('ff')
>>> browser.get('http://www.google.com')
>>> input = (By.NAME, 'q') # input element
>>> search_btn = (By.NAME, 'btnG') # search button element
>>> result = (By.CSS_SELECTOR, '.r') # found
>>> browser.type(input, u'selenium')
>>> browser.click(search_btn)
>>> browser.get_text(result)
u'Selenium - Web Browser Automation'
>>> browser.quit() # closing browser
```

Check []browser_test.py for more examples.

Installation
------------
1. Install selenium if is not installed
```shell
$ sudo pip install selenium
```
2. Download `easyselenium` and unpack
3. Go to `easyselenium` folder and install with command:
```shell
$ sudo python setup install
```
