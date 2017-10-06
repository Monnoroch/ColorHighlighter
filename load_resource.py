"""A module with tools loading ST resources."""

import codecs
import os

try:
    from .st_helper import running_in_st
    from . import st_helper
    from . import path
except ValueError:
    from st_helper import running_in_st
    import st_helper
    import path

if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


def load_resource(file_path):
    """
    Polyfill for ST3 sublime.load_resource function.

    Arguments:
    - file_path - a resource path.
    Returns a string with the resource's content.
    """
    if st_helper.is_st3():
        return sublime.load_resource(file_path)

    file_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), file_path)
    return _read_file(file_path)


def load_binary_resource(file_path):
    """
    Polyfill for ST3 sublime.load_binary_resource function.

    Arguments:
    - file_path - a resource path.
    Returns a byte string with the resource's content.
    """
    if st_helper.is_st3():
        return sublime.load_binary_resource(file_path)

    file_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), file_path)
    return _read_binary_file(file_path)


def get_binary_resource_size(file_path):
    """
    Polyfill for ST3 sublime.load_binary_resource function.

    Arguments:
    - file_path - a resource path.
    Returns a byte string with the resource's content.
    """
    if st_helper.is_st3():
        return len(sublime.load_binary_resource(file_path))

    file_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), file_path)
    return os.path.getsize(file_path)


def _read_file(file_path):
    with codecs.open(file_path, "r", "utf-8") as file:
        return file.read()


def _read_binary_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()
