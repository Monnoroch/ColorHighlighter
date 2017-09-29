"""A module with data structures for plugin's settings."""

import copy

try:
    from . import st_helper
except ValueError:
    import st_helper


# Color Highlighter settings file name.
COLOR_HIGHLIGHTER_SETTINGS_NAME = "ColorHighlighter.sublime-settings"


class Settings(object):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """The data structure for holding plugin's settings."""

    def __init__(self, settings):
        """
        Init plugin's settings.

        Arguments:
        - settings - the plugin's settings dict.
        """
        self._settings = settings
        file_extensions = settings.get("file_extensions", [])
        self.file_extensions = {}
        for extension in file_extensions:
            self.file_extensions[extension] = True
        self.autoreload = _AutoreloadSettings(copy.deepcopy(settings.get("autoreload", {})))
        self.icon_factory = _IconFactorySettings(copy.deepcopy(settings.get("icon_factory", {})))
        self.search_colors_in = _SearchColorsSettings(copy.deepcopy(settings.get("search_colors_in", {})))
        self.regex_compiler = _RegexCompilerSettings(copy.deepcopy(settings.get("regex_compiler", {})))
        self.default_keybindings = settings.get("default_keybindings", True)
        self.experimental = _ExperimentalSettings(copy.deepcopy(settings.get("experimental", {})))
        self.debug = settings.get("debug", False)


class _ExperimentalSettings(object):  # pylint: disable=too-few-public-methods
    """Experimental settings that are not ready to be shipped for everyone yet."""

    def __init__(self, settings):
        """
        Init plugin's settings.

        Arguments:
        - settings - experimental settings dict.
        """
        self.asynchronosly_update_color_scheme = settings.get(  # pylint: disable=invalid-name
            "asynchronosly_update_color_scheme", False)
        if not st_helper.is_st3():
            print("Updating the color scheme asynchronously is not supported in ST2.")
            self.asynchronosly_update_color_scheme = False


class _AutoreloadSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding auto reload settings."""

    def __init__(self, settings):
        """
        Init auto reload settings.

        Arguments:
        - settings - the auto reload settings dict.
        """
        self.when_settings_change = settings.get("when_settings_change", False)
        self.when_color_scheme_change = settings.get("when_color_scheme_change", False)


class _IconFactorySettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding icon factory settings."""

    def __init__(self, settings):
        """
        Init icon factory settings.

        Arguments:
        - settings - the icon factory dict.
        """
        self.convert_command = settings.get("convert_command", "convert")
        self.convert_timeout = settings.get("convert_timeout", 5)


class _SearchColorsSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding color searching settings."""

    def __init__(self, settings):
        """
        Init color searching settings.

        Arguments:
        - settings - the color searching settings dict.
        """
        self.color_searcher_names = {"selection": True, "all_content": True, "hover": True}
        self.selection = _ColorSearcherSettings(settings.get("selection", {}), "selection")
        self.all_content = _ColorSearcherSettings(settings.get("all_content", {}), "all_content")
        self.hover = _ColorSearcherSettings(settings.get("hover", {}), "hover")
        if not st_helper.is_st3():
            print("Highlighting colors while hovering over them is not supported on ST2.")
            self.hover.enabled = False


class _ColorSearcherSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding color searcher settings."""

    def __init__(self, settings, name):
        """
        Init color searcher settings.

        Arguments:
        - settings - the color searcher settings dict.
        - name - the name of the color searcher.
        """
        self.name = name
        self.enabled = settings.get("enabled", False)
        self.color_highlighters = _ColorHighlighterSettings(settings.get("color_highlighters", {}))


class _ColorHighlighterSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding color highlihgting settings."""

    def __init__(self, settings):
        """
        Init color highlihgting settings.

        Arguments:
        - settings - the color highlihgting settings dict.
        """
        self.color_highlighter_names = {"color_scheme": True, "gutter_icons": True, "phantoms": True}
        self.color_scheme = ColorSchemeColorHighlighterSettings(settings.get("color_scheme", {}))
        self.gutter_icons = GutterIconsColorHighlighterSettings(settings.get("gutter_icons", {}))
        self.phantoms = _PhantomsColorHighlighterSettings(settings.get("phantoms", {}))


class ColorSchemeColorHighlighterSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding color scheme color highlihgter settings."""

    ST2_VALID_STYLES = ["filled", "text", "outlined"]
    ST3_VALID_STYLES = ["filled", "text", "outlined", "underlined_solid", "underlined_strippled", "underlined_squiggly"]

    def __init__(self, settings):
        """
        Init color scheme color highlihgter settings.

        Arguments:
        - settings - the color scheme color highlihgter settings dict.
        """
        if st_helper.is_st3():
            valid_styles = self.ST3_VALID_STYLES
        else:
            valid_styles = self.ST2_VALID_STYLES
        self.enabled = settings.get("enabled", False)
        self.highlight_style = settings.get("highlight_style", "filled")
        assert self.highlight_style in valid_styles


class GutterIconsColorHighlighterSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding gutter icons color highlihgter settings."""

    VALID_STYLES = ["circle", "square"]

    def __init__(self, settings):
        """
        Init gutter icons color highlihgter settings.

        Arguments:
        - settings - the gutter icons color highlihgter settings dict.
        """
        self.enabled = settings.get("enabled", False)
        self.icon_style = settings.get("icon_style", "circle")
        assert self.icon_style in self.VALID_STYLES
        if not st_helper.is_st3():
            print("Highlighting colors with gutter icons is not supported on ST2.")
            self.enabled = False


class _PhantomsColorHighlighterSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding phantoms color highlihgter settings."""

    def __init__(self, settings):
        """
        Init phantoms color highlihgter settings.

        Arguments:
        - settings - the phantoms color highlihgter settings dict.
        """
        self.enabled = settings.get("enabled", False)
        if not st_helper.is_st3():
            print("Highlighting colors with phantoms is not supported on ST2.")
            self.enabled = False


class _RegexCompilerSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding regex compiler settings."""

    def __init__(self, settings):
        """
        Init regex compiler settings.

        Arguments:
        - settings - the regex compiler settings dict.
        """
        self.channels = settings.get("channels", {})
        self.formats = {}
        formats_settings = settings.get("formats", {})
        for name in formats_settings:
            self.formats[name] = _ColorFormatSettings(formats_settings.get(name, {}))


class _ColorFormatSettings(object):  # pylint: disable=too-few-public-methods
    """The data structure for holding color format settings."""

    def __init__(self, settings):
        """
        Init color format settings.

        Arguments:
        - settings - the color format settings dict.
        """
        self.description = settings["description"]
        self.regex = settings["regex"]
        self.white = settings["white"]
        after = settings.get("after", [])
        if not isinstance(after, list):
            after = [after]
        self.after = after
