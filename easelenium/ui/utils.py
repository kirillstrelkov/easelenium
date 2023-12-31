"""UI utilities."""
from __future__ import annotations

import os
import tempfile
import traceback
from pathlib import Path
from threading import Thread
from typing import Any

from wx import ALL, EXPAND

from easelenium.ui.file_utils import save_file
from easelenium.ui.parser.parsed_class import ParsedClass

FLAG_ALL_AND_EXPAND = ALL | EXPAND


TypeArea = tuple[int, int, int, int] | list[int, int, int, int]
TypePoint = tuple[int, int] | list[int, int]
TypeBy = tuple[str, str] | list[str, str]


def run_in_separate_thread(
    target: callable,
    name: str | None = None,
    args: tuple[Any] = (),
    kwargs: dict[str, Any] | None = None,
) -> Thread:
    """Run a function in a separate thread."""
    thread = Thread(target=target, name=name, args=args, kwargs=kwargs)
    thread.start()
    return thread


def check_py_code_for_errors(
    code: str,
    *additional_python_paths: list[str],
) -> str | None:
    """Check python code for errors."""
    tmp_file = tempfile.mkstemp()
    save_file(tmp_file, code)
    formatted_exception = check_file_for_errors(tmp_file, *additional_python_paths)
    Path(tmp_file).unlink()
    return formatted_exception


def check_file_for_errors(
    path: str,
    *additional_python_paths: list[str],
) -> str | None:
    """Check file for errors."""
    syspath = list(os.sys.path)

    for py_path in additional_python_paths:
        if Path(py_path).exists():
            os.sys.path.append(py_path)

    try:
        ParsedClass.get_parsed_classes(path)
        os.sys.path = syspath
    except Exception:  # noqa: BLE001
        os.sys.path = syspath
        return traceback.format_exc()

    return None
