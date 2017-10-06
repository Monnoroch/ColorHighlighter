"""A color highlighter that uses color scheme scopes to highlight colors."""

import os
from xml.etree import ElementTree

try:
    from . import st_helper
except ValueError:
    import st_helper

try:
    from . import path
    from . import colors
    from . import load_resource
    from .gutter_icons_color_highlighter import GutterIconsColorHighlighter
except ValueError:
    import path
    import colors
    import load_resource
    from gutter_icons_color_highlighter import GutterIconsColorHighlighter


# NOTE: keep in sync with ColorSchemeBuilder._color_scope_template.
CH_COLOR_SCOPE_NAME = "CH_color"


def parse_color_scheme(color_scheme, debug):
    """
    Load, parse, validate and prepare the color scheme.

    Arguments:
    - color_scheme - the color scheme name to process.
    Returns the new color scheme and a ColorSchemeData and a ColorSchemeWriter for input color scheme.
    """
    fake_color_scheme = path.fake_color_scheme_path(color_scheme, path.ABSOLUTE)
    new_color_scheme = path.fake_color_scheme_path(color_scheme, path.RELATIVE)
    if color_scheme != new_color_scheme:
        if os.path.exists(fake_color_scheme):
            color_scheme = new_color_scheme
    color_scheme_content = load_resource.load_resource(color_scheme)
    if not st_helper.is_st3():
        color_scheme_content = color_scheme_content.encode("utf-8")
    color_scheme_xml = ElementTree.fromstring(color_scheme_content)
    scopes_array_element = _get_array_element(color_scheme_xml)
    if scopes_array_element is None:
        return None

    scheme_settings_element = _get_scheme_settings_element(scopes_array_element)
    if scheme_settings_element is None:
        return None

    background_color = _get_value_child_with_tag(scheme_settings_element, "background", "string")
    if background_color is None:
        return None

    existing_colors = _load_colors(scopes_array_element)
    background_color = colors.normalize_hex_color(background_color.text)
    color_scheme_data = ColorSchemeData(background_color, existing_colors)
    color_scheme_writer = ColorSchemeWriter(
        fake_color_scheme, ElementTree.ElementTree(color_scheme_xml), scopes_array_element, debug)
    return new_color_scheme, color_scheme_data, color_scheme_writer


class ColorSchemeData(object):  # pylint: disable=too-few-public-methods
    """Data object with all the data loaded from a color scheme."""

    def __init__(self, background_color, existing_colors):
        """
        Create a color scheme data.

        Argumets:
        - background_color - the background color of a color scheme.
        - existing_colors - the colors from color highlighter scopes, written to this color scheme.
        """
        self.background_color = background_color
        self.existing_colors = existing_colors


class ColorSchemeWriter(object):
    """A class that writes elements to a color scheme."""

    def __init__(self, color_scheme, xml_tree, scopes_array_element, debug):
        """
        Create a ColorSchemeWriter.

        Arguments:
        - color_scheme - an absolute path to a color scheme.
        - xml_tree - an ElementTree object for the color scheme.
        - scopes_array_element - an Element that represents the dict array in the color scheme XML.
        - debug - whether to enable debug mode.
        """
        self._color_scheme = color_scheme
        self._xml_tree = xml_tree
        self._scopes_array_element = scopes_array_element
        self._debug = debug

    def add_scopes(self, scopes):
        """
        Add scopes to the color scheme.

        Arguments:
        - scopes -- an iterable of Elements with scopes to add.
        """
        self._scopes_array_element.extend(scopes)
        if self._debug:
            packages_path = os.path.dirname(path.packages_path(path.ABSOLUTE))
            print("ColorHighlighter: action=write_color_scheme scheme=%s" % self._color_scheme[len(packages_path) + 1:])

        init_color_scheme_dir()
        self._xml_tree.write(self._color_scheme, encoding="utf-8")
        try:
            os.remove(path.cached_scheme_path(self._color_scheme))
        except FileNotFoundError:
            # No cache -- no problems.
            pass

    def fix_color_scheme_for_gutter_colors(self):  # pylint: disable=invalid-name
        """Fix color scheme for gutter icons to work properly."""
        for child in self._scopes_array_element:
            if child.tag != "dict":
                continue

            scope = _get_value_child_with_tag(child, "scope", "string")
            if scope is None:
                continue
            # The scheme is already fixed.
            if scope == GutterIconsColorHighlighter.region_scope:
                return

        if self._debug:
            print("ColorHighlighter: action=fix_color_scheme")
        self.add_scopes([ElementTree.fromstring("""
<dict>
    <key>name</key>
    <string>CH_color_scheme_fix</string>
    <key>scope</key>
    <string>%s</string>
    <key>settings</key>
    <dict>
        <key>foreground</key>
        <string>#ffffff</string>
    </dict>
</dict>
""" % GutterIconsColorHighlighter.region_scope)])


def _get_child_by_tag(element, child_tag):
    for child in element:
        if child.tag == child_tag:
            return child
    return None


def _get_value_child_with_tag(element, key, tag):
    for child_index, child in enumerate(element):
        if child.tag == "key" and child.text == key:
            if child_index + 1 < len(element):
                next_child = element[child_index + 1]
                if next_child.tag == tag:
                    return next_child
    return None


def _get_array_element(xml):
    dict_element = _get_child_by_tag(xml, "dict")
    if dict_element is None:
        print(2)
        return None

    return _get_value_child_with_tag(dict_element, "settings", "array")


def _get_scheme_settings_element(array_element):
    for child in array_element:
        if child.tag != "dict":
            continue

        settings = _get_value_child_with_tag(child, "settings", "dict")
        if settings is not None:
            scope = _get_value_child_with_tag(settings, "scope", "string")
            if scope is None:
                return settings
    return None


def _load_colors(scopes_array_element):
    existing_colors = {}
    for child in scopes_array_element:
        if child.tag != "dict":
            continue

        name = _get_value_child_with_tag(child, "name", "string")
        if name is None:
            continue
        if name.text != CH_COLOR_SCOPE_NAME:
            continue

        settings = _get_value_child_with_tag(child, "settings", "dict")
        if settings is None:
            continue

        background = _get_value_child_with_tag(settings, "background", "string")
        if background is None:
            continue

        color = background.text
        existing_colors[color] = color[1:]
    return existing_colors


def init_color_scheme_dir():
    """Initialise the directory for color schemes."""
    _create_if_not_exists(path.data_path(path.ABSOLUTE))
    _create_if_not_exists(path.themes_path(path.ABSOLUTE))


def _create_if_not_exists(path_to_create):
    if not os.path.exists(path_to_create):
        os.mkdir(path_to_create)
