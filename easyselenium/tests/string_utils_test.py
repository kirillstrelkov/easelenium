from unittest.case import TestCase
from easyselenium.ui.string_utils import StringUtils


class StringUtilsTest(TestCase):
    def test_is_test_file_name_correct(self):
        self.assertTrue(StringUtils.is_test_file_name_correct('my_new_test.py'))
        self.assertTrue(StringUtils.is_test_file_name_correct('2my_new_test.py'))
        self.assertTrue(StringUtils.is_test_file_name_correct('my_2new_test.py'))

        self.assertFalse(StringUtils.is_test_file_name_correct('test.py'))
        self.assertFalse(StringUtils.is_test_file_name_correct('_test.py'))
        self.assertFalse(StringUtils.is_test_file_name_correct('A_test.py'))
        self.assertFalse(StringUtils.is_test_file_name_correct('9B_test.py'))
        self.assertFalse(StringUtils.is_test_file_name_correct('B9_test.py'))

    def test_is_test_case_name_correct(self):
        self.assertTrue(StringUtils.is_test_case_name_correct('test_1'))
        self.assertTrue(StringUtils.is_test_case_name_correct('test_new'))
        self.assertTrue(StringUtils.is_test_case_name_correct('test_search'))

        self.assertFalse(StringUtils.is_test_case_name_correct('test.py'))
        self.assertFalse(StringUtils.is_test_case_name_correct('test'))
        self.assertFalse(StringUtils.is_test_case_name_correct('_test_asd'))
        self.assertFalse(StringUtils.is_test_case_name_correct('asd'))
        self.assertFalse(StringUtils.is_test_case_name_correct('453453sfs'))

    def test_is_method_name_correct(self):
        self.assertTrue(StringUtils.is_method_name_correct('method_1'))
        self.assertTrue(StringUtils.is_method_name_correct('new_method'))
        self.assertTrue(StringUtils.is_method_name_correct('search'))
        self.assertTrue(StringUtils.is_method_name_correct('asd'))

        self.assertFalse(StringUtils.is_method_name_correct('test.py'))
        self.assertFalse(StringUtils.is_method_name_correct('_test_asd'))
        self.assertFalse(StringUtils.is_method_name_correct('453453sfs'))

    def test_is_area_correct(self):
        self.assertTrue(StringUtils.is_area_correct('(0,0,0,0)'))
        self.assertTrue(StringUtils.is_area_correct('(0, 0, 0, 0)'))
        self.assertTrue(StringUtils.is_area_correct('(   0,   0,   0,   0   )'))
        self.assertTrue(StringUtils.is_area_correct('(100, 100, 100, 100)'))

        self.assertFalse(StringUtils.is_area_correct('(0, 0, 0)'))
        self.assertFalse(StringUtils.is_area_correct('(0, 0, 0, d)'))
        self.assertFalse(StringUtils.is_area_correct('0, 0, 0, 0'))
        self.assertFalse(StringUtils.is_area_correct('(0, 0, 0, 0, 0)'))
        self.assertFalse(StringUtils.is_area_correct('[0, 0, 0, 0]'))

    def test_is_url_correct(self):
        self.assertTrue(StringUtils.is_url_correct('http://google.com'))
        self.assertTrue(StringUtils.is_url_correct('http://google.com/'))
        self.assertTrue(StringUtils.is_url_correct('http://www.google.com'))
        self.assertTrue(StringUtils.is_url_correct('http://www.google.com/'))
        self.assertTrue(StringUtils.is_url_correct('https://google.com/'))
        self.assertTrue(StringUtils.is_url_correct('https://google.com/sdf/we/qwe/asd?q=4'))

        self.assertFalse(StringUtils.is_url_correct(''))
        self.assertFalse(StringUtils.is_url_correct('google.com'))
        self.assertFalse(StringUtils.is_url_correct('www.google.com'))
