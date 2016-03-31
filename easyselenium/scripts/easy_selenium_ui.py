#!/usr/bin/env python

import os
import sys

from wx import App

# TODO: remove, fix for local import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from easyselenium.ui.main_ui import MainFrame


if __name__ == '__main__':
    app = App(False)
    main_ui = MainFrame(None)
    main_ui.Show()
    app.MainLoop()

# TODO: use relative path in generator
# TODO: better naming for generated fields
# TODO: find and remove duplicate code
# TODO: add wait_for_text_changed
# TODO: add wait_for_value_changed
# TODO: add wait_for_attribute_changed
# TODO: add parent to Browser methods
# TODO: changes are not applied when running test - if method is added to pagemodel and is used in test - NoMethod exception will be raised
    # TODO: generator - when browser is closed - remove screenshot
