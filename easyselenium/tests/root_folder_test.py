import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest.case import TestCase

from easyselenium.ui.root_folder import RootFolder


class RootFolderTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(RootFolderTest, cls).setUpClass()
        cls.tmp_dir = mkdtemp()

    @classmethod
    def tearDownClass(cls):
        super(RootFolderTest, cls).tearDownClass()
        if os.path.exists(cls.tmp_dir):
            rmtree(cls.tmp_dir)

    def test_prepare_root_folder(self):
        RootFolder.prepare_folder(self.tmp_dir)

        files_and_folders = os.listdir(self.tmp_dir)

        assert RootFolder.PO_FOLDER in files_and_folders
        assert RootFolder.TESTS_FOLDER in files_and_folders

        assert RootFolder.INIT_PY in os.listdir(
            os.path.join(self.tmp_dir, RootFolder.PO_FOLDER)
        )

        assert RootFolder.INIT_PY not in os.listdir(
            os.path.join(self.tmp_dir, RootFolder.TESTS_FOLDER)
        )
