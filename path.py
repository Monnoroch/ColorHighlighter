"""A module with tools for paths."""

import os

try:
    from .st_helper import running_in_st
    from .settings import COLOR_HIGHLIGHTER_SETTINGS_NAME
except ValueError:
    from settings import COLOR_HIGHLIGHTER_SETTINGS_NAME
    from st_helper import running_in_st

if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


def normalize_path_for_st(path):
    """
    Normalize path for ST.

    On Linux, does nothing. On windows, maps windows directory separators to linux ones, as ST wants linux
    directory separators.
    Arguments:
    - path - the path to normalize.
    """
    if sublime.platform() == "windows":
        return path.replace("\\", "/")
    return path


RELATIVE = True
ABSOLUTE = False


def plugin_name():
    """
    Determine if the plugin is installed via a Package Control package or manually.

    Returns the plugin directory or package name.
    """
    manual_install_plugin_name = "ColorHighlighter"
    package_install_plugin_name = "Color Highlighter"
    if (os.path.exists(os.path.join(
            packages_path(ABSOLUTE), manual_install_plugin_name, COLOR_HIGHLIGHTER_SETTINGS_NAME))):
        return manual_install_plugin_name
    return package_install_plugin_name


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
    return os.path.join(packages_path(relative), "User", plugin_name())


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


def color_picker_path(relative):
    """
    Get color picker directory path.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    return os.path.join(data_path(relative), "ColorPicker")


def _color_picker_file():
    executable_suffix = None
    platform = sublime.platform()
    if platform == "windows":
        executable_suffix = "win.exe"
    else:
        executable_suffix = "%s_%s" % (platform, sublime.arch())
    return "ColorPicker_" + executable_suffix


def color_picker_file(relative):
    """
    Get color picker file.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    return os.path.join(color_picker_path(relative), _color_picker_file())


def color_picker_binary(relative):
    """
    Get color picker file.

    Arguments:
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    """
    path = os.path.join(packages_path(relative), plugin_name(), "ColorPicker", _color_picker_file())
    if relative:
        path = normalize_path_for_st(path)
    return path


def fake_color_scheme_path(color_scheme, relative):
    """
    Given a color scheme, get a fake color scheme path.

    Arguments:
    - color_scheme - color scheme sublime relative path.
    - relative - whether to get an absolute path or a relative to sublime packages directory.
    Returns a path to the fake color scheme for this color scheme.
    """
    file_name = os.path.basename(color_scheme)
    path = os.path.join(themes_path(relative), file_name)
    if relative:
        path = normalize_path_for_st(path)
    return path
