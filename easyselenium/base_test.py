# coding=utf8
from unittest.case import TestCase

from easyselenium.browser import Browser
from easyselenium.utils import Logger


class BaseTest(TestCase):
    TC_NAME_WIDTH = 100
    BROWSER_NAME = None
    logger = Logger(name='easyselenim.base_test.BaseTest')

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.browser = Browser(browser_name=cls.BROWSER_NAME,
                              logger=cls.logger)

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.browser.quit()

    def setUp(self):
        TestCase.setUp(self)
        if self.browser.logger:
            name = self.id()
            symbols_before = u"-" * ((self.TC_NAME_WIDTH - len(name) - 2) / 2)
            self.browser.logger.info(symbols_before + ' %s ' + symbols_before,
                                     name)

    def tearDown(self):
        TestCase.tearDown(self)
        if self.browser.logger:
            self.browser.logger.info(u"-" * self.TC_NAME_WIDTH)
