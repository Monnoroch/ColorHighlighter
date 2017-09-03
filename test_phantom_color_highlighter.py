"""Tests for PhantomColorHighlighter."""

try:
    from .st_helper import running_in_st
except ValueError:
    from st_helper import running_in_st


if not running_in_st():

    import unittest
    from mockito import mock, when, verify, ANY

    from . import sublime

    from .phantoms_color_highlighter import PhantomColorHighlighter
    from .regions import NormalizedRegion

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

            PhantomColorHighlighter(view, self.test_name).highlight_region(
                None, (NormalizedRegion(begin, end), test_color))
            verify(view).add_phantom(
                PhantomColorHighlighter.phantom_key_template %
                (self.test_name, begin, end), region, html, sublime.LAYOUT_BELOW, None)

        def test_unhighlight(self):  # pylint: disable=no-self-use
            """Test unhighlighting a region removes the added phantom from the view."""
            view = mock()
            color_highlighter = PhantomColorHighlighter(view, self.test_name)

            begin = 4
            end = 9
            region = mock()
            when(sublime).Region(begin, end).thenReturn(region)

            phantom_id = 95
            when(view).add_phantom(ANY, ANY, ANY, ANY, ANY).thenReturn(phantom_id)

            color_highlighter.unhighlight_region(None, (NormalizedRegion(begin, end), None))
            verify(view).erase_phantoms(PhantomColorHighlighter.phantom_key_template % (self.test_name, begin, end))
