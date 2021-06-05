from unittest.case import TestCase

from easelenium.utils import (
    get_class_name_from_file,
    get_py_file_name_from_class_name,
)


class UtilsTest(TestCase):
    def test_get_class_name_from_file(self):
        class_name = get_class_name_from_file("my_test.py")
        assert class_name == "MyTest"

        class_name = get_class_name_from_file("/tmp/my_test.py")
        assert class_name == "MyTest"

    def test_get_py_file_name_from_class_name(self):
        class_name = get_py_file_name_from_class_name("my_test")
        assert class_name == "my_test.py"

        class_name = get_py_file_name_from_class_name("My_Test")
        assert class_name == "my_test.py"

        class_name = get_py_file_name_from_class_name("MyTest")
        assert class_name == "my_test.py"

        class_name = get_py_file_name_from_class_name("MyTESt")
        assert class_name == "my_test.py"

        class_name = get_py_file_name_from_class_name("MyTest1")
        assert class_name == "my_test1.py"

        class_name = get_py_file_name_from_class_name("MyTest2")
        assert class_name == "my_test2.py"

        class_name = get_py_file_name_from_class_name("A")
        assert class_name == "a.py"
