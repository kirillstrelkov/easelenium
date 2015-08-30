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
