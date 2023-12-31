#!/usr/bin/env python3

"""easelenium main UI."""

import sys
from pathlib import Path

from wx import App

sys.path.append(str(Path(__file__).parent / "../.."))

from easelenium.ui.main_ui import MainFrame  # noqa: E402

if __name__ == "__main__":
    app = App(redirect=False)
    main_ui = MainFrame(None)
    main_ui.Show()
    app.MainLoop()

# TODO: use relative path in generator # noqa: FIX002, TD002, TD003
# TODO: better naming for generated fields # noqa: FIX002, TD002, TD003
# TODO: find and remove duplicate code # noqa: FIX002, TD002, TD003
# TODO: add wait_for_text_changed # noqa: FIX002, TD002, TD003
# TODO: add wait_for_value_changed # noqa: FIX002, TD002, TD003
# TODO: add wait_for_attribute_changed # noqa: FIX002, TD002, TD003
# TODO: add parent to Browser methods # noqa: FIX002, TD002, TD003
# TODO: changes are not applied when running test - if method is added to pagemodel and is used in test - NoMethod exception will be raised # noqa: FIX002, TD002, TD003, E501
# TODO: if test case updated - doesn't updated in test runner # noqa: FIX002, TD002, TD003, E501
# TODO: generator - when browser is closed - remove # noqa: FIX002, TD002, TD003
# TODO: add support for not uniq selectors # noqa: FIX002, TD002, TD003
# TODO: if selector is not uniq in 'Editor' use status text with notification: 'NOTE: this selector is not uniq' and show all possible object which could be found with this selector # noqa: FIX002, TD002, TD003, E501
# TODO: add enable/disable for uniq selector in 'Selector finder' # noqa: FIX002, TD002, TD003, E501
# TODO: add support for adding code where mouse is located # noqa: FIX002, TD002, TD003
# TODO: when adding code auto wrap input if it is a string?? # noqa: FIX002, TD002, TD003, E501
# TODO: move to Python3! # noqa: FIX002, TD002, TD003
# TODO: add copy selector in 'Selector finder' # noqa: FIX002, TD002, TD003
# TODO: if generation log window close - stop all generation # noqa: FIX002, TD002, TD003, E501
# TODO: no vertical scroll in Windows in Editor tab # noqa: FIX002, TD002, TD003
# TODO: second import of page object is inserted incorrectly in Windows # noqa: FIX002, TD002, TD003, E501
# TODO: forbid setting root folder 'img' or 'page_objects' # noqa: FIX002, TD002, TD003
# TODO: fix Windows GUI bugs: # noqa: FIX002, TD002, TD003
#     if split is move to the top - not possible to resize it again
#     if click on reload image image is located in center , hover over element and image adjusted to the left # noqa: E501
#     if test runner selected tree windows is not visible
# TODO: split browser class into smaller classes like Waits, Getters etc # noqa: FIX002, TD002, TD003, E501
# TODO: add support for headless drivers, mobile driver, remote execution # noqa: FIX002, TD002, TD003, E501
# TODO: add save_page_code to browser and add auto save on failed # noqa: FIX002, TD002, TD003, E501
# TODO: html option is not supported in Test runner in Windows # noqa: FIX002, TD002, TD003, E501
