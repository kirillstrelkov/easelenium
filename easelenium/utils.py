"""easelenium utilities."""
from __future__ import annotations

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from random import choice
from typing import Any

from loguru import logger

LINESEP = os.linesep


def get_match(
    regexp: str,
    string: str,
    *,
    single_match: bool = True,
) -> str | None:
    """Return first match."""
    found = re.findall(regexp, string)
    if found:
        return found[0] if single_match else found

    return None


def is_windows() -> bool:
    """Return True if running on Windows."""
    return sys.platform.startswith("win")


def get_timestamp() -> str:
    """Return current timestamp."""
    timetuple = datetime.now().timetuple()  # noqa: DTZ005
    return "%d%02d%02d%02d%02d%02d" % timetuple[:6]


def is_string(obj: Any) -> bool:  # noqa: ANN401
    """Return True if object is string."""
    return isinstance(obj, str)


def get_random_value(values: list[Any], *val_to_skip: str[Any]) -> Any:  # noqa: ANN401
    """Return random value from list."""
    tmp_values = list(values)
    for skipped in val_to_skip:
        tmp_values.remove(skipped)
    return choice(tmp_values)  # noqa: S311


class Logger:
    """Logger class."""

    def __init__(  # noqa: PLR0913
        self,
        name: str | None = None,
        *,
        log_to_console: bool = True,
        file_path: str | None = None,
        handler: callable | None = None,
        level: int = logging.INFO,
    ) -> None:
        """Initialize."""
        self.__logger = logger

        if log_to_console:
            self.__logger.add(sys.stdout, filter=name, level=level)

        if file_path:
            self.__logger.add(file_path, filter=name, level=level)

        if handler:
            self.__logger.add(handler, filter=name, level=level)

    def debug(self, msg: str, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """Log debug message."""
        self.__logger.info(msg, *args, **kwargs)

    def info(self, msg: str, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """Log info message."""
        self.__logger.info(msg, *args, **kwargs)

    def warn(self, msg: str, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """Log warning message."""
        self.__logger.warning(msg, *args, **kwargs)


def get_class_name_from_file(path: str) -> str:
    """Return class name from file."""
    return "".join([w.capitalize() for w in Path(path).stem.split("_")])


def get_py_file_name_from_class_name(class_name: str) -> str:
    """Return py file name from class name."""
    words = re.findall("[A-Z]*[a-z0-9]*", class_name)
    words = [w for w in words if w]
    return "_".join(words).lower() + ".py"
