import os
import re
import tempfile
import traceback
from threading import Thread
from wx import ALL, EXPAND

from easyselenium.utils import unicode_str
from easyselenium.ui.parser.parsed_class import ParsedClass
from easyselenium.ui.file_utils import save_file

LINESEP = unicode_str(os.linesep)
FLAG_ALL_AND_EXPAND = ALL | EXPAND


def run_in_separate_thread(target, name=None, args=(), kwargs=None):
    thread = Thread(target=target, name=name, args=args, kwargs=kwargs)
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
