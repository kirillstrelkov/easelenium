"""Module for main UI."""

import shutil
import traceback
from tempfile import mkdtemp

from wx import (
    EVT_BUTTON,
    EVT_CLOSE,
    ID_OK,
    Button,
    Choice,
    DirDialog,
    Event,
    Frame,
    GridBagSizer,
    Panel,
    StaticText,
    TextCtrl,
    Window,
)

from easelenium.browser import Browser
from easelenium.ui.editor.editor_ui import EditorTab
from easelenium.ui.generator.generator_ui import GeneratorTab
from easelenium.ui.root_folder import RootFolder
from easelenium.ui.selector_finder.finder_ui import SelectorFinderTab
from easelenium.ui.string_utils import StringUtils
from easelenium.ui.test_runner_ui import TestRunnerTab
from easelenium.ui.utils import FLAG_ALL_AND_EXPAND
from easelenium.ui.widgets.utils import Tabs, show_dialog, show_error_dialog


class MainFrame(Frame):
    """Main UI class."""

    def __init__(self, parent: Window) -> None:
        """Initialize main UI."""
        Frame.__init__(self, parent)
        self.__browser = None
        self.__tmp_dir = mkdtemp()

        self.SetTitle("Easy Selenium UI")
        self.SetSize((800, 600))

        self.__create_widgets()
        self.Bind(EVT_CLOSE, self.__on_close)

    def __create_widgets(self) -> None:
        panel = Panel(self)

        sizer = GridBagSizer(5, 5)
        row = 0
        col = 0
        label = StaticText(panel, label="Root folder:")
        sizer.Add(label, pos=(row, col))

        col += 1
        col_width = 4
        self.__txt_root_path = TextCtrl(panel)
        sizer.Add(
            self.__txt_root_path,
            pos=(row, col),
            span=(1, col_width),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += col_width
        self.__btn_set_root = Button(panel, label="Set root folder")
        self.__btn_set_root.Bind(EVT_BUTTON, self.__set_root_folder)
        sizer.Add(self.__btn_set_root, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        label = StaticText(panel, label="Url:")
        sizer.Add(label, pos=(row, col))

        col += 1
        self.__txt_url = TextCtrl(
            panel,
            value="https://www.google.com/",
        )  # TODO: remove url  # noqa: TD003, TD002, FIX002
        sizer.Add(self.__txt_url, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        label = StaticText(panel, label="Browser:")
        sizer.Add(label, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.__cb_browser = Choice(panel, choices=Browser.get_supported_browsers())
        self.__cb_browser.Select(0)
        sizer.Add(self.__cb_browser, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.bth_open_url = Button(panel, label="Open url")
        self.bth_open_url.Bind(EVT_BUTTON, self.__open_url)
        sizer.Add(self.bth_open_url, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.bth_close_url = Button(panel, label="Close browser")
        self.bth_close_url.Bind(EVT_BUTTON, self.__close_browser)
        sizer.Add(self.bth_close_url, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        tabs = Tabs(
            panel,
            [
                (GeneratorTab, "Generator"),
                (EditorTab, "Editor"),
                (TestRunnerTab, "Test runner"),
                (SelectorFinderTab, "Selector finder"),
            ],
        )
        sizer.Add(tabs, pos=(row, col), span=(1, 6), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(2, 1)
        panel.SetSizer(sizer)
        self.Layout()

    def get_root_folder(self) -> str:
        """Get root folder path."""
        text = self.__txt_root_path.GetValue()
        if text:
            return text

        return None

    def __set_root_folder(self, _evt: Event) -> None:
        dialog = DirDialog(self)
        if dialog.ShowModal() == ID_OK:
            path = dialog.GetPath()
            RootFolder.prepare_folder(path)
            self.__txt_root_path.SetValue(path)

    def __open_url(self, _evt: Event) -> None:
        url = self.__txt_url.GetValue()
        if StringUtils.is_url_correct(url):
            self.bth_open_url.Disable()

            name = self.get_browser_initials()

            try:
                if self.__browser and self.__browser.get_browser_initials() != name:
                    self.__browser.quit()
                    self.__browser = Browser(name)
                elif not self.__browser:
                    self.__browser = Browser(name)
            except Exception:  # noqa: BLE001
                show_error_dialog(
                    self,
                    traceback.format_exc(),
                    "Failed to open browser",
                )
                self.__browser = None

            if self.__browser:
                self.__browser.open(url)
            # TODO: if generator or selector -> load image  # noqa: TD002, TD003, FIX002
            self.bth_open_url.Enable()
        else:
            show_dialog(self, "Bad url: %s" % url, "Bad url")

    def __close_browser(self, _evt: Event) -> None:
        if self.__browser:
            self.__browser.quit()
            self.__browser = None

    def __on_close(self, evt: Event) -> None:
        self.__close_browser(evt)

        shutil.rmtree(self.__tmp_dir, ignore_errors=True)
        self.Destroy()

    def get_url(self) -> str:
        """Get url from text control."""
        return self.__txt_url.GetValue()

    def set_url(self, url: str) -> None:
        """Set url to text control."""
        self.__txt_url.SetValue(url)

    def get_browser(self) -> Browser:
        """Get browser."""
        return self.__browser

    def get_browser_initials(self) -> str:
        """Get browser initials."""
        return self.__cb_browser.GetStringSelection()

    def get_tmp_dir(self) -> str:
        """Get temporary directory."""
        return self.__tmp_dir
