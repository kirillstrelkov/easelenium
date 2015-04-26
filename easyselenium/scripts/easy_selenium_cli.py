#!/usr/bin/env python

from nose.core import main
from nose.plugins.base import Plugin

# TODO: removed path editing
import sys
sys.path.append('/home/kirill/Dropbox/tmpworkspace/easyselenium')
from easyselenium.browser import Browser


class EasySeleniumPlugin(Plugin):
    name = 'easyselenium'
    enabled = False

    def __init__(self):
        Plugin.__init__(self)

    def help(self):
        return 'Easy Selenium plugin for Nose - allows to specify ' \
        'browser that tests will be executed with.'

    def options(self, parser, env):
        browsers = Browser.get_supported_browsers()
        parser.add_option('-b', '--browser',
                          help="Specify browser by using initials. " \
                          "If value was not passed then 'ff' will be used. " \
                          "Supported choices: %s" % browsers,
                          choices=browsers)
        Plugin.options(self, parser, env)

    def configure(self, options, conf):
        if options.browser:
            Browser.DEFAULT_BROWSER = options.browser
        return Plugin.configure(self, options, conf)


if __name__ == '__main__':
    main(addplugins=[EasySeleniumPlugin()])
