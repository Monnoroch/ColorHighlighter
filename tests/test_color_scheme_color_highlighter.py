"""Tests for color_scheme_color_highlighter."""

import unittest

from xml.etree import ElementTree

from ColorHighlighter import sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.color_scheme import ColorSchemeData  # pylint: disable=no-name-in-module,import-error
from ColorHighlighter.color_scheme_color_highlighter import (  # pylint: disable=no-name-in-module,import-error
    ColorSchemeBuilder, ColorSchemeColorHighlighter)
from ColorHighlighter.regions import NormalizedRegion  # pylint: disable=no-name-in-module,import-error
from ColorHighlighter.settings import (  # pylint: disable=no-name-in-module,import-error
    ColorSchemeColorHighlighterSettings)

from mockito import ANY, captor, mock, verify, when


class ColorSchemeColorHighlighterTest(unittest.TestCase):
    """Tests for ColorSchemeColorHighlighter."""

    test_name = "test-name"

    def test_bad_style(self):
        """Check that bad style failes."""
        with self.assertRaises(AssertionError):
            ColorSchemeColorHighlighter(None, "bad-style", None, self.test_name)

    def test_valid_style_set(self):
        """Test that sets of valid highlighting styles are consistent."""
        self.assertEqual(
            set(ColorSchemeColorHighlighterSettings.ST3_VALID_STYLES),
            set(ColorSchemeColorHighlighter._region_style_flags.keys()))  # pylint: disable=protected-access

    def test_highlight_region(self):  # pylint: disable=no-self-use
        """Test highlight one region."""
        region_a = 10
        region_b = 20
        sublime_region = mock()
        when(sublime).Region(region_a, region_b).thenReturn(sublime_region)
        color = "color"
        region = NormalizedRegion(region_a, region_b)
        color_scheme_builder = mock()
        scope = mock()
        when(color_scheme_builder).get_scopes(ANY, ANY).thenReturn([scope])
        view = mock()
        color_highlighter = ColorSchemeColorHighlighter(view, "filled", color_scheme_builder, self.test_name)
        context = {}
        color_highlighter.highlight_region(context, (region, color))
        color_highlighter.highlight_regions_done(context)
        verify(color_scheme_builder).get_scopes([color], False)
        verify(view).add_regions(
            ColorSchemeColorHighlighter.region_name_template %
            (self.test_name, region.a, region.b), [sublime_region], scope, "", sublime.DRAW_NO_OUTLINE)

    def test_text_highlight(self):  # pylint: disable=no-self-use
        """Test highlight a region with text style."""
        region_a = 10
        region_b = 20
        sublime_region = mock()
        when(sublime).Region(region_a, region_b).thenReturn(sublime_region)
        color = "color"
        region = NormalizedRegion(region_a, region_b)
        color_scheme_builder = mock()
        scope = mock()
        when(color_scheme_builder).get_scopes(ANY, ANY).thenReturn([scope])
        view = mock()
        color_highlighter = ColorSchemeColorHighlighter(view, "text", color_scheme_builder, self.test_name)
        context = {}
        color_highlighter.highlight_region(context, (region, color))
        color_highlighter.highlight_regions_done(context)
        verify(color_scheme_builder).get_scopes([color], True)
        verify(view).add_regions(
            ColorSchemeColorHighlighter.region_name_template %
            (self.test_name, region.a, region.b), [sublime_region], scope, "", sublime.DRAW_NO_OUTLINE)

    def test_highlight_regions(self):  # pylint: disable=no-self-use,too-many-locals
        """Test highlight multiple regions."""
        region1_a = 10
        region1_b = 20
        sublime_region1 = mock()
        when(sublime).Region(region1_a, region1_b).thenReturn(sublime_region1)
        color1 = "color 1"
        region1 = NormalizedRegion(region1_a, region1_b)
        region2_a = 30
        region2_b = 40
        sublime_region2 = mock()
        when(sublime).Region(region2_a, region2_b).thenReturn(sublime_region2)
        color2 = "color 2"
        region2 = NormalizedRegion(region2_a, region2_b)

        color_scheme_builder = mock()
        scope1 = mock()
        scope2 = mock()
        when(color_scheme_builder).get_scopes(ANY, ANY).thenReturn([scope1, scope2])
        view = mock()
        color_highlighter = ColorSchemeColorHighlighter(view, "filled", color_scheme_builder, self.test_name)
        context = {}
        color_highlighter.highlight_region(context, (region1, color1))
        color_highlighter.highlight_region(context, (region2, color2))
        color_highlighter.highlight_regions_done(context)
        verify(color_scheme_builder).get_scopes([color1, color2], False)
        verify(view).add_regions(
            ColorSchemeColorHighlighter.region_name_template %
            (self.test_name, region1.a, region1.b), [sublime_region1], scope1, "", sublime.DRAW_NO_OUTLINE)
        verify(view).add_regions(
            ColorSchemeColorHighlighter.region_name_template %
            (self.test_name, region2.a, region2.b), [sublime_region2], scope2, "", sublime.DRAW_NO_OUTLINE)

    def test_no_regions(self):  # pylint: disable=no-self-use
        """Test highlight zero regions."""
        color_scheme_builder = mock()
        view = mock()
        color_highlighter = ColorSchemeColorHighlighter(view, "filled", color_scheme_builder, self.test_name)
        context = {}
        color_highlighter.highlight_regions_done(context)
        verify(color_scheme_builder, times=0).get_scopes(ANY, ANY)
        verify(view, times=0).add_regions(ANY, ANY, ANY, ANY, ANY)

    def test_unhighlight_region(self):  # pylint: disable=no-self-use
        """Test unhighlight a region."""
        region = NormalizedRegion(10, 20)
        view = mock()
        color_highlighter = ColorSchemeColorHighlighter(view, "filled", None, self.test_name)
        color_highlighter.unhighlight_region(None, (region, None))
        verify(view).erase_regions(
            ColorSchemeColorHighlighter.region_name_template % (self.test_name, region.a, region.b))


class ColorSchemeBuilderTest(unittest.TestCase):
    """Tests for ColorSchemeBuilder."""

    def test_get_scopes(self):
        """Test get_scopes on a new color."""
        background_color = "#FFFFF1FF"
        data = ColorSchemeData(background_color, {})
        color_scheme_writer = mock()
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, False)
        color = "#FFFFFFFF"
        scopes = color_scheme_builder.get_scopes([color], False)
        self.assertEqual(
            [ColorSchemeBuilder._scope_name_template % color[1:]], scopes)  # pylint: disable=protected-access
        scopes = captor()
        verify(color_scheme_writer).add_scopes(scopes)
        self.assertEqual(2, len(scopes.value))
        self.assertEqual(b"""<dict>
<key>name</key>
<string>CH_color</string>
<key>scope</key>
<string>CH_color_FFFFFFFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFFFFF</string>
<key>foreground</key>
<string>#000000FF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[0]))

        self.assertEqual(b"""<dict>
<key>scope</key>
<string>CH_text_color_FFFFFFFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFF2FF</string>
<key>foreground</key>
<string>#FFFFFFFF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[1]))
        self.assertEqual({"#FFFFFFFF": "FFFFFFFF"}, data.existing_colors)

    def test_get_scopes_async(self):
        """Test get_scopes on a new color and update the color scheme in the background ."""
        background_color = "#FFFFF1FF"
        data = ColorSchemeData(background_color, {})
        color_scheme_writer = mock()
        when(sublime).set_timeout_async(ANY, ANY).thenReturn(None)
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, True)
        color = "#FFFFFFFF"
        scopes = color_scheme_builder.get_scopes([color], False)
        self.assertEqual(
            [ColorSchemeBuilder._scope_name_template % color[1:]], scopes)  # pylint: disable=protected-access
        verify(color_scheme_writer, times=0).add_scopes(ANY)
        async_work = captor()
        verify(sublime).set_timeout_async(async_work, ANY)
        async_work.value()
        scopes = captor()
        verify(color_scheme_writer).add_scopes(scopes)
        self.assertEqual(2, len(scopes.value))
        self.assertEqual(b"""<dict>
<key>name</key>
<string>CH_color</string>
<key>scope</key>
<string>CH_color_FFFFFFFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFFFFF</string>
<key>foreground</key>
<string>#000000FF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[0]))

        self.assertEqual(b"""<dict>
<key>scope</key>
<string>CH_text_color_FFFFFFFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFF2FF</string>
<key>foreground</key>
<string>#FFFFFFFF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[1]))
        self.assertEqual({"#FFFFFFFF": "FFFFFFFF"}, data.existing_colors)

    def test_get_scopes_for_background(self):
        """Test get_scopes on a new color that is the same as the background color."""
        background_color = "#FFFFFFFF"
        data = ColorSchemeData(background_color, {})
        color_scheme_writer = mock()
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, False)
        color = "#FFFFFFFF"
        scopes = color_scheme_builder.get_scopes([color], False)
        self.assertEqual(
            [ColorSchemeBuilder._scope_name_template % "FFFFFEFF"], scopes)  # pylint: disable=protected-access
        scopes = captor()
        verify(color_scheme_writer).add_scopes(scopes)
        self.assertEqual(2, len(scopes.value))
        self.assertEqual(b"""<dict>
<key>name</key>
<string>CH_color</string>
<key>scope</key>
<string>CH_color_FFFFFEFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFFEFF</string>
<key>foreground</key>
<string>#000000FF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[0]))

        self.assertEqual(b"""<dict>
<key>scope</key>
<string>CH_text_color_FFFFFEFF</string>
<key>settings</key>
<dict>
<key>background</key>
<string>#FFFFFEFF</string>
<key>foreground</key>
<string>#FFFFFEFF</string>
<key>caret</key>
<string>#000000FF</string>
</dict>
</dict>""", ElementTree.tostring(scopes.value[1]))
        self.assertEqual({"#FFFFFFFF": "FFFFFEFF"}, data.existing_colors)

    def test_get_scopes_existing(self):
        """Test get_scopes on an existing color."""
        background_color = "#FFFFF1FF"
        data = ColorSchemeData(background_color, {"#FFFFFFFF": "FFFFFFFF"})
        color_scheme_writer = mock()
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, False)
        color = "#FFFFFFFF"
        scopes = color_scheme_builder.get_scopes([color], False)
        self.assertEqual(
            [ColorSchemeBuilder._scope_name_template % color[1:]], scopes)  # pylint: disable=protected-access
        verify(color_scheme_writer, times=0).add_scopes(ANY)

    def test_get_scopes_for_text_highlight_style(self):  # pylint: disable=invalid-name
        """Test get_scopes on an existing color for text highlight style."""
        background_color = "#FFFFF1FF"
        data = ColorSchemeData(background_color, {"#FFFFFFFF": "FFFFFFFF"})
        color_scheme_writer = mock()
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, False)
        color = "#FFFFFFFF"
        scopes = color_scheme_builder.get_scopes([color], True)
        self.assertEqual(
            [ColorSchemeBuilder._text_scope_name_template % color[1:]], scopes)  # pylint: disable=protected-access
        verify(color_scheme_writer, times=0).add_scopes(ANY)

    def test_get_scopes_multiple(self):
        """Test get_scopes for several new colors."""
        background_color = "#FFFFF1FF"
        data = ColorSchemeData(background_color, {})
        color_scheme_writer = mock()
        color_scheme_builder = ColorSchemeBuilder(data, color_scheme_writer, False)
        color1 = "#FFFFFFFF"
        color2 = "#000000FF"
        scopes = color_scheme_builder.get_scopes([color1, color2], False)
        self.assertEqual([ColorSchemeBuilder._scope_name_template % color1[1:],  # pylint: disable=protected-access
                          ColorSchemeBuilder._scope_name_template % color2[1:]],  # pylint: disable=protected-access
                         scopes)  # pylint: disable=protected-access
        scopes = captor()
        verify(color_scheme_writer).add_scopes(scopes)
        self.assertEqual(4, len(scopes.value))
