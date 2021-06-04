import codecs
import os

__ENCODING = "utf8"
__WRITE_MODE = "wb"
__READ_MODE = "rb"


def is_correct_python_file(filename):
    name = os.path.basename(filename)
    return name.endswith(".py") and not name.startswith("__")


def check_if_path_exists(path):
    if not os.path.exists(path):
        raise Exception(u"Path not found '%s'" % path)
    return True


def safe_remove_path(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def safe_create_path(path):
    if os.path.exists(path):
        return False
    is_dir = len(os.path.splitext(path)[-1]) == 0
    if is_dir:
        os.makedirs(path)
    else:
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        codecs.open(path, __WRITE_MODE, __ENCODING).close()


def save_file(path, content, is_text=True):
    if is_text:
        with codecs.open(path, __WRITE_MODE, encoding=__ENCODING) as f:
            f.write(content)
    else:
        with open(path, __WRITE_MODE) as f:
            f.write(content)


def read_file(path):
    with codecs.open(path, __READ_MODE, encoding=__ENCODING) as f:
        return f.read()


def get_list_of_files(path, recursively=False):
    files = []
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        if os.path.isdir(file_path) and recursively:
            files += get_list_of_files(file_path, recursively)
        else:
            files.append(file_path)
    return files
