import os
from importlib.machinery import SourceFileLoader


def listdir_abs(folder):
    dirname = os.path.abspath(folder)
    for file in os.listdir(folder):
        yield os.path.join(dirname, file)


def dynamic_import(path):
    file = SourceFileLoader("tmp", path).load_module()
    return file


class WorkingDirectory:
    def __init__(self, path) -> None:
        self.path = path
        self.cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, type, value, traceback):
        os.chdir(self.cwd)
