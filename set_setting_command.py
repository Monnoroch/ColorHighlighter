"""A ST3 command for setting plugin settings."""

try:
    from . import st_helper
    from .settings import COLOR_HIGHLIGHTER_SETTINGS_NAME, ColorSchemeColorHighlighterSettings, Settings
except ValueError:
    import st_helper
    from settings import COLOR_HIGHLIGHTER_SETTINGS_NAME, ColorSchemeColorHighlighterSettings, Settings


if st_helper.running_in_st():
    import sublime  # pylint: disable=import-error
    import sublime_plugin  # pylint: disable=import-error
else:
    from . import sublime
    from . import sublime_plugin


class ColorHighlighterSetSetting(sublime_plugin.ApplicationCommand):
    """
    A ST3 command for setting plugin settings.

    It supports:
    - Regular settings that just get set.
    - Boolean settings that get flipped.
    - Enum settings that have a special "none" value that gets mapped to flipping a specified boolean setting.
    - Computed boolean settings which get automatically recomputed every time it's dependencies are recomputed.
    - Disabling some settings or setting prefixes for ST2.
    """

    _BOOL_SETTINGS = [
        "autoreload.when_settings_change",
        "autoreload.when_color_scheme_change",
        "search_colors_in.selection.enabled",
        "search_colors_in.selection.color_highlighters.color_scheme.enabled",
        "search_colors_in.selection.color_highlighters.gutter_icons.enabled",
        "search_colors_in.selection.color_highlighters.phantoms.enabled",
        "search_colors_in.all_content.enabled",
        "search_colors_in.all_content.color_highlighters.color_scheme.enabled",
        "search_colors_in.all_content.color_highlighters.gutter_icons.enabled",
        "search_colors_in.all_content.color_highlighters.phantoms.enabled",
        "search_colors_in.hover.enabled",
        "search_colors_in.hover.color_highlighters.color_scheme.enabled",
        "search_colors_in.hover.color_highlighters.gutter_icons.enabled",
        "search_colors_in.hover.color_highlighters.phantoms.enabled",
        "default_keybindings",
        "experimental.asynchronosly_update_color_scheme",
    ]

    # A key is an enum setting and a value is the boolean setting that gets disabled when the value setting is set to
    # none.
    _ENUM_SETTINGS = {
        "search_colors_in.selection.color_highlighters.color_scheme.highlight_style":
            "search_colors_in.selection.color_highlighters.color_scheme.enabled",
        "search_colors_in.selection.color_highlighters.gutter_icons.icon_style":
            "search_colors_in.selection.color_highlighters.gutter_icons.enabled",
        "search_colors_in.all_content.color_highlighters.color_scheme.highlight_style":
            "search_colors_in.all_content.color_highlighters.color_scheme.enabled",
        "search_colors_in.all_content.color_highlighters.gutter_icons.icon_style":
            "search_colors_in.all_content.color_highlighters.gutter_icons.enabled",
        "search_colors_in.hover.color_highlighters.color_scheme.highlight_style":
            "search_colors_in.hover.color_highlighters.color_scheme.enabled",
        "search_colors_in.hover.color_highlighters.gutter_icons.icon_style":
            "search_colors_in.hover.color_highlighters.gutter_icons.enabled",
    }

    # A key is a boolean setting, a value is a list of boolean settings that need to be OR-ed to compute the key
    # setting.
    _COMPUTED_BOOLEAN_SETTINGS = {
        "search_colors_in.selection.enabled": [
            "search_colors_in.selection.color_highlighters.color_scheme.enabled",
            "search_colors_in.selection.color_highlighters.gutter_icons.enabled",
            "search_colors_in.selection.color_highlighters.phantoms.enabled",
        ],
        "search_colors_in.all_content.enabled": [
            "search_colors_in.all_content.color_highlighters.color_scheme.enabled",
            "search_colors_in.all_content.color_highlighters.gutter_icons.enabled",
            "search_colors_in.all_content.color_highlighters.phantoms.enabled",
        ],
        "search_colors_in.hover.enabled": [
            "search_colors_in.hover.color_highlighters.color_scheme.enabled",
            "search_colors_in.hover.color_highlighters.gutter_icons.enabled",
            "search_colors_in.hover.color_highlighters.phantoms.enabled",
        ]
    }

    # A key is a setting prefix, a value is either a boolean, in which case the whole prefix is disabled for ST2 or
    # a list of values for this setting unsupported in ST2.
    _ST2_UNSUPPORTED_SETTINGS = {
        "search_colors_in.selection.color_highlighters.color_scheme.highlight_style":
            list(set(ColorSchemeColorHighlighterSettings.ST3_VALID_STYLES) -
                 set(ColorSchemeColorHighlighterSettings.ST2_VALID_STYLES)),
        "search_colors_in.all_content.color_highlighters.color_scheme.highlight_style":
            list(set(ColorSchemeColorHighlighterSettings.ST3_VALID_STYLES) -
                 set(ColorSchemeColorHighlighterSettings.ST2_VALID_STYLES)),
        "search_colors_in.selection.color_highlighters.gutter_icons": True,
        "search_colors_in.selection.color_highlighters.phantoms": True,
        "search_colors_in.all_content.color_highlighters.gutter_icons": True,
        "search_colors_in.all_content.color_highlighters.phantoms": True,
        "search_colors_in.hover": True,
        "experimental.asynchronosly_update_color_scheme": True,
    }

    def run(self, setting, **args):
        """
        Run the command.

        Arguments:
        - setting - the setting name.
        - args - other args as a dict.
        """
        value = self._get_value(setting, **args)
        if self._is_enum_setting(setting):
            enable_setting = self._ENUM_SETTINGS[setting]
            if value == "none":
                _set_setting(enable_setting, False)
                self._recompute_settings([enable_setting])
            else:
                _set_setting(enable_setting, True)
                _set_setting(setting, value)
                self._recompute_settings([setting, enable_setting])
            return
        _set_setting(setting, value)
        self._recompute_settings([setting])

    def is_checked(self, setting, **args):
        """
        Return True if the setting is enabled or False otherwise.

        Arguments:
        - setting - the setting name.
        - args - other args as a dict.
        """
        if self._is_bool_setting(setting):
            return _get_setting(setting)
        if self._is_enum_setting(setting):
            enable_setting = self._ENUM_SETTINGS[setting]
            if not _get_setting(enable_setting):
                return args["value"] == "none"
            return _get_setting(setting) == args["value"]
        return False

    def is_visible(self, setting, **args):
        """
        Return True if the setting is supported or False otherwise.

        Arguments:
        - setting - the setting name.
        - args - other args as a dict.
        """
        if st_helper.is_st3():
            return True
        support_data = self._get_st2_unsupported_prefix(setting)
        if support_data is None:
            return True
        if isinstance(support_data, bool):
            return False
        return self._get_value(setting, **args) not in support_data

    def _get_st2_unsupported_prefix(self, setting):
        for setting_prefix in self._ST2_UNSUPPORTED_SETTINGS:
            if setting.startswith(setting_prefix):
                return self._ST2_UNSUPPORTED_SETTINGS[setting_prefix]
        return None

    def _recompute_settings(self, changed_settings):
        if not changed_settings:
            return
        settings_to_recompute = []
        for computed_setting in self._COMPUTED_BOOLEAN_SETTINGS:
            for setting in self._COMPUTED_BOOLEAN_SETTINGS[computed_setting]:
                if setting in changed_settings:
                    settings_to_recompute.append(computed_setting)
        for setting_to_recompute in settings_to_recompute:
            ored_value = False
            for setting in self._COMPUTED_BOOLEAN_SETTINGS[setting_to_recompute]:
                ored_value = ored_value or _get_setting(setting)
            _set_setting(setting_to_recompute, ored_value)
        self._recompute_settings(settings_to_recompute)

    def _get_value(self, setting, **args):
        if self._is_bool_setting(setting):
            return not _get_setting(setting)
        return args["value"]

    def _is_bool_setting(self, setting):
        return setting in self._BOOL_SETTINGS

    def _is_enum_setting(self, setting):
        return setting in self._ENUM_SETTINGS


def _get_setting(setting):
    setting_path = setting.split(".")
    settings = sublime.load_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME)
    setting_value = settings.get(setting_path[0])
    if len(setting_path) == 1:
        return setting_value
    for name in setting_path[1:-1]:
        setting_value = setting_value[name]
    return setting_value[setting_path[-1]]


def _set_setting(setting, value):
    settings = sublime.load_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME)
    if Settings(settings).debug:
        print("ColorHighlighter: action=run_command name=color_highlighter_set_setting setting=%s value=%s"
              % (setting, value))
    setting_path = setting.split(".")
    if len(setting_path) == 1:
        settings.set(setting_path[0], value)
        return
    top_level_setting = settings.get(setting_path[0])
    setting_value = top_level_setting
    for name in setting_path[1:-1]:
        setting_value = setting_value[name]
    setting_value[setting_path[-1]] = value
    settings.set(setting_path[0], top_level_setting)
    sublime.save_settings(COLOR_HIGHLIGHTER_SETTINGS_NAME)
