"""Tests for color_searcher.ColorSearcher."""

import re
import unittest

from ColorHighlighter import sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.color_searcher import ColorSearcher  # pylint: disable=no-name-in-module,import-error
from ColorHighlighter.regions import NormalizedRegion  # pylint: disable=no-name-in-module,import-error

from mockito import ANY, mock, when


class ColorSearcherTest(unittest.TestCase):
    """Tests for ColorSearcher."""

    def test_search_found(self):
        """Test found color."""
        begin = 5
        end = 10
        region = NormalizedRegion(begin, end)
        whole_region = mock()
        when(sublime).Region(begin, end).thenReturn(whole_region)
        color_region = mock()
        when(sublime).Region(begin + 1, end - 1).thenReturn(color_region)
        view = mock()
        test_color_text = "#FA"
        when(view).substr(whole_region).thenReturn(" %s " % test_color_text)
        when(view).substr(color_region).thenReturn(test_color_text)
        test_color = "#FB"
        test_group = "test_group"
        color_converter = mock()
        when(color_converter).to_color({test_group: test_color_text}).thenReturn(test_color)
        color_searcher = ColorSearcher(re.compile("(?P<%s>#[0-9a-fA-F]{2})" % test_group), color_converter)

        results = [result for result in color_searcher.search(view, region)]
        self.assertEqual(
            [(NormalizedRegion(begin + 1, end - 1), test_color, {test_group: test_color_text})], results)

    def test_search_found_bad(self):
        """Test found color which could not be converted to a canonical form."""
        begin = 5
        end = 10
        region = NormalizedRegion(begin, end)
        whole_region = mock()
        when(sublime).Region(begin, end).thenReturn(whole_region)
        color_region = mock()
        when(sublime).Region(begin + 1, end - 1).thenReturn(color_region)
        view = mock()
        test_color_text = "#FA"
        when(view).substr(whole_region).thenReturn(" %s " % test_color_text)
        when(view).substr(color_region).thenReturn(test_color_text)
        color_searcher = ColorSearcher(re.compile("#[0-9a-fA-F]{2}"), mock())

        results = [result for result in color_searcher.search(view, region)]
        self.assertEqual([], results)

    def test_search_found_multiple(self):  # pylint: disable=too-many-locals
        """Test found multiple colors."""
        begin = 5
        end = 15
        region = NormalizedRegion(begin, end)
        whole_region = mock()
        when(sublime).Region(begin, end).thenReturn(whole_region)
        color_region1 = mock()
        when(sublime).Region(begin + 1, begin + 4).thenReturn(color_region1)
        color_region2 = mock()
        when(sublime).Region(end - 4, end - 1).thenReturn(color_region2)
        view = mock()
        test_color_text1 = "#FA"
        test_color_text2 = "#E5"
        when(view).substr(whole_region).thenReturn(" %s  %s " % (test_color_text1, test_color_text2))
        when(view).substr(color_region1).thenReturn(test_color_text1)
        when(view).substr(color_region2).thenReturn(test_color_text2)
        test_color1 = "#FB"
        test_color2 = "#DB"
        test_group = "test_group"
        color_converter = mock()
        when(color_converter).to_color({test_group: test_color_text1}).thenReturn(test_color1)
        when(color_converter).to_color({test_group: test_color_text2}).thenReturn(test_color2)
        color_searcher = ColorSearcher(re.compile("(?P<%s>#[0-9a-fA-F]{2})" % test_group), color_converter)

        results = [result for result in color_searcher.search(view, region)]
        self.assertEqual(
            [(NormalizedRegion(begin + 1, begin + 4), test_color1, {test_group: test_color_text1}),
             (NormalizedRegion(end - 4, end - 1), test_color2, {test_group: test_color_text2})], results)

    def test_search_not_found(self):
        """Test search."""
        begin = 5
        end = 10
        region = NormalizedRegion(begin, end)
        whole_region = mock()
        when(sublime).Region(begin, end).thenReturn(whole_region)
        view = mock()
        when(view).substr(ANY).thenReturn(" " * 30)

        color_searcher = ColorSearcher(re.compile("#[0-9a-fA-F]{2}"), mock())

        results = [result for result in color_searcher.search(view, region)]
        self.assertEqual([], results)
