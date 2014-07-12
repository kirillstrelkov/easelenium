easyselenium
============
Simple selenium wrapper for most of selenium command.
* Supports Firefox, Chrome, IE and Opera.
* Suits for novice users.

Usage
-----
Main idea - each element should contains selector/locator as first element and value as a second element.
Example: `input = (By.NAME, 'q')`

Here is simple example: 
```python
>>> from selenium.webdriver.common.by import By
>>> from easyselenium.browser import Browser
>>> browser = Browser('ff') # initilizing browser
>>> browser.get('http://www.google.com') # going to google
>>> # creating variables for page elements:
>>> input = (By.NAME, 'q') # input element
>>> search_btn = (By.NAME, 'btnG') # search button element
>>> result = (By.CSS_SELECTOR, '.r') # found results titles' elements
>>> browser.type(input, u'selenium') # typing 'selenium' into search field
>>> browser.click(search_btn) # clicking search button
>>> browser.get_text(result) # getting first found title
u'Selenium - Web Browser Automation'
>>> browser.quit() # closing browser
```

Check [browser_test.py](/ambi7ks/easyselenium/easyselenium/browser_test.py) for more examples.

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
