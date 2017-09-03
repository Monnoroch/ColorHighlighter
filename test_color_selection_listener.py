"""Tests for color_searcher.ColorSearcher."""

try:
    from .st_helper import running_in_st
except ValueError:
    from st_helper import running_in_st


if not running_in_st():

    import unittest
    from mockito import mock, when, verify, ANY
    from mockito.matchers import captor

    from .regions import NormalizedRegion
    from .color_selection_listener import ColorSelectionListener, deduplicate_regions

    class ColorSelectionListenerTest(unittest.TestCase):
        """Tests for ColorSelectionListener."""

        def test_selection_changed(self):
            """Test modify selection."""
            color_searcher = mock()
            view = mock()
            color_highlighter = mock()
            color_selection_listener = ColorSelectionListener(color_searcher, view, color_highlighter)

            color_region1 = (NormalizedRegion(10, 11), 1)
            color_region2 = (NormalizedRegion(11, 12), 2)
            color_region3 = (NormalizedRegion(17, 21), 3)

            sel_region1 = NormalizedRegion(10, 13)
            sel_region2 = NormalizedRegion(16, 20)
            sel_line1 = NormalizedRegion(14, 15)
            sel_line2 = NormalizedRegion(16, 17)
            when(view).lines(sel_region1).thenReturn([sel_line1])
            when(view).lines(sel_region2).thenReturn([sel_line2])
            when(view).sel().thenReturn([sel_region1, sel_region2])
            when(color_searcher).search(view, sel_line1).thenReturn([color_region1, color_region2])
            when(color_searcher).search(view, sel_line2).thenReturn([color_region3])
            color_selection_listener.on_selection_modified()
            color_regions = captor()
            verify(color_highlighter).highlight_regions(color_regions)
            self.assertEqual([color_region1, color_region2, color_region3], [region for region in color_regions.value])

        def test_selection_unchanged(self):  # pylint: disable=no-self-use
            """Test modify selection without it actually changing."""
            color_searcher = mock()
            view = mock()
            color_highlighter = mock()
            color_selection_listener = ColorSelectionListener(color_searcher, view, color_highlighter)

            when(view).sel().thenReturn([])

            color_selection_listener.on_selection_modified()
            color_selection_listener.on_selection_modified()
            verify(color_highlighter, times=1).highlight_regions(ANY)

        def test_selection_no_intersections(self):
            """Test modify selection with color searher returning regions with no intersections with the selection."""
            color_searcher = mock()
            view = mock()
            color_highlighter = mock()
            color_selection_listener = ColorSelectionListener(color_searcher, view, color_highlighter)

            color_region = (NormalizedRegion(4, 5), 1)

            sel_region = NormalizedRegion(10, 13)
            sel_line = NormalizedRegion(14, 15)
            when(view).lines(sel_region).thenReturn([sel_line])
            when(view).sel().thenReturn([sel_region])
            when(color_searcher).search(view, sel_line).thenReturn([color_region])
            color_selection_listener.on_selection_modified()
            color_regions = captor()
            verify(color_highlighter).highlight_regions(color_regions)
            self.assertEqual([], [region for region in color_regions.value])

        def test_deduplicate_lines(self):
            """Test that having two selections on the same line yields that line only one time ."""
            color_searcher = mock()
            view = mock()
            color_highlighter = mock()
            color_selection_listener = ColorSelectionListener(color_searcher, view, color_highlighter)

            color_region = (NormalizedRegion(11, 14), 1)

            sel_region1 = NormalizedRegion(10, 11)
            sel_region2 = NormalizedRegion(12, 13)
            sel_line = NormalizedRegion(14, 15)
            when(view).lines(sel_region1).thenReturn([sel_line])
            when(view).lines(sel_region2).thenReturn([sel_line])
            when(view).sel().thenReturn([sel_region1, sel_region2])
            when(color_searcher).search(view, sel_line).thenReturn([color_region])
            color_selection_listener.on_selection_modified()
            color_regions = captor()
            verify(color_highlighter).highlight_regions(color_regions)
            self.assertEqual([color_region], [region for region in color_regions.value])

    class DeduplicateRegionsTest(unittest.TestCase):
        """Tests for deduplicate_regions."""

        def test_deduplicate(self):
            """Test deduplicating regions."""
            region1 = 1
            region2 = 2
            regions = [region1, region2, region1]
            output = [value for value in deduplicate_regions(regions)]
            self.assertEqual([region1, region2], output)
