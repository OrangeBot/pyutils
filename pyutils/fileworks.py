import os


def fix_path(path):
    return os.path.abspath(os.path.expanduser(path))


def read(path):
    with open(fix_path(path), 'r') as f:
        return f.read()


def write(what, where, mode='w'):
    with open(fix_path(where), mode=mode) as f:
        return f.write(what)


def get_password(path):
    if os.path.exists(fix_path(path)):
        return read(path)
    return path  # in case the actual password was passed instead of path to it - don't raise exception displaying it.
