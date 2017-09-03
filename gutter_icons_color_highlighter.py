"""A color highlighter that uses phantom sets to highlight colors."""

import os
import subprocess
import threading

try:
    from .st_helper import running_in_st
    from .debug import DEBUG
    from .path import normalize_path_for_st
    from .color_highlighter import ColorHighlighter
except ValueError:
    from st_helper import running_in_st
    from debug import DEBUG
    from path import normalize_path_for_st
    from color_highlighter import ColorHighlighter


if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


class IconFactory(object):
    """A class for generating gutter icons with different styles and colors."""

    _icon_style_circle = "circle"
    _icon_style_square = "square"
    _convert_styles = {
        _icon_style_circle: "circle 15,16 8,10",
        _icon_style_square: "rectangle 4,4 24,24"
    }
    _convert_command_template = (
        '%s -type TrueColorMatte -channel RGBA -size 32x32 -alpha transparent xc:none -fill "%s" -draw "%s" png32:"%s"')
    _icon_name_template = "%s_icon_%s.png"
    _bad_icon_name = "bad-icon.png"

    def __init__(self, icons_path, sublime_icons_path, convert_command, execute_timeout_seconds):
        """
        Init the icon factory.

        Arguments:
        - icons_path - an absolute path to the icons directory.
        - sublime_icons_path - a relative to ST Packages path to the icons directory.
        - convert_command - a convert tool path.
        - execute_timeout_seconds - the timeout in seconds to wait for convert to finish.
        """
        self._icons_path = icons_path
        self._sublime_icons_path = sublime_icons_path
        self._convert_command = convert_command
        self._execute_timeout_seconds = execute_timeout_seconds
        self._icons_cache = {}
        self._lock = threading.Lock()

    def get_icon_path(self, style, color):
        """
        Get the icon path given the icon style and color.

        If the icon does not exist, create it.
        Arguments:
        - style - the style of the icon.
        - color -- the color of the icon.
        Returns the icon path of None if creating the icon has failed.
        """
        assert style in self._convert_styles

        icon_name = self._icon_name_template % (style, color[1:])
        sublime_icon_path = normalize_path_for_st(os.path.join(self._sublime_icons_path, icon_name))
        # TODO(#5): return sublime_icon_path immediately and create icon in background.  # pylint: disable=fixme
        icon_path = os.path.join(self._icons_path, icon_name)
        convert_style = IconFactory._convert_styles[style]
        convert_command = IconFactory._convert_command_template % (
            self._convert_command, color, convert_style, icon_path)
        cache_key = (style, color)
        with self._lock:
            if cache_key in self._icons_cache:
                return self._icons_cache[cache_key]

            if os.path.exists(icon_path):
                self._icons_cache[cache_key] = sublime_icon_path
                return sublime_icon_path

            if DEBUG:
                print("ColorHighlighter: action=create_icon style=%s color=%s" % (style, color))

            self._run_command(convert_command)
            if os.path.exists(icon_path):
                self._icons_cache[cache_key] = sublime_icon_path
                return sublime_icon_path

        if DEBUG:
            print("ColorHighlighter: action=could_not_create_icon style=%s color=%s" % (style, color))
        return normalize_path_for_st(os.path.join(self._sublime_icons_path, IconFactory._bad_icon_name))

    def _run_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            output, error = process.communicate(timeout=self._execute_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            output, error = process.communicate()

        output = _decode_data(output)
        error = _decode_data(error)

        if error is not None and error != "":
            print("Traceback: error.\n\nOutput:\n%s\n\nError:\n%s" % (output, error))


class GutterIconsColorHighlighter(ColorHighlighter):
    """A color highlighter that uses gutter icons to highlight colors."""

    region_name_template = "CH_icon_%s_%d_%d"
    region_scope = "ch_gutter_icon"

    def __init__(self, view, icon_style, icon_factory, name):
        """
        Init a GutterIconsColorHighlighter.

        Arguments:
        - view - a view to highlight colors in.
        - icon_style - the icon style.
        - icon_factory - the icon factory to create icons with.
        - name - the name of the color highlighter.
        """
        assert icon_style in IconFactory._convert_styles  # pylint: disable=protected-access
        self._view = view
        self._icon_style = icon_style
        self._icon_factory = icon_factory
        self._name = name

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        (region, color) = value
        icon_path = self._icon_factory.get_icon_path(self._icon_style, color)
        region_key = GutterIconsColorHighlighter.region_name_template % (self._name, region.a, region.b)
        if DEBUG:
            print("ColorHighlighter: action=highlight highlighter=GutterIconsColorHighlighter region=%s color=%s"
                  % (region, color))
        self._view.add_regions(
            region_key, [region.region()], GutterIconsColorHighlighter.region_scope, icon_path, sublime.HIDDEN)

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        (region, _) = value
        region_key = GutterIconsColorHighlighter.region_name_template % (self._name, region.a, region.b)
        self._view.erase_regions(region_key)


def _decode_data(data):
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exception:
        return str(exception)
