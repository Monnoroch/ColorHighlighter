"""Component for listening for selection changes in a view and highlighting selected colors."""

try:
    from .regions import NormalizedRegion, intersects
except ValueError:
    from regions import NormalizedRegion, intersects


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
        self._selection = None

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

    def _on_selection_really_modified(self):
        color_regions = self._generate_color_regions(self._selection)
        self._color_highlighter.highlight_regions(color_regions)

    def _generate_color_regions(self, regions):
        normalized_regions = [NormalizedRegion(region) for region in regions]
        for line in deduplicate_regions(self._generate_lines(regions)):
            for color_region in self._color_searcher.search(self._view, line):
                if _intersects_any(color_region, normalized_regions):
                    yield color_region

    def _generate_lines(self, regions):
        for region in regions:
            for line in self._view.lines(region):
                yield NormalizedRegion(line)


def _intersects_any(color_region, regions):
    (value, _) = color_region
    for region in regions:
        if intersects(value, region):
            return True
    return False


def deduplicate_regions(regions):
    """
    Deduplicate regions.

    Argumens:
    - regions - an iterable of pairs (region, color).
    Returns an iterable of (region, color) with unique regions.
    """
    processed_regions = {}
    for region in regions:
        if region in processed_regions:
            continue
        processed_regions[region] = True
        yield region
