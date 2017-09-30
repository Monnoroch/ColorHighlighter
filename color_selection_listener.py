"""Component for listening for selection changes in a view and highlighting selected colors."""

try:
    from .regions import NormalizedRegion, intersects_any, deduplicate_regions
except ValueError:
    from regions import NormalizedRegion, intersects_any, deduplicate_regions


class ColorSelectionListener(object):
    """Component for listening for selection changes in a view and highlighting selected colors."""

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

    def on_selection_modified(self):
        """
        Call when view's selection was modified.

        Because ST sometimes call EventListener.on_selection_modified even when the selection didn't change, this class
        also handles such cases by ignoring them.
        """
        new_selection = [region for region in self._view.sel()]
        if self._selection != new_selection:
            self._selection = new_selection
            self._on_selection_really_modified()

    def on_modified(self):
        """on_modified event."""
        self._on_selection_really_modified()

    def _on_selection_really_modified(self):
        color_regions = _drop_match(_generate_color_regions(self._view, self._color_searcher, self._selection))
        self._color_highlighter.highlight_regions(color_regions)


def search_colors_in_selection(view, color_searcher):
    """
    Search colors in selection.

    Arguments:
    - view - the view to search colors in.
    - color_searcher - the color searcher to search colors with.
    """
    return _generate_color_regions(view, color_searcher, view.sel())


def _drop_match(values):
    for value in values:
        yield (value[0], value[1])


def _generate_color_regions(view, color_searcher, regions):
    normalized_regions = [NormalizedRegion(region) for region in regions]
    for line in deduplicate_regions(_generate_lines(view, regions)):
        for color_data in color_searcher.search(view, line):
            if intersects_any(color_data[0], normalized_regions):
                yield color_data


def _generate_lines(view, regions):
    for region in regions:
        for line in view.lines(region):
            yield NormalizedRegion(line)
