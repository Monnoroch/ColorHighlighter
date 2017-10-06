"""A base class for all color highlighters."""

try:
    from .regions import intersects_any
except ValueError:
    from regions import intersects_any


class ColorHighlighter(object):
    """A base class for all color highlighters."""

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        raise NotImplementedError

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        raise NotImplementedError

    def highlight_regions_done(self, context):  # noqa: D401
        """
        Called after all calls to highlight_region and unhighlight_region from highlight_regions have been made.

        Arguments:
        - context - a dict with color highlighter run data.
        """
        pass


class CombinedColorHighlighter(ColorHighlighter):
    """A color highlighter that forwards calls to a list of base color highlighters."""

    def __init__(self, color_highlighters):
        """
        Create a combined color highlighter.

        Arguments:
        - color_highlighters - a list of color highlighters.
        """
        self._color_highlighters = color_highlighters

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        for index, color_highlighter in enumerate(self._color_highlighters):
            color_highlighter.highlight_region(context[index], value)

    def highlight_regions_done(self, context):  # noqa: D401
        """
        Called after all calls to highlight_region and unhighlight_region from highlight_regions have been made.

        Arguments:
        - context - a dict with color highlighter run data.
        """
        for index, color_highlighter in enumerate(self._color_highlighters):
            color_highlighter.highlight_regions_done(context[index])

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        for index, color_highlighter in enumerate(self._color_highlighters):
            color_highlighter.unhighlight_region(context[index], value)

    def make_context(self):
        """Get a list of contexts for a list of color highlighters in this combined color highlighter."""
        contexts = []
        for _ in self._color_highlighters:
            contexts.append({})
        return contexts


class CachingColorHighlighter(CombinedColorHighlighter):  # pylint: disable=abstract-method
    """
    A caching color highlighter.

    It remembers currently highlighted regions and only rerenders those that are new and deletes those that are not
    highlighted any more.
    """

    def __init__(self, color_highlighters):
        """
        Create a caching color highlighter.

        Arguments:
        - color_highlighters - a list of color highlighters.
        """
        super(CachingColorHighlighter, self).__init__(color_highlighters)
        self._existing_regions = {}

    def highlight_regions(self, regions):
        """
        Highlight regions.

        Arguments:
        - regions - an iterable of tuples (region to highlight, it's color).
        """
        for region in self._existing_regions:
            self._existing_regions[region].need_delete = True
        self._highlight_regions(regions)

    def highlight_regions_in(self, regions, regions_in):
        """
        Highlight regions that lay within specified regions.

        Arguments:
        - regions - an iterable of tuples (region to highlight, it's color).
        - regions_in - an iterable of regions wherr highlightings need to be updated.
        """
        for region in self._existing_regions:
            if intersects_any(region, regions_in):
                self._existing_regions[region].need_delete = True
        self._highlight_regions(regions)

    def _highlight_regions(self, regions):
        regions_to_highlight = []
        changed_color = []
        for value in regions:
            region = value[0]
            color = value[1]
            if region in self._existing_regions:
                region_data = self._existing_regions[region]
                if region_data.color == color:
                    region_data.need_delete = False
                    continue
                else:
                    changed_color.append((region, region_data.color))

            regions_to_highlight.append(value)
            self._existing_regions[region] = _RegionData(color)

        context = self.make_context()

        regions_to_delete = []
        for region in self._existing_regions:
            region_data = self._existing_regions[region]
            if region_data.need_delete:
                self.unhighlight_region(context, (region, region_data.color))
                regions_to_delete.append(region)
        for value in changed_color:
            self.unhighlight_region(context, value)
        for region in regions_to_delete:
            del self._existing_regions[region]
        for value in regions_to_highlight:
            self.highlight_region(context, value)
        self.highlight_regions_done(context)

    def clear_all(self):
        """Unhighlight all regions."""
        context = self.make_context()
        for region in self._existing_regions:
            self.unhighlight_region(context, (region, self._existing_regions[region].color))
        self._existing_regions = {}
        self.highlight_regions_done(context)


class _RegionData(object):  # pylint: disable=too-few-public-methods
    def __init__(self, color):
        self.color = color
        self.need_delete = False
