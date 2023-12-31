"""Root folder."""
from __future__ import annotations

import os
from pathlib import Path

from easelenium.ui.file_utils import save_file


class RootFolder:
    """Root folder."""

    PO_FOLDER = "page_objects"
    TESTS_FOLDER = "tests"
    REPORTS = "reports"
    INIT_PY = "__init__.py"

    @classmethod
    def prepare_folder(cls: type[RootFolder], path: str) -> None:
        """Prepare root folder."""
        if Path(path).is_dir():
            files_and_folders = os.listdir(path)

            for folder in [cls.PO_FOLDER, cls.TESTS_FOLDER, cls.REPORTS]:
                if folder not in files_and_folders:
                    (Path(path) / folder).mkdir(parents=True, exist_ok=True)

            save_file(str(Path(path) / cls.PO_FOLDER / cls.INIT_PY), "")
        else:
            msg = f"'{path}' is not a folder."
            raise ValueError(msg)
