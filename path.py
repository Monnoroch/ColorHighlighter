"""A module with tools for paths."""

import os

try:
    from .st_helper import running_in_st
except ValueError:
    from st_helper import running_in_st

if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


def normalize_path_for_st(path):
    """
    Normalize path for ST.

    On Linux, does nothing. On wildows, maps windows directory separators to linux ones, as ST wants linux
    directory separators.
    Arguments:
    - path - the path to normalize.
    """
    if sublime.platform() == "windows":
        return path.replace("\\", "/")
    return path


PLUGIN_NAME = "color_highlighter"
RELATIVE = True
ABSOLUTE = False


def packages_path(relative):
    """
    Get packages path.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    path = sublime.packages_path()
    if relative:
        path = os.path.basename(path)
    return path


def data_path(relative):
    """
    Get Color Highlighter path.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    return os.path.join(packages_path(relative), "User", PLUGIN_NAME)


def icons_path(relative):
    """
    Get Color Highlighter icons path.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    return os.path.join(data_path(relative), "icons")


def themes_path(relative):
    """
    Get Color Highlighter themes path.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    return os.path.join(data_path(relative), "themes")


def fake_color_scheme_path(color_scheme, relative):
    """
    Given a color scheme, get a fake color scheme path.

    Arguments:
    - color_scheme - color scheme sublime relative path.
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    Returns a path to the fake color scheme for this color scheme.
    """
    file_name = os.path.basename(color_scheme)
    return os.path.join(themes_path(relative), file_name)
