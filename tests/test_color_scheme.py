"""Tests for parse_color_scheme."""

import os
import unittest

from xml.etree.ElementTree import ParseError

from ColorHighlighter import load_resource, path, sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.color_scheme import (  # pylint: disable=no-name-in-module,import-error
    CH_COLOR_SCOPE_NAME, ColorSchemeData, ColorSchemeWriter, parse_color_scheme)

from mockito import ANY, mock, verify, when


class ParseColorSchemeTest(unittest.TestCase):
    """Tests for parse_color_scheme."""

    def test_invalid_xml(self):
        """Parsing invalid XML fails."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("<")
        with self.assertRaises(ParseError):
            parse_color_scheme("", False)

    def test_no_dict(self):
        """There should be a top-level dict tag."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("<root></root>")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_no_settings_array(self):
        """The top-level dict should have a settings key."""
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
</dict>
</root>""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_non_array_settings(self):
        """The top-level dict should have an array settings key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <a></a>
</dict>
</root>""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_no_dicts(self):
        """The settings array should have dict elements."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <a></a>
    </array>
</dict>
</root>""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_scheme_scope_no_settings(self):  # pylint: disable=invalid-name
        """The scope dict should have a settings key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict></dict>
    </array>
</dict>
</root>
""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_scheme_scope_non_dict_settings(self):  # pylint: disable=invalid-name
        """The scope dict should have a dict settings key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <a></a>
        </dict>
    </array>
</dict>
</root>
""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_scheme_scope_has_scope(self):  # pylint: disable=invalid-name
        """The scope dict should not have a scope key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>scope</key>
                <string></string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_scheme_scope_does_not_have_background(self):  # pylint: disable=invalid-name
        """The scheme scope settings should have a background key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_array_scheme_scope_does_non_string_background(self):  # pylint: disable=invalid-name
        """The scheme scope settings should have a string background key."""
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn("")
        when(load_resource).load_resource(ANY).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <a></a>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        self.assertEqual(None, parse_color_scheme("", False))

    def test_parse_color_scheme(self):
        """Test parsing color scheme."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FFFFFFFF</string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        new_color_scheme, color_scheme_data, color_scheme_writer = parse_color_scheme(scheme_path, False)
        self.assertEqual(path.fake_color_scheme_path(scheme_path, path.RELATIVE), new_color_scheme)
        self.assertEqual("#FFFFFFFF", color_scheme_data.background_color)
        self.assertEqual({}, color_scheme_data.existing_colors)
        self.assertEqual(
            path.fake_color_scheme_path(scheme_path, path.ABSOLUTE),
            color_scheme_writer._color_scheme)  # pylint: disable=protected-access
        self.assertEqual("root", color_scheme_writer._xml_tree.getroot().tag)  # pylint: disable=protected-access
        self.assertEqual("array", color_scheme_writer._scopes_array_element.tag)  # pylint: disable=protected-access

    def test_normalize_background(self):
        """Test background color is normalized."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#111</string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual("#111FFFFF", color_scheme_data.background_color)

    def test_colors_no_settings(self):
        """Test existing colors should have a settings key."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
        </dict>
    </array>
</dict>
</root>
""" % (CH_COLOR_SCOPE_NAME))
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual({}, color_scheme_data.existing_colors)

    def test_colors_non_dict_settings(self):
        """Test existing colors should have a dict settings key."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
            <key>settings</key>
            <a></a>
        </dict>
    </array>
</dict>
</root>
""" % (CH_COLOR_SCOPE_NAME))
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual({}, color_scheme_data.existing_colors)

    def test_colors_no_background(self):
        """Test existing color settings should have a background key."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
            <key>settings</key>
            <a></a>
        </dict>
    </array>
</dict>
</root>
""" % (CH_COLOR_SCOPE_NAME))
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual({}, color_scheme_data.existing_colors)

    def test_colors_non_string_background(self):  # pylint: disable=invalid-name
        """Test existing color settings should have a string background key."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <a></a>
            </dict>
        </dict>
    </array>
</dict>
</root>
""" % (CH_COLOR_SCOPE_NAME))
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual({}, color_scheme_data.existing_colors)

    def test_load_colors(self):
        """Test existing colors are loaded."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        package_path = "/a/b/Packages"
        when(os.path).exists(ANY).thenReturn(False)
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(scheme_path).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#1</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>%s</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#2</string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""" % (CH_COLOR_SCOPE_NAME, CH_COLOR_SCOPE_NAME))
        _, color_scheme_data, _ = parse_color_scheme(scheme_path, False)
        self.assertEqual({"#1": "1", "#2": "2"}, color_scheme_data.existing_colors)

    def test_parse_fake_color_scheme_exists(self):  # pylint: disable=invalid-name
        """Test parsing color scheme when it's fake color scheme already exists."""
        scheme = "Scheme.tmTheme"
        scheme_path = "Packages/Color/" + scheme
        fake_color_scheme = path.fake_color_scheme_path(scheme_path, path.ABSOLUTE)
        fake_color_scheme_sublime = path.fake_color_scheme_path(scheme_path, path.RELATIVE)
        when(os.path).exists(fake_color_scheme).thenReturn(True)
        package_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(fake_color_scheme_sublime).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FFFFFFFF</string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        new_color_scheme, color_scheme_data, color_scheme_writer = parse_color_scheme(scheme_path, False)
        self.assertEqual(fake_color_scheme_sublime, new_color_scheme)
        self.assertEqual("#FFFFFFFF", color_scheme_data.background_color)
        self.assertEqual({}, color_scheme_data.existing_colors)
        self.assertEqual(fake_color_scheme, color_scheme_writer._color_scheme)  # pylint: disable=protected-access
        self.assertEqual("root", color_scheme_writer._xml_tree.getroot().tag)  # pylint: disable=protected-access
        self.assertEqual("array", color_scheme_writer._scopes_array_element.tag)  # pylint: disable=protected-access

    def test_parse_fake_color_scheme(self):
        """Test parsing fake color scheme."""
        scheme_path = "Packages/Color/Scheme.tmTheme"
        fake_color_scheme = path.fake_color_scheme_path(scheme_path, path.ABSOLUTE)
        fake_color_scheme_sublime = path.fake_color_scheme_path(scheme_path, path.RELATIVE)
        when(os.path).exists(fake_color_scheme).thenReturn(False)
        package_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(package_path)
        when(load_resource).load_resource(fake_color_scheme_sublime).thenReturn("""
<root>
<dict>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FFFFFFFF</string>
            </dict>
        </dict>
    </array>
</dict>
</root>
""")
        new_color_scheme, color_scheme_data, color_scheme_writer = parse_color_scheme(fake_color_scheme_sublime, False)
        self.assertEqual(fake_color_scheme_sublime, new_color_scheme)
        self.assertEqual("#FFFFFFFF", color_scheme_data.background_color)
        self.assertEqual({}, color_scheme_data.existing_colors)
        self.assertEqual(fake_color_scheme, color_scheme_writer._color_scheme)  # pylint: disable=protected-access
        self.assertEqual("root", color_scheme_writer._xml_tree.getroot().tag)  # pylint: disable=protected-access
        self.assertEqual("array", color_scheme_writer._scopes_array_element.tag)  # pylint: disable=protected-access


class ColorSchemeDataTest(unittest.TestCase):
    """Tests for ColorSchemeData."""

    def test_create(self):
        """Test creating ColorSchemeData."""
        background_color = "color"
        colors = {"key": "value"}
        data = ColorSchemeData(background_color, colors)
        self.assertEqual(background_color, data.background_color)
        self.assertEqual(colors, data.existing_colors)


class ColorSchemeWriterTest(unittest.TestCase):
    """Tests for ColorSchemeWriter."""

    def test_add_scopes(self):
        """Test that add_scopes adds scopes and writes the file."""
        xml_tree = mock()
        color_scheme = "test color scheme"
        initial_scopes = ["test"]
        scopes = initial_scopes[:]
        color_scheme_writer = ColorSchemeWriter(color_scheme, xml_tree, scopes, False)
        new_scopes = ["scope1", "scope2"]
        color_scheme_writer.add_scopes(new_scopes)
        self.assertEqual(initial_scopes + new_scopes, scopes)
        verify(xml_tree).write(color_scheme, encoding="utf-8")
