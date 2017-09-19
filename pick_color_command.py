"""A ST3 commands for converting colors between formats."""

import subprocess

try:
    from . import st_helper
    from . import path
    from .color_converter import ColorConverter
    from .color_searcher import ColorSearcher
    from .color_selection_listener import search_colors_in_selection
    from .debug import DEBUG
    from .regex_compiler import compile_regex
    from .settings import Settings, COLOR_HIGHLIGHTER_SETTINGS_NAME
except ValueError:
    import st_helper
    import path
    from color_converter import ColorConverter
    from color_searcher import ColorSearcher
    from color_selection_listener import search_colors_in_selection
    from debug import DEBUG
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

    def run(self, edit):
        """
        Run the command.

        Arguments:
        - edit - an edit object.
        """
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
            if DEBUG:
                print("ColorHighlighter: action=run_command name=color_highlighter_pick_color result=canceled")
            return

        if replace_colors:
            for (region, _, format_name) in colors:
                new_color = color_converter.from_color((output, format_name))
                if DEBUG:
                    print(("ColorHighlighter: action=run_command name=color_highlighter_pick_color result=replace " +
                           "region=%s format=%s color=%s") % (str(region.region()), format_name, new_color))
                self.view.replace(edit, region.region(), new_color)
        else:
            for region in self.view.sel():
                self.view.replace(edit, region, output)


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
