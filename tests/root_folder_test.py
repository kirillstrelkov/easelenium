"""Root folder tests."""
from __future__ import annotations

import os
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest.case import TestCase

from easelenium.ui.root_folder import RootFolder


class RootFolderTest(TestCase):
    """Root folder tests."""

    @classmethod
    def setUpClass(cls: type[RootFolderTest]) -> None:
        """Setp up class."""
        super().setUpClass()
        cls.tmp_dir = mkdtemp()

    @classmethod
    def tearDownClass(cls: type[RootFolderTest]) -> None:
        """Tear down class."""
        super().tearDownClass()
        if Path(cls.tmp_dir).exists():
            rmtree(cls.tmp_dir)

    def test_prepare_root_folder(self) -> None:
        """Check root folder structure."""
        RootFolder.prepare_folder(self.tmp_dir)

        files_and_folders = os.listdir(self.tmp_dir)

        assert RootFolder.PO_FOLDER in files_and_folders
        assert RootFolder.TESTS_FOLDER in files_and_folders

        assert RootFolder.INIT_PY in os.listdir(
            Path(self.tmp_dir) / RootFolder.PO_FOLDER,
        )

        assert RootFolder.INIT_PY not in os.listdir(
            Path(self.tmp_dir) / RootFolder.TESTS_FOLDER,
        )
