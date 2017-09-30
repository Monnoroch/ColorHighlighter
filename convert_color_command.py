"""A ST3 commands for converting colors between formats."""

try:
    from . import st_helper
    from .color_converter import ColorConverter
    from .color_searcher import ColorSearcher
    from .color_selection_listener import search_colors_in_selection
    from .regex_compiler import compile_regex
    from .settings import Settings, COLOR_HIGHLIGHTER_SETTINGS_NAME
except ValueError:
    import st_helper
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


class ColorHighlighterNextColor(sublime_plugin.TextCommand):
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
        for (region, color, format_name) in _get_colors(self.view, settings, formats, color_converter):
            index = formats.index(format_name) + 1
            if index == len(formats):
                index = 0
            new_format = formats[index]
            new_color = color_converter.from_color((color, new_format))
            if settings.debug:
                print(("ColorHighlighter: action=run_command name=color_highlighter_next_color region=%s format=%s " +
                       "color=%s new_format=%s new_color=%s")
                      % (str(region.region()), format_name, color, new_format, new_color))
            self.view.replace(edit, region.region(), new_color)

    def is_visible(self):
        """Check if the command can be ran."""
        return _any_colors_selected(self.view)


class ColorHighlighterPreviousColor(sublime_plugin.TextCommand):
    """Convert currently selected colors to a prevoius color format."""

    def run(self, edit):
        """
        Run the command.

        Arguments:
        - edit - an edit object.
        """
        settings = Settings(sublime.load_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME))
        formats = [value for value in sorted(settings.regex_compiler.formats.keys())]
        color_converter = ColorConverter(formats)
        for (region, color, format_name) in _get_colors(self.view, settings, formats, color_converter):
            index = formats.index(format_name) - 1
            if index == -1:
                index = len(formats) - 1
            new_format = formats[index]
            new_color = color_converter.from_color((color, new_format))
            if settings.debug:
                print(("ColorHighlighter: action=run_command name=color_highlighter_previous_color region=%s " +
                       "format=%s color=%s new_format=%s new_color=%s")
                      % (str(region.region()), format_name, color, new_format, new_color))
            self.view.replace(edit, region.region(), new_color)

    def is_visible(self):
        """Check if the command can be ran."""
        return _any_colors_selected(self.view)


def _get_colors(view, settings, formats, color_converter):
    color_searcher = ColorSearcher(compile_regex(settings.regex_compiler), color_converter)
    for (region, color, match) in search_colors_in_selection(view, color_searcher):
        format_name = _get_format_name(match, formats)
        yield region, color, format_name


def _any_colors_selected(view):
    settings = Settings(sublime.load_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME))
    formats = [value for value in sorted(settings.regex_compiler.formats.keys())]
    color_converter = ColorConverter(formats)
    color_searcher = ColorSearcher(compile_regex(settings.regex_compiler), color_converter)
    for _ in search_colors_in_selection(view, color_searcher):
        return True
    return False


def _get_format_name(match, formats):
    for name in formats:
        if match.get(name, None) is not None:
            return name
    raise Exception("Unreachable code.")
