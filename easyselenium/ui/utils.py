import os
import re
import logging
import tempfile
import traceback

from wx import MessageDialog, OK, CENTER, Notebook, BoxSizer, \
    VERTICAL, ALL, EXPAND, CallAfter, Dialog, RESIZE_BORDER, \
    TextCtrl, TE_MULTILINE, TE_READONLY, HSCROLL, DEFAULT_DIALOG_STYLE, Button, \
    ID_OK, EVT_BUTTON, StaticText, Gauge, GA_SMOOTH, GA_HORIZONTAL, CAPTION, \
    STAY_ON_TOP, EVT_CLOSE, CallLater

from easyselenium.utils import unicode_str
from easyselenium.ui.parser.parsed_class import ParsedClass
from easyselenium.ui.file_utils import save_file
import threading
from time import sleep
from threading import Thread, Event


LINESEP = unicode_str(os.linesep)


def run_in_separate_thread(taget, name=None, args=(), kwargs=None):
    thread = Thread(target=taget, name=name, args=args, kwargs=kwargs)
    thread.start()
    return thread


def get_class_name_from_file(path):
    filename, _ = os.path.splitext(os.path.basename(path))
    return ''.join([w.capitalize() for w in filename.split(u'_')])


def get_py_file_name_from_class_name(class_name):
    words = re.findall('[A-Z]*[a-z0-9]*',
                       class_name)
    words = [w for w in words if len(w) > 0]
    return '_'.join(words).lower() + '.py'


def check_py_code_for_errors(code, *additional_python_paths):
    tmp_file = tempfile.mktemp()
    save_file(tmp_file, code)
    formatted_exception = check_file_for_errors(tmp_file, *additional_python_paths)
    os.remove(tmp_file)
    return formatted_exception


def check_file_for_errors(path, *additional_python_paths):
    syspath = list(os.sys.path)

    for py_path in additional_python_paths:
        if os.path.exists(py_path):
            os.sys.path.append(py_path)

    try:
        ParsedClass.get_parsed_classes(path)
        os.sys.path = syspath
        return None
    except Exception:
        os.sys.path = syspath
        formatted_exc = traceback.format_exc()
        return formatted_exc


def show_error_dialog(parent, message, caption):
    return DialogWithText(parent, caption, message).ShowModal()


def show_dialog(parent, message, caption, style=OK | CENTER):
    return MessageDialog(parent, message, caption, style).ShowModal()


def show_dialog_path_does_exist(parent, path):
    if path is None:
        path = ''
    msg = u"Path already exists: '%s'" % path
    caption = u'Bad path'
    return show_dialog(parent, msg, caption)


def show_dialog_path_doesnt_exist(parent, path):
    if path is None:
        path = ''
    msg = u"Path doesn't exist: '%s'" % path
    caption = u'Bad path'
    return show_dialog(parent, msg, caption)


def show_dialog_bad_name(parent, name, *expected_names):
    msg = u"Bad name: '%s'" % name
    if len(expected_names) > 0:
        msg += LINESEP + 'Expected names like:' + LINESEP + LINESEP.join(expected_names)
    caption = u'Bad name'
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
        Dialog.__init__(self, parent, title=title, style=DEFAULT_DIALOG_STYLE | RESIZE_BORDER)
        self.SetTitle(title)
        self.SetSizeWH(600, 400)

        sizer = BoxSizer(VERTICAL)

        self.txt_ctrl = TextCtrl(self, style=TE_MULTILINE | TE_READONLY | HSCROLL)
        if text:
            self.txt_ctrl.SetValue(text)
        sizer.Add(self.txt_ctrl, 1, flag=ALL | EXPAND)

        self.btn_ok = Button(self, label=u'OK')
        self.btn_ok.Bind(EVT_BUTTON, self.__close)
        sizer.Add(self.btn_ok, flag=CENTER)

        self.SetSizer(sizer)

    def __close(self, evt):
        self.EndModal(ID_OK)
        self.Hide()


class InfiniteProgressBarDialog(Dialog):
    def __init__(self, parent, title, text):
        Dialog.__init__(self, parent, title=title, style=CAPTION | STAY_ON_TOP)
        sizer = BoxSizer(VERTICAL)

        self.label = StaticText(self, label=text)
        sizer.Add(self.label, flag=ALL | EXPAND)

        self.gauge = Gauge(self, style=GA_SMOOTH | GA_HORIZONTAL)
        sizer.Add(self.gauge, flag=ALL | EXPAND)

        self.close_event = Event()
        def show_progress():
            while(not self.close_event.is_set()):
                sleep(0.05)
                self.gauge.Pulse()
            self.EndModal(ID_OK)

        self.SetSizerAndFit(sizer)

        run_in_separate_thread(show_progress)
