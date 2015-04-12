import os
import re
import logging
import tempfile
import traceback

from wx import MessageDialog, OK, CENTER, Notebook, BoxSizer, \
    VERTICAL, ALL, EXPAND, CallAfter, Dialog, RESIZE_BORDER, \
    TextCtrl, TE_MULTILINE, TE_READONLY, HSCROLL, DEFAULT_DIALOG_STYLE

from easyselenium.utils import unicode_str
from easyselenium.ui.parser.parsed_class import ParsedClass
from easyselenium.ui.file_utils import save_file


LINESEP = unicode_str(os.linesep)


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
    # TODO: implement dialog correctly - error  message should be easy to read
    return show_dialog(parent, message, caption)


def show_dialog(parent, message, caption, style=OK | CENTER):
    return MessageDialog(parent, message, caption, style).ShowModal()


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
    def __init__(self, parent, title):
        Dialog.__init__(self, parent, style=DEFAULT_DIALOG_STYLE | RESIZE_BORDER)
        self.SetSizeWH(600, 400)

        sizer = BoxSizer(VERTICAL)

        self.txt_ctrl = TextCtrl(self, style=TE_MULTILINE | TE_READONLY | HSCROLL)
        sizer.Add(self.txt_ctrl, flag=ALL | EXPAND)

        self.SetTitle(title)
