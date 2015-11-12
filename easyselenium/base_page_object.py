

class BasePageObject(object):
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger
