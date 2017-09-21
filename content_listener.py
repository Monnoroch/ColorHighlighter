"""Component for listening for loaded views and highlighting colors in them."""

try:
    from .regions import NormalizedRegion, deduplicate_regions
except ValueError:
    from regions import NormalizedRegion, deduplicate_regions


class ContentListener(object):
    """Component for listening for loaded views and highlighting colors in them."""

    def __init__(self, color_searcher, view, color_highlighter):
        """
        Init ContentListener.

        Arguments:
        - color_searcher - a color searcher to search colors with.
        - view - a view to highlight colors in.
        - color_highlighter - a combined color highlighter to highlight colors with.
        """
        self._color_searcher = color_searcher
        self._view = view
        self._color_highlighter = color_highlighter

    def on_load(self):
        """Call when view's content is loaded."""
        color_regions = self._generate_color_regions()
        self._color_highlighter.highlight_regions(color_regions)

    def on_modified(self):
        """on_modified event."""
        lines = deduplicate_regions(self._generate_lines_for_selection())
        color_regions = self._generate_color_regions_for_selection(lines)
        self._color_highlighter.highlight_regions_in(color_regions, lines)

    def _generate_color_regions(self):
        for line in self._generate_lines():
            for (region, color, _) in self._color_searcher.search(self._view, line):
                yield (region, color)

    def _generate_lines(self):
        for line in self._view.lines(NormalizedRegion(0, self._view.size()).region()):
            yield NormalizedRegion(line)

    def _generate_color_regions_for_selection(self, lines):
        for line in lines:
            for (region, color, _) in self._color_searcher.search(self._view, line):
                yield (region, color)

    def _generate_lines_for_selection(self):
        for region in self._view.sel():
            for line in self._view.lines(region):
                yield NormalizedRegion(line)
