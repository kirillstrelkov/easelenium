"""Utilities."""
from __future__ import annotations

import logging
from time import sleep
from typing import TYPE_CHECKING, Any

from wx import (
    CAPTION,
    CENTER,
    DEFAULT_DIALOG_STYLE,
    EVT_BUTTON,
    GA_HORIZONTAL,
    GA_SMOOTH,
    HSCROLL,
    ID_OK,
    OK,
    RESIZE_BORDER,
    STAY_ON_TOP,
    TE_MULTILINE,
    TE_READONLY,
    VERTICAL,
    BoxSizer,
    Button,
    CallAfter,
    Dialog,
    Event,
    Gauge,
    MessageDialog,
    Notebook,
    StaticText,
    TextCtrl,
    Window,
)

from easelenium.ui.utils import FLAG_ALL_AND_EXPAND, run_in_separate_thread
from easelenium.ui.widgets.image.image_with_elements import ImageWithElements
from easelenium.utils import LINESEP

if TYPE_CHECKING:
    from easelenium.ui.generator.page_object_class import PageObjectClassField
    from easelenium.ui.widgets.table import Table


def show_dialog(
    parent: Window,
    message: str,
    caption: str,
    style: int = OK | CENTER,
) -> MessageDialog:
    """Show a message dialog."""
    return MessageDialog(parent, message, caption, style).ShowModal()


def show_dialog_path_does_exist(parent: Window, path: str | None) -> MessageDialog:
    """Show a message dialog that path exists."""
    return show_dialog(parent, f"Path already exists: '{path}'", "Bad path")


def show_dialog_path_doesnt_exist(parent: Window, path: str | None) -> MessageDialog:
    """Show a message dialog that path does not exist."""
    return show_dialog(parent, f"Path doesn't exist: '{path}'", "Bad path")


def show_dialog_bad_name(
    parent: Window,
    name: str,
    *expected_names: list[str],
) -> MessageDialog:
    """Show a message dialog."""
    msg = f"Bad name: '{name}'"
    if len(expected_names) > 0:
        msg += LINESEP + "Expected names like:" + LINESEP + LINESEP.join(expected_names)
    return show_dialog(parent, msg, "Bad name")


class Tabs(Notebook):
    """Tabs."""

    def __init__(
        self,
        parent: Window,
        tabs_and_title: list[tuple[Any, str]] | None = None,
    ) -> None:
        """Initialize."""
        Notebook.__init__(self, parent)
        if tabs_and_title and len(tabs_and_title):
            for tab, title in tabs_and_title:
                self.AddPage(tab(self), title)

    def get_tabs_text(self, index: int | None = None) -> str:
        """Get tab's text."""
        if index is None:
            index = self.GetSelection()
        return self.GetPageText(index)

    def set_tabs_text(self, text: str, index: int | None = None) -> None:
        """Set tab's text."""
        if index is None:
            index = self.GetSelection()
        self.SetPageText(index, text)


class WxTextCtrlHandler(logging.Handler):
    """TextCtrl."""

    def __init__(self, ctrl: TextCtrl) -> None:
        """Initialize."""
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record: logging.LogRecord) -> None:
        """Emit."""
        CallAfter(
            self.ctrl.AppendText,
            self.format(record) + LINESEP,
        )


class DialogWithText(Dialog):
    """Dialog with text."""

    def __init__(
        self,
        parent: Window,
        title: str,
        text: str | None = None,
    ) -> None:
        """Initialize."""
        Dialog.__init__(
            self,
            parent,
            title=title,
            style=DEFAULT_DIALOG_STYLE | RESIZE_BORDER,
        )
        self.SetTitle(title)
        self.SetSize(600, 400)

        sizer = BoxSizer(VERTICAL)

        self.txt_ctrl = TextCtrl(self, style=TE_MULTILINE | TE_READONLY | HSCROLL)
        if text:
            self.txt_ctrl.SetValue(text)
        sizer.Add(self.txt_ctrl, 1, flag=FLAG_ALL_AND_EXPAND)

        self.btn_ok = Button(self, label="OK")
        self.btn_ok.Bind(EVT_BUTTON, self.__close)
        sizer.Add(self.btn_ok, flag=CENTER)

        self.SetSizer(sizer)

    def __close(self, _evt: Event) -> None:
        CallAfter(self.EndModal, ID_OK)
        self.Hide()


class InfiniteProgressBarDialog(Dialog):
    """Progress bar."""

    def __init__(self, parent: Window, title: str, text: str) -> None:
        """Initialize."""
        Dialog.__init__(self, parent, title=title, style=CAPTION | STAY_ON_TOP)
        sizer = BoxSizer(VERTICAL)

        self.label = StaticText(self, label=text)
        sizer.Add(self.label, flag=FLAG_ALL_AND_EXPAND)

        self.gauge = Gauge(self, style=GA_SMOOTH | GA_HORIZONTAL)
        sizer.Add(self.gauge, flag=FLAG_ALL_AND_EXPAND)

        self.close_event = Event()

        def show_progress() -> None:
            while not self.close_event.is_set():
                sleep(0.05)
                self.gauge.Pulse()
            CallAfter(self.EndModal, ID_OK)

        self.SetSizerAndFit(sizer)

        run_in_separate_thread(show_progress)


class ImageAndTableHelper:
    """Helper for image and table."""

    @staticmethod
    def select_field_on_mouse_move(
        evt: Event,
        po_fields: list[PageObjectClassField],
        image_panel: ImageWithElements,
        table: Table,
    ) -> None:
        """Select field on mouse move."""
        field_before = image_panel.selected_field
        image_panel.set_po_fields(po_fields)
        ImageWithElements.on_mouse_move(image_panel, evt)
        field_after = image_panel.selected_field
        if field_after and field_after != field_before:
            row = po_fields.index(field_after)
            table.select_row(row)


def show_error_dialog(
    parent: Window,
    message: str,
    caption: str,
) -> DialogWithText:
    """Show error dialog."""
    return DialogWithText(parent, caption, message).ShowModal()
