"""Component for listening for selection changes in a view and highlighting selected colors."""

try:
    from . import st_helper
    from .regions import NormalizedRegion, intersects
except ValueError:
    import st_helper
    from regions import NormalizedRegion, intersects


if st_helper.running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


class ColorHoverListener(object):
    """Component for listening for cursor position changes in a view and highlighting colors under the cursor."""

    def __init__(self, color_searcher, view, color_highlighter):
        """
        Init ColorSelectionListener.

        Arguments:
        - color_searcher - a color searcher to search colors with.
        - view - a view to highlight colors in.
        - color_highlighter - a combined color highlighter to highlight colors with.
        """
        self._color_searcher = color_searcher
        self._view = view
        self._color_highlighter = color_highlighter
        self._selection = []
        self._regions = []
        self._point = None

    def on_hover(self, point, hover_zone):
        """
        on_hover event.

        Arguments:
        - point - the position of the cursor.
        - hover_zone - the soze where the cursor is currently.
        """
        if hover_zone != sublime.HOVER_TEXT:
            self._unhighlight()
            return
        self._point = point
        self._update_highlighting()

    def on_modified(self):
        """on_modified event."""
        if _intersects(self._regions, self._selection):
            self._update_highlighting()

    def on_selection_modified(self):
        """on_selection_modified event."""
        new_selection = [NormalizedRegion(region) for region in self._view.sel()]
        if self._selection != new_selection:
            self._selection = new_selection
            self._on_selection_really_modified()

    def _unhighlight(self):
        self._color_highlighter.highlight_regions([])

    def _update_highlighting(self):
        color_regions = self._generate_color_regions(self._point)
        self._color_highlighter.highlight_regions(color_regions)

    def _on_selection_really_modified(self):
        if not _intersects(self._regions, self._selection):
            self._unhighlight()

    def _generate_color_regions(self, point):
        self._regions = []
        region = sublime.Region(point, point)
        normalized_region = NormalizedRegion(region)
        for line in self._view.lines(region):
            for (region, color, _) in self._color_searcher.search(self._view, NormalizedRegion(line)):
                if intersects(region, normalized_region):
                    self._regions.append(region)
                    yield (region, color)


def _intersects(regions1, regions2):
    for region1 in regions1:
        for region2 in regions2:
            if intersects(region1, region2):
                return True
    return False
