from unittest.case import TestCase


class BasePageObject(TestCase):
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger
