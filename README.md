easyselenium
============
Simple selenium wrapper. Easies and expands selenium functionality.
* Supports Firefox, Chrome, IE and Opera.
* Supports [PageObject pattern](https://code.google.com/p/selenium/wiki/PageObjects)
* Suits for novice users.

Usage
-----
Most of `Browser` functions support both `WebElement` object and tuple/list which represents html element. This tuple/list object should contain selector/locator as first element and value as a second element. Example: `input = (By.NAME, 'q')`

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
>>> # back to action
>>> browser.type(input, u'selenium') # typing 'selenium' into search field
>>> browser.click(search_btn) # clicking search button
>>> browser.get_text(result) # getting first found title
u'Selenium - Web Browser Automation'
>>> browser.quit() # closing browser
```

Check [browser_test.py](/easyselenium/browser_test.py) for more examples.

Installation
------------
Installation flow:
0. Install all required libraries and software
1. Download latest code from GitHub as archive file
2. Unzip it
3. Open terminal or command line console
4. Navigate to extracted folder
5. Go to `easyselenium` folder and install with command:
```shell
python setup.py install
```
