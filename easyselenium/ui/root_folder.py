import os

from easyselenium.ui.file_utils import save_file


class RootFolder(object):
    PO_FOLDER = u"page_objects"
    TESTS_FOLDER = u"tests"
    REPORTS = u"reports"
    INIT_PY = u"__init__.py"

    @classmethod
    def prepare_folder(cls, path):
        if os.path.isdir(path):
            files_and_folders = os.listdir(path)

            for folder in [cls.PO_FOLDER, cls.TESTS_FOLDER, cls.REPORTS]:
                if folder not in files_and_folders:
                    os.mkdir(os.path.join(path, folder))

            save_file(os.path.join(path, cls.PO_FOLDER, cls.INIT_PY), u"")
        else:
            raise Exception(u"'%s' is not a folder." % path)
