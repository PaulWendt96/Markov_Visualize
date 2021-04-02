from contextlib import contextmanager
import os
import shutil

@contextmanager
def make_temporary_directory(path, dir_name, remove_if_already_exists=False):
    ''' create a temporary directory, do stuff with it, and remove it '''
    assert os.path.isdir(path), "Error -- '{}' is not a directory".format(path)
    dir_path = os.path.join(path, dir_name)

    if not remove_if_already_exists:
        assert dir_name not in os.listdir(path), "Error -- a directory named '{}' already exists. " \
                                                 "Cannot create a temporary directory over a " \
                                                 "permanent directory".format(dir_name)
    else:
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)


    os.mkdir(dir_path)
    yield dir_path
    shutil.rmtree(dir_name)

def sample_save(text):
    def call(path):
        with open(path, 'w+') as f:
            f.write(text)
    return call

def save(objects, path, file_name, extension):
    # objects is a method that can save an object given a path argument
    for object in objects:
        object(os.path.join(path, file_name, extension))
