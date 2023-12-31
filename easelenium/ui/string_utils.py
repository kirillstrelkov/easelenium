"""String utilities."""
from __future__ import annotations

import re
from pathlib import Path


class RegExps:
    """Regular expressions."""

    CLASS_NAME = r"^[A-Z][a-zA-Z0-9]*$"
    TEST_FILE_NAME = r"^[a-z_\d]+_test.py$"
    TEST_CASE_NAME = r"^test_[a-z_\d]+$"
    METHOD_NAME = r"^[a-z][a-z_\d]+$"
    AREA = r"\( *\d+ *, *\d+ *, *\d+ *, *\d+ *\)"
    URL = r"https?://.+"


class StringUtils:
    """String Utilities."""

    @classmethod
    def is_test_file_name_correct(cls: type[StringUtils], filename: str) -> bool:
        """Return True if test filename name is correct else False."""
        return cls.does_text_match_regexp(
            Path(filename).name,
            RegExps.TEST_FILE_NAME,
        )

    @classmethod
    def is_area_correct(cls: type[StringUtils], area_as_string: str) -> bool:
        """Return True if area is correct else False."""
        return cls.does_text_match_regexp(area_as_string, RegExps.AREA)

    @classmethod
    def is_test_case_name_correct(cls: type[StringUtils], test_case_name: str) -> bool:
        """Return True if test case name is correct else False."""
        return cls.does_text_match_regexp(test_case_name, RegExps.TEST_CASE_NAME)

    @classmethod
    def is_method_name_correct(cls: type[StringUtils], method_name: str) -> bool:
        """Return True if method name is correct else False."""
        return cls.does_text_match_regexp(method_name, RegExps.METHOD_NAME)

    @classmethod
    def is_class_name_correct(cls: type[StringUtils], class_name: str) -> bool:
        """Return True if class name is correct else False."""
        return cls.does_text_match_regexp(class_name, RegExps.CLASS_NAME)

    @classmethod
    def is_url_correct(cls: type[StringUtils], url: str) -> bool:
        """Return True if url is correct else False."""
        return cls.does_text_match_regexp(url, RegExps.URL)

    @classmethod
    def does_text_match_regexp(cls: type[StringUtils], text: str, regexp: str) -> bool:
        """Return True if regexp mathches text else False."""
        return re.match(regexp, text) is not None
