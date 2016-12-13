# coding=utf8
from nose.tools import *
from selenium.webdriver.common.by import By

from easyselenium.base_page_object import BasePageObject


class DuckDuckGo(BasePageObject):
    # Please do NOT remove auto-generated comments
    # Url: https://duckduckgo.com/
    # Area: None
    # File path: /tmp/DuckDuckGo.py
    # Image path: /tmp/img/DuckDuckGo.png
    BAD_NAME = (By.LINK_TEXT, u'⇶') # location: (1261, 23) dimensions: (33, 33)
    LOGO_HOMEPAGE_LINK = (By.ID, u'logo_homepage_link') # location: (526, 117) dimensions: (250, 200)
    SEARCH_FORM_INPUT_HOMEPAGE = (By.ID, u'search_form_input_homepage') # location: (347, 347) dimensions: (562, 46)
    SEARCH_BUTTON_HOMEPAGE = (By.ID, u'search_button_homepage') # location: (912, 350) dimensions: (52, 40)
    TAG_HOME_NAV_TAG_HOME_NAV_ITEM = (By.CSS_SELECTOR, u'.tag-home__nav > .tag-home__nav__item') # location: (625, 458) dimensions: (7, 7)
    TAG_HOME_NAV_ITEM_IS_ACTIVE = (By.CSS_SELECTOR, u'.tag-home__nav__item.is-active') # location: (658, 458) dimensions: (7, 7)
    ADD_TO_BROWSER_BADGE_ICON_BROWSER_FIREFOX = (By.CSS_SELECTOR, u'.add-to-browser-badge__icon.browser--firefox') # location: (518, 521) dimensions: (64, 64)
    ID_FOOTER_HOMEPAGE_DIV_1_SPAN_1_BR_1 = (By.XPATH, u'id("footer_homepage")/DIV[1]/SPAN[1]/BR[1]') # location: (747, 572) dimensions: (0, 20)
    DDGSI_ADD_TO_BROWSER_BADGE_CLOSE_JS_ADD_TO_BROWSER_CLOSE = (By.CSS_SELECTOR, u'.ddgsi.add-to-browser-badge__close.js-add-to-browser-close') # location: (754, 559) dimensions: (30, 38)
