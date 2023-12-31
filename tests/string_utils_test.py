"""String utilities tests."""
from unittest.case import TestCase

from easelenium.ui.string_utils import StringUtils


class StringUtilsTest(TestCase):
    """String utilities tests."""

    def test_is_test_file_name_correct(self) -> None:
        """Check test file name is correct."""
        assert StringUtils.is_test_file_name_correct("my_new_test.py")
        assert StringUtils.is_test_file_name_correct("2my_new_test.py")
        assert StringUtils.is_test_file_name_correct("my_2new_test.py")

        assert not StringUtils.is_test_file_name_correct("test.py")
        assert not StringUtils.is_test_file_name_correct("_test.py")
        assert not StringUtils.is_test_file_name_correct("A_test.py")
        assert not StringUtils.is_test_file_name_correct("9B_test.py")
        assert not StringUtils.is_test_file_name_correct("B9_test.py")

    def test_is_test_case_name_correct(self) -> None:
        """Check test case name is correct."""
        assert StringUtils.is_test_case_name_correct("test_1")
        assert StringUtils.is_test_case_name_correct("test_new")
        assert StringUtils.is_test_case_name_correct("test_search")

        assert not StringUtils.is_test_case_name_correct("test.py")
        assert not StringUtils.is_test_case_name_correct("test")
        assert not StringUtils.is_test_case_name_correct("_test_asd")
        assert not StringUtils.is_test_case_name_correct("asd")
        assert not StringUtils.is_test_case_name_correct("453453sfs")

    def test_is_method_name_correct(self) -> None:
        """Check method name is correct."""
        assert StringUtils.is_method_name_correct("method_1")
        assert StringUtils.is_method_name_correct("new_method")
        assert StringUtils.is_method_name_correct("search")
        assert StringUtils.is_method_name_correct("asd")

        assert not StringUtils.is_method_name_correct("test.py")
        assert not StringUtils.is_method_name_correct("_test_asd")
        assert not StringUtils.is_method_name_correct("453453sfs")

    def test_is_area_correct(self) -> None:
        """Check area is correct."""
        assert StringUtils.is_area_correct("(0,0,0,0)")
        assert StringUtils.is_area_correct("(0, 0, 0, 0)")
        assert StringUtils.is_area_correct("(   0,   0,   0,   0   )")
        assert StringUtils.is_area_correct("(100, 100, 100, 100)")

        assert not StringUtils.is_area_correct("(0, 0, 0)")
        assert not StringUtils.is_area_correct("(0, 0, 0, d)")
        assert not StringUtils.is_area_correct("0, 0, 0, 0")
        assert not StringUtils.is_area_correct("(0, 0, 0, 0, 0)")
        assert not StringUtils.is_area_correct("[0, 0, 0, 0]")

    def test_is_url_correct(self) -> None:
        """Check url is correct."""
        assert StringUtils.is_url_correct("http://google.com")
        assert StringUtils.is_url_correct("http://google.com/")
        assert StringUtils.is_url_correct("http://www.google.com")
        assert StringUtils.is_url_correct("http://www.google.com/")
        assert StringUtils.is_url_correct("https://google.com/")
        assert StringUtils.is_url_correct("https://google.com/sdf/we/qwe/asd?q=4")

        assert not StringUtils.is_url_correct("")
        assert not StringUtils.is_url_correct("google.com")
        assert not StringUtils.is_url_correct("www.google.com")

    def test_is_class_name_correct(self) -> None:
        """Check class name is correct."""
        assert StringUtils.is_class_name_correct("AsDaAs")
        assert StringUtils.is_class_name_correct("AAASdsd")
        assert StringUtils.is_class_name_correct("Azczxc")
        assert StringUtils.is_class_name_correct("AWEasd8")
        assert StringUtils.is_class_name_correct("XCZXC32423")
        assert StringUtils.is_class_name_correct("X")

        assert not StringUtils.is_class_name_correct("")
        assert not StringUtils.is_class_name_correct("google")
        assert not StringUtils.is_class_name_correct("google.com")
