#!/usr/bin/env python3

import os
import sys

from wx import App

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from easelenium.ui.main_ui import MainFrame

if __name__ == "__main__":
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
# TODO: if test case updated - doesn't updated in test runner
# TODO: generator - when browser is closed - remove
# TODO: add support for not uniq selectors
# TODO: if selector is not uniq in 'Editor' use status text with notification: 'NOTE: this selector is not uniq' and show all possible object which could be found with this selector
# TODO: add enable/disable for uniq selector in 'Selector finder'
# TODO: add support for adding code where mouse is located
# TODO: when adding code auto wrap input if it is a string??
# TODO: move to Python3!
# TODO: add copy selector in 'Selector finder'
# TODO: if generation log window close - stop all generation
# TODO: no vertical scroll in Windows in Editor tab
# TODO: second import of page object is inserted incorrectly in Windows
# TODO: forbid setting root folder 'img' or 'page_objects'
# TODO: fix Windows GUI bugs:
#     if split is move to the top - not possible to resize it again
#     if click on reload image image is located in center , hover over element and image adjusted to the left
#     if test runner selected tree windows is not visible
# TODO: split browser class into smaller classes like Waits, Getters etc
# TODO: add support for headless drivers, mobile driver, remote execution
# TODO: add save_page_code to browser and add auto save on failed
# TODO: html option is not supported in Test runner in Windows
