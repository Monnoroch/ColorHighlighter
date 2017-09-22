"""Tests for color_highlighter module."""

import unittest

from ColorHighlighter.color_highlighter import (  # pylint: disable=no-name-in-module,import-error
    CachingColorHighlighter, CombinedColorHighlighter)

from mockito import ANY, mock, verify


class CombinedColorHighlighterTest(unittest.TestCase):
    """Tests for CombinedColorHighlighter."""

    color_highlighter1 = mock()
    color_highlighter2 = mock()
    context1 = 1
    context2 = 2
    contexts = [context1, context2]
    combined_color_highlighter = CombinedColorHighlighter([color_highlighter1, color_highlighter2])

    def test_highlight(self):
        """Test that highlight_regions calls are forwarded to base color highlighters."""
        test_region = 1
        self.combined_color_highlighter.highlight_region(self.contexts, test_region)
        verify(self.color_highlighter1).highlight_region(self.context1, test_region)
        verify(self.color_highlighter2).highlight_region(self.context2, test_region)

    def test_unhighlight(self):
        """Test that unhighlight_regions calls are forwarded to base color highlighters."""
        test_region = 1
        self.combined_color_highlighter.unhighlight_region(self.contexts, test_region)
        verify(self.color_highlighter1).unhighlight_region(self.context1, test_region)
        verify(self.color_highlighter2).unhighlight_region(self.context2, test_region)

    def test_highlight_done(self):
        """Test that highlight_regions_done calls are forwarded to base color highlighters."""
        self.combined_color_highlighter.highlight_regions_done(self.contexts)
        verify(self.color_highlighter1).highlight_regions_done(self.context1)
        verify(self.color_highlighter2).highlight_regions_done(self.context2)


class _TestColorHighlighter(CachingColorHighlighter):
    def __init__(self, object_mock):
        super(_TestColorHighlighter, self).__init__([])
        self.object_mock = object_mock

    def highlight_region(self, context, value):  # pylint: disable=missing-docstring
        return self.object_mock.highlight_region(context, value)

    def highlight_regions_done(self, context):  # pylint: disable=missing-docstring
        return self.object_mock.highlight_regions_done(context)

    def unhighlight_region(self, context, value):  # pylint: disable=missing-docstring
        return self.object_mock.unhighlight_region(context, value)

    def make_context(self):  # pylint: disable=missing-docstring,no-self-use
        return [{}]


class CachingColorHighlighterTest(unittest.TestCase):
    """Tests for CachingColorHighlighter."""

    def test_highlight(self):  # pylint: disable=no-self-use
        """Test that highlight_region is called for every new region."""
        mock_color_highlighter = mock()
        color_highlighter = _TestColorHighlighter(mock_color_highlighter)
        region1 = (1, 2)
        region2 = (3, 4)
        color_highlighter.highlight_regions([region1, region2])
        verify(mock_color_highlighter).highlight_region(ANY, region1)
        verify(mock_color_highlighter).highlight_region(ANY, region2)
        verify(mock_color_highlighter).highlight_regions_done(ANY)

    def test_cache_regions(self):  # pylint: disable=no-self-use
        """Test that highlight_region is not called for existing regions."""
        mock_color_highlighter = mock()
        color_highlighter = _TestColorHighlighter(mock_color_highlighter)
        region = (1, 2)
        color_highlighter.highlight_regions([region])
        verify(mock_color_highlighter).highlight_region(ANY, region)
        verify(mock_color_highlighter).highlight_regions_done(ANY)
        color_highlighter.highlight_regions([region])
        verify(mock_color_highlighter, times=1).highlight_region(ANY, region)
        verify(mock_color_highlighter, times=2).highlight_regions_done(ANY)

    def test_update_color(self):  # pylint: disable=no-self-use
        """Test that highlight_region is called for existing regions with updated color."""
        mock_color_highlighter = mock()
        color_highlighter = _TestColorHighlighter(mock_color_highlighter)
        region1 = (1, 2)
        region2 = (1, 3)
        color_highlighter.highlight_regions([region1])
        verify(mock_color_highlighter).highlight_region(ANY, region1)
        verify(mock_color_highlighter).highlight_regions_done(ANY)
        color_highlighter.highlight_regions([region2])
        verify(mock_color_highlighter, times=1).unhighlight_region(ANY, region1)
        verify(mock_color_highlighter, times=1).highlight_region(ANY, region2)
        verify(mock_color_highlighter, times=2).highlight_regions_done(ANY)

    def test_erase_regions(self):  # pylint: disable=no-self-use
        """Test that unhighlight_region is called for all regions that were highlighted, but not any more."""
        mock_color_highlighter = mock()
        color_highlighter = _TestColorHighlighter(mock_color_highlighter)
        region = (1, 2)
        color_highlighter.highlight_regions([region])
        verify(mock_color_highlighter).highlight_region(ANY, region)
        verify(mock_color_highlighter).highlight_regions_done(ANY)
        color_highlighter.highlight_regions([])
        verify(mock_color_highlighter, times=1).highlight_region(ANY, region)
        verify(mock_color_highlighter).unhighlight_region(ANY, region)
        verify(mock_color_highlighter, times=2).highlight_regions_done(ANY)

    def test_clear_all(self):  # pylint: disable=no-self-use
        """Test that unhighlight_region is called for every highlighted region."""
        mock_color_highlighter = mock()
        color_highlighter = _TestColorHighlighter(mock_color_highlighter)
        region = (1, 2)
        color_highlighter.highlight_regions([region])
        color_highlighter.clear_all()
        verify(mock_color_highlighter).unhighlight_region(ANY, region)
        verify(mock_color_highlighter, times=2).highlight_regions_done(ANY)
