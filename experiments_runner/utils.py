import os
from importlib.machinery import SourceFileLoader


def listdir_abs(folder):
    dirname = os.path.abspath(folder)
    for file in os.listdir(folder):
        yield os.path.join(dirname, file)


def dynamic_import(path):
    file = SourceFileLoader("tmp", path).load_module()
    return file
