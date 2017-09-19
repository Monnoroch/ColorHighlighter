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

    def on_hover(self, point, hover_zone):
        """
        on_hover event.

        Arguments:
        - point - the position of the cursor.
        - hover_zone - the soze where the cursor is currently.
        """
        if hover_zone != sublime.HOVER_TEXT:
            self._color_highlighter.highlight_regions([])
            return
        color_regions = _drop_match(self._generate_color_regions(point))
        self._color_highlighter.highlight_regions(color_regions)

    def _generate_color_regions(self, point):
        region = sublime.Region(point, point)
        normalized_region = NormalizedRegion(region)
        for line in self._view.lines(region):
            for color_data in self._color_searcher.search(self._view, NormalizedRegion(line)):
                if intersects(color_data[0], normalized_region):
                    yield color_data


def _drop_match(values):
    for value in values:
        yield (value[0], value[1])
