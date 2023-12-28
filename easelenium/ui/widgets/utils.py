import logging
from threading import Event
from time import sleep

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
    Gauge,
    MessageDialog,
    Notebook,
    StaticText,
    TextCtrl,
)

from easelenium.ui.utils import FLAG_ALL_AND_EXPAND, run_in_separate_thread
from easelenium.ui.widgets.image.image_with_elements import ImageWithElements
from easelenium.utils import LINESEP


def show_error_dialog(parent, message, caption):
    return DialogWithText(parent, caption, message).ShowModal()


def show_dialog(parent, message, caption, style=OK | CENTER):
    return MessageDialog(parent, message, caption, style).ShowModal()


def show_dialog_path_does_exist(parent, path):
    if path is None:
        path = ""
    msg = "Path already exists: '%s'" % path
    caption = "Bad path"
    return show_dialog(parent, msg, caption)


def show_dialog_path_doesnt_exist(parent, path):
    if path is None:
        path = ""
    msg = "Path doesn't exist: '%s'" % path
    caption = "Bad path"
    return show_dialog(parent, msg, caption)


def show_dialog_bad_name(parent, name, *expected_names):
    msg = "Bad name: '%s'" % name
    if len(expected_names) > 0:
        msg += LINESEP + "Expected names like:" + LINESEP + LINESEP.join(expected_names)
    caption = "Bad name"
    return show_dialog(parent, msg, caption)


class Tabs(Notebook):
    def __init__(self, parent, tabs_and_title=None):
        Notebook.__init__(self, parent)
        if tabs_and_title and len(tabs_and_title):
            for tab, title in tabs_and_title:
                self.AddPage(tab(self), title)

    def get_tabs_text(self, index=None):
        if index is None:
            index = self.GetSelection()
        text = self.GetPageText(index)
        return text

    def set_tabs_text(self, text, index=None):
        if index is None:
            index = self.GetSelection()
        self.SetPageText(index, text)


class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + LINESEP
        CallAfter(self.ctrl.AppendText, s)


class DialogWithText(Dialog):
    def __init__(self, parent, title, text=None):
        Dialog.__init__(
            self, parent, title=title, style=DEFAULT_DIALOG_STYLE | RESIZE_BORDER,
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

    def __close(self, evt):
        CallAfter(self.EndModal, ID_OK)
        self.Hide()


class InfiniteProgressBarDialog(Dialog):
    def __init__(self, parent, title, text):
        Dialog.__init__(self, parent, title=title, style=CAPTION | STAY_ON_TOP)
        sizer = BoxSizer(VERTICAL)

        self.label = StaticText(self, label=text)
        sizer.Add(self.label, flag=FLAG_ALL_AND_EXPAND)

        self.gauge = Gauge(self, style=GA_SMOOTH | GA_HORIZONTAL)
        sizer.Add(self.gauge, flag=FLAG_ALL_AND_EXPAND)

        self.close_event = Event()

        def show_progress():
            while not self.close_event.is_set():
                sleep(0.05)
                self.gauge.Pulse()
            CallAfter(self.EndModal, ID_OK)

        self.SetSizerAndFit(sizer)

        run_in_separate_thread(show_progress)


class ImageAndTableHelper:
    @staticmethod
    def select_field_on_mouse_move(evt, po_fields, image_panel, table):
        field_before = image_panel.selected_field
        image_panel.set_po_fields(po_fields)
        ImageWithElements.on_mouse_move(image_panel, evt)
        field_after = image_panel.selected_field
        if field_after and field_after != field_before:
            row = po_fields.index(field_after)
            table.select_row(row)
