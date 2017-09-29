"""A ST3 commands for converting colors between formats."""

import subprocess
import threading

from ast import literal_eval

try:
    from . import st_helper
    from . import path
    from .color_converter import ColorConverter
    from .color_searcher import ColorSearcher
    from .color_selection_listener import search_colors_in_selection
    from .regex_compiler import compile_regex
    from .settings import Settings, COLOR_HIGHLIGHTER_SETTINGS_NAME
except ValueError:
    import st_helper
    import path
    from color_converter import ColorConverter
    from color_searcher import ColorSearcher
    from color_selection_listener import search_colors_in_selection
    from regex_compiler import compile_regex
    from settings import Settings, COLOR_HIGHLIGHTER_SETTINGS_NAME


if st_helper.running_in_st():
    import sublime  # pylint: disable=import-error
    import sublime_plugin  # pylint: disable=import-error
else:
    from . import sublime
    from . import sublime_plugin


class ColorHighlighterPickColor(sublime_plugin.TextCommand):
    """Convert currently selected colors to a next color format."""

    def run(self, edit):  # pylint: disable=unused-argument
        """
        Run the command.

        Arguments:
        - edit - an edit object.
        """
        _run_async(self._open_color_picker)

    def _open_color_picker(self):
        settings = Settings(sublime.load_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME))
        formats = [value for value in sorted(settings.regex_compiler.formats.keys())]
        color_converter = ColorConverter(formats)
        colors = [value for value in _get_colors(self.view, settings, formats, color_converter)]
        replace_colors = len(colors) > 0
        if replace_colors:
            initial_color = colors[0][1][1:]
        else:
            initial_color = "FFFFFFFF"
        popen = subprocess.Popen(
            [path.color_picker_file(path.ABSOLUTE), initial_color],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        output, error = popen.communicate()
        output = output.decode("utf-8")
        error = error.decode("utf-8")
        if error is not None and error:
            print("Color Picker error:\n" + error)

        if output == "CANCEL":
            if settings.debug:
                print("ColorHighlighter: action=run_command name=color_highlighter_pick_color result=canceled")
            return

        replace_data = []
        if replace_colors:
            for (region, _, format_name) in colors:
                new_color = color_converter.from_color((output, format_name))
                if settings.debug:
                    print(("ColorHighlighter: action=run_command name=color_highlighter_pick_color result=replace " +
                           "region=%s format=%s color=%s") % (region.region(), format_name, new_color))
                replace_data.append((region.region(), new_color))
        else:
            for region in self.view.sel():
                if settings.debug:
                    print(("ColorHighlighter: action=run_command name=color_highlighter_pick_color result=insert " +
                           "region=%s color=%s") % (region, output))
                replace_data.append((region, output))
        self.view.run_command("color_highlighter_impl_replace_color", {"replace_data": str(replace_data)})


def _get_colors(view, settings, formats, color_converter):
    color_searcher = ColorSearcher(compile_regex(settings.regex_compiler), color_converter)
    for (region, color, match) in search_colors_in_selection(view, color_searcher):
        format_name = _get_format_name(match, formats)
        yield region, color, format_name


def _get_format_name(match, formats):
    for name in formats:
        if match.get(name, None) is not None:
            return name
    raise Exception("Unreachable code.")


class ColorHighlighterImplReplaceColor(sublime_plugin.TextCommand):
    """Replace texts in a list of regions."""

    def run(self, edit, replace_data):
        """
        Run the command.

        Arguments:
        - edit - an edit object.
        - replace_data - string representation of a list of (region, color) pairs.
        """
        regions_to_replace = literal_eval(replace_data)
        offset = 0
        for (region, color) in sorted(regions_to_replace):
            self.view.replace(edit, sublime.Region(offset + region[0], offset + region[1]), color)
            offset -= (region[1] - region[0])
            offset += len(color)


def _run_async(callback):
    if st_helper.is_st3():
        sublime.set_timeout_async(callback, 0)
    else:
        _RunAsync(callback).start()


class _RunAsync(threading.Thread):
    def __init__(self, callback):
        self.callback = callback
        threading.Thread.__init__(self)

    def run(self):
        self.callback()
