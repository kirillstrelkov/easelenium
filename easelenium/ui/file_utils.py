"""File utility functions."""
from __future__ import annotations

import codecs
import os
from pathlib import Path

__ENCODING = "utf8"
__WRITE_MODE = "wb"
__READ_MODE = "rb"


def is_correct_python_file(filename: str) -> bool:
    """Return True if the file is a python file else False."""
    name = Path(filename).name
    return name.endswith(".py") and not name.startswith("__")


def check_if_path_exists(path: str) -> bool:
    """Check if the path exists."""
    if not Path(path).exists():
        msg = f"Path not found '{path}'"
        raise FileNotFoundError(msg)
    return True


def safe_remove_path(path: str) -> bool:
    """Remove existing file."""
    if Path(path).exists():
        Path(path).unlink()
        return True
    return False


def safe_create_path(path: str) -> None:
    """Create path if it doesn't exist."""
    if Path(path).exists():
        return

    if Path(path).is_dir():
        Path(path).mkdir()
    else:
        basedir = Path(path).parent
        if not Path(basedir).exists():
            Path(basedir).mkdir()
        codecs.open(path, __WRITE_MODE, __ENCODING).close()


def save_file(path: str, content: str, *, is_text: bool = True) -> None:
    """Save file."""
    if is_text:
        with codecs.open(path, __WRITE_MODE, encoding=__ENCODING) as f:
            f.write(content)
    else:
        with Path(path).open(__WRITE_MODE) as f:
            f.write(content)


def read_file(path: str) -> str:
    """Read file."""
    with codecs.open(path, __READ_MODE, encoding=__ENCODING) as f:
        return f.read()


def get_list_of_files(path: str, *, recursively: bool = False) -> list[str]:
    """Get list of files."""
    files = []
    for f in os.listdir(path):
        file_path = (Path(path) / f).as_posix()
        if Path(file_path).is_dir() and recursively:
            files += get_list_of_files(file_path, recursively)
        else:
            files.append(file_path)
    return files
