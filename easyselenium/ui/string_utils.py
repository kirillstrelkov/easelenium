import os
import re


class RegExps(object):
    TEST_FILE_NAME = r'^[a-z_\d]+_test.py$'
    TEST_CASE_NAME = r'^test_[a-z_\d]+$'
    AREA = r'\( *\d+ *, *\d+ *, *\d+ *, *\d+ *\)'
    URL = r'https?://.+'


class StringUtils(object):
    @classmethod
    def is_test_file_name_correct(cls, file_name):
        file_name = os.path.basename(file_name)
        return cls.does_text_match_regexp(file_name, RegExps.TEST_FILE_NAME)

    @classmethod
    def is_area_correct(cls, area_as_string):
        return cls.does_text_match_regexp(area_as_string, RegExps.AREA)

    @classmethod
    def is_test_case_name_correct(cls, test_case_name):
        return cls.does_text_match_regexp(test_case_name, RegExps.TEST_CASE_NAME)

    @classmethod
    def is_url_correct(cls, url):
        return cls.does_text_match_regexp(url, RegExps.URL)

    @classmethod
    def does_text_match_regexp(cls, text, regexp):
        return re.match(regexp, text) is not None
