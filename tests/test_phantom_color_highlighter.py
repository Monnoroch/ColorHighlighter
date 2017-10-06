"""Tests for PhantomColorHighlighter."""

import unittest

from ColorHighlighter import sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.phantoms_color_highlighter import (  # pylint: disable=no-name-in-module,import-error
    PhantomColorHighlighter)
from ColorHighlighter.regions import NormalizedRegion  # pylint: disable=no-name-in-module,import-error

from mockito import ANY, mock, verify, when


class PhantomColorHighlighterTest(unittest.TestCase):
    """Tests for PhantomColorHighlighter."""

    test_name = "test-name"

    def test_highlight(self):  # pylint: disable=no-self-use
        """Test highlighting a region adds a phantom to the view."""
        view = mock()

        test_color = "test"
        begin = 4
        end = begin + len(test_color)
        region = mock()
        when(sublime).Region(begin, end).thenReturn(region)

        html = '''
<body>
    <style>
        * {
            background-color: test;
        }
    </style>
    &nbsp;&nbsp;&nbsp;&nbsp;
</body>
'''
        phantom_id = 95
        when(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_BELOW, None).thenReturn(phantom_id)

        PhantomColorHighlighter(view, self.test_name, "below", 10, False).highlight_region(
            None, (NormalizedRegion(begin, end), test_color))
        verify(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_BELOW, None)

    def test_highlight_right(self):  # pylint: disable=no-self-use
        """Test highlighting a region adds a phantom to the right of the color to the view."""
        view = mock()

        test_color = "test"
        begin = 4
        end = begin + len(test_color)
        region = mock()
        when(sublime).Region(end, end).thenReturn(region)

        html = '''
<body>
    <style>
        * {
            background-color: test;
        }
    </style>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</body>
'''
        phantom_id = 95
        when(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_INLINE, None).thenReturn(phantom_id)

        PhantomColorHighlighter(view, self.test_name, "right", 5, False).highlight_region(
            None, (NormalizedRegion(begin, end), test_color))
        verify(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_INLINE, None)

    def test_highlight_left(self):  # pylint: disable=no-self-use
        """Test highlighting a region adds a phantom to the left of the color to the view."""
        view = mock()

        test_color = "test"
        begin = 4
        end = begin + len(test_color)
        region = mock()
        when(sublime).Region(begin, begin).thenReturn(region)

        html = '''
<body>
    <style>
        * {
            background-color: test;
        }
    </style>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</body>
'''
        phantom_id = 95
        when(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_INLINE, None).thenReturn(phantom_id)

        PhantomColorHighlighter(view, self.test_name, "left", 5, False).highlight_region(
            None, (NormalizedRegion(begin, end), test_color))
        verify(view).add_phantom(
            PhantomColorHighlighter.phantom_key_template %
            (self.test_name, begin, end), region, html, sublime.LAYOUT_INLINE, None)

    def test_unhighlight(self):  # pylint: disable=no-self-use
        """Test unhighlighting a region removes the added phantom from the view."""
        view = mock()
        color_highlighter = PhantomColorHighlighter(view, self.test_name, "below", 1, False)

        begin = 4
        end = 9
        region = mock()
        when(sublime).Region(begin, end).thenReturn(region)

        phantom_id = 95
        when(view).add_phantom(ANY, ANY, ANY, ANY, ANY).thenReturn(phantom_id)

        color_highlighter.unhighlight_region(None, (NormalizedRegion(begin, end), None))
        verify(view).erase_phantoms(PhantomColorHighlighter.phantom_key_template % (self.test_name, begin, end))
