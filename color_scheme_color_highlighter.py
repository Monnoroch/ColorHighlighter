"""A color highlighter that uses color scheme scopes to highlight colors."""

import threading
from xml.etree import ElementTree

try:
    from .st_helper import running_in_st, is_st3
    from . import colors
    from .color_highlighter import ColorHighlighter
except ValueError:
    from st_helper import running_in_st, is_st3
    import colors
    from color_highlighter import ColorHighlighter

if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


class ColorSchemeBuilder(object):
    """A class for building a color scheme."""

    _scope_name_template = "CH_color_%s"
    _color_scope_template = """
<dict>
<key>name</key>
<string>CH_color</string>
<key>scope</key>
<string>CH_color_%s</string>
<key>settings</key>
<dict>
<key>background</key>
<string>%s</string>
<key>foreground</key>
<string>%s</string>
<key>caret</key>
<string>%s</string>
</dict>
</dict>
"""

    _text_scope_name_template = "CH_text_color_%s"
    _text_color_scope_template = """
<dict>
<key>scope</key>
<string>CH_text_color_%s</string>
<key>settings</key>
<dict>
<key>background</key>
<string>%s</string>
<key>foreground</key>
<string>%s</string>
<key>caret</key>
<string>%s</string>
</dict>
</dict>
"""

    def __init__(self, color_scheme_data, color_scheme_writer, async_update):
        """
        Init the ColorSchemeBuilder.

        Arguments:
        - color_scheme_data - a ColorSchemeData instance for a color scheme.
        - color_scheme_writer - a ColorSchemeWriter instance for a color scheme.
        - async_update - whether to update the color scheme asynchronously or not.
        """
        self._color_scheme_data = color_scheme_data
        self._color_scheme_writer = color_scheme_writer
        self._async_update = async_update
        self._lock = threading.Lock()

    def get_scopes(self, for_colors, for_text_coloring):
        """
        Get scope names for a list of colors.

        Arguments:
        - for_colors - a list of colors.
        - for_text_coloring - whether or not to return text highlighting scope names.
        Returns a list of scope names, one for each color.
        """
        scope_names = []
        for color in for_colors:
            background_color = self._color_scheme_data.background_color
            fixed_color = colors.background_color_for_text_workaround(color, background_color)
            color_name = fixed_color[1:]
            scope_names.append(self._get_color_name(for_text_coloring, color_name))
        if self._async_update:
            sublime.set_timeout_async(lambda: self._update_schema(for_colors), 0)
        else:
            self._update_schema(for_colors)
        return scope_names

    def _update_schema(self, for_colors):
        with self._lock:
            existing_colors = self._color_scheme_data.existing_colors
            scopes = []
            for color in for_colors:
                if color in existing_colors:
                    continue

                opposite_color = colors.complementary_color(color)
                background_color = self._color_scheme_data.background_color
                fixed_color = colors.background_color_for_text_workaround(color, background_color)
                fixed_background_color = colors.background_color_for_text_workaround(background_color, background_color)

                color_name = fixed_color[1:]
                scope = ElementTree.fromstring(
                    self._color_scope_template % (color_name, fixed_color, opposite_color, opposite_color))
                scopes.append(scope)
                text_scope = ElementTree.fromstring(
                    self._text_color_scope_template % (color_name, fixed_background_color, fixed_color, opposite_color))
                scopes.append(text_scope)
                existing_colors[color] = color_name
            if scopes:
                self._color_scheme_writer.add_scopes(scopes)

    def _get_color_name(self, for_text_coloring, color_name):
        if for_text_coloring:
            return self._text_scope_name_template % color_name
        return self._scope_name_template % color_name


class ColorSchemeColorHighlighter(ColorHighlighter):
    """A color highlighter that uses color scheme scopes to highlight colors."""

    region_name_template = "CH_color_%s_%d_%d"

    if is_st3():
        _region_style_flags = {
            "filled": sublime.DRAW_NO_OUTLINE,
            "text": sublime.DRAW_NO_OUTLINE,
            "outlined": sublime.DRAW_NO_FILL,
            "underlined_solid": sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE,
            "underlined_strippled": sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_STIPPLED_UNDERLINE,
            "underlined_squiggly": sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SQUIGGLY_UNDERLINE,
        }
    else:
        _region_style_flags = {
            "filled": 0,
            "text": 0,
            "outlined": sublime.DRAW_OUTLINED,
        }

    def __init__(self, view, style, color_scheme_builder, name, debug):  # pylint: disable=too-many-arguments
        """
        Init a ColorSchemeColorHighlighter.

        Arguments:
        - view - a view to highlight colors in.
        - style - the style of color highlighting.
        - color_scheme_builder - the color scheme builder to build regions for colors.
        - name - the name of the color highlighter.
        - debug - whether to enable debug mode.
        """
        assert style in ColorSchemeColorHighlighter._region_style_flags
        self._view = view
        self._color_scheme_builder = color_scheme_builder
        self._text_coloring = style == "text"
        self._flags = ColorSchemeColorHighlighter._region_style_flags[style]
        self._name = name
        self._debug = debug

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        if "values" not in context:
            context["values"] = []
        context["values"].append(value)

    def highlight_regions_done(self, context):  # noqa: D401
        """
        Called after all calls to highlight_region and unhighlight_region from highlight_regions have been made.

        Arguments:
        - context - a dict with color highlighter run data.
        """
        values = context.get("values", None)
        if not values:
            return

        colors_to_highlight = []
        for (_, color) in values:
            colors_to_highlight.append(color)
        scopes = self._color_scheme_builder.get_scopes(colors_to_highlight, self._text_coloring)

        for index, value in enumerate(values):
            (region, color) = value
            region_key = ColorSchemeColorHighlighter.region_name_template % (self._name, region.a, region.b)
            if self._debug:
                print("ColorHighlighter: action=highlight highlighter=ColorSchemeColorHighlighter region=%s color=%s"
                      % (region, color))
            self._view.add_regions(region_key, [region.region()], scopes[index], "", self._flags)

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        (region, _) = value
        region_key = ColorSchemeColorHighlighter.region_name_template % (self._name, region.a, region.b)
        self._view.erase_regions(region_key)
