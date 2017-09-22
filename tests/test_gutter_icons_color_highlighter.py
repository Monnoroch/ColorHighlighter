"""Tests for GutterIconsColorHighlighter."""

import unittest

from ColorHighlighter import sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.gutter_icons_color_highlighter import (  # pylint: disable=no-name-in-module,import-error
    GutterIconsColorHighlighter)
from ColorHighlighter.regions import NormalizedRegion  # pylint: disable=no-name-in-module,import-error

from mockito import mock, verify, when


class GutterIconsColorHighlighterTest(unittest.TestCase):
    """Tests for PhantomColorHighlighter."""

    test_name = "test-name"

    def test_highlight(self):  # pylint: disable=no-self-use
        """Check highlighting a region."""
        view = mock()
        icon_factory = mock()
        test_style = "circle"
        color_highlighter = GutterIconsColorHighlighter(view, test_style, icon_factory, self.test_name)

        test_color = "test"
        begin = 4
        end = begin + len(test_color)
        normalized_region = NormalizedRegion(begin, end)
        region = mock()
        when(sublime).Region(begin, end).thenReturn(region)

        test_path = "test/path"
        when(icon_factory).get_icon_path(test_style, test_color).thenReturn(test_path)

        color_highlighter.highlight_region(None, (normalized_region, test_color))
        verify(view).add_regions(
            GutterIconsColorHighlighter.region_name_template %
            (self.test_name, normalized_region.a, normalized_region.b),
            [region], GutterIconsColorHighlighter.region_scope, test_path, sublime.HIDDEN)

    def test_unhighlight(self):  # pylint: disable=no-self-use
        """Check unhighlighting a region."""
        view = mock()
        color_highlighter = GutterIconsColorHighlighter(view, "circle", mock(), self.test_name)
        normalized_region = NormalizedRegion(4, 9)

        color_highlighter.unhighlight_region(None, (normalized_region, None))
        verify(view).erase_regions(
            GutterIconsColorHighlighter.region_name_template %
            (self.test_name, normalized_region.a, normalized_region.b))
