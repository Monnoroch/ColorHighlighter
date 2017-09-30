"""The module with tools for searching for colors in ST views."""

try:
    from . import regions
except ValueError:
    import regions


class ColorSearcher(object):
    """Class for searching for colors in ST views."""

    def __init__(self, regex, color_converter):
        """
        Init a ColorSearcher.

        Arguments:
        - regex - the regex for matching colors.
        - color_converter - the color converter to convert color text into cannical form.
        """
        self._color_regex = regex
        self._color_converter = color_converter

    def search(self, view, region):
        """
        Get a region with a color in the view.

        Given a region, yield regions inside of it that contain colors.
        Arguments:
        - view - the view to look in.
        - region - the initial region to look around.
        Yields tuples of of NormalizedRegion-s, canonical colors that are in this regions and color matches for them.
        """
        region_text = view.substr(region.region())
        match = self._color_regex.search(region_text)
        while match:
            start = match.start()
            end = match.end()
            color_region = regions.NormalizedRegion(region.a + start, region.a + end)
            groups = match.groupdict()
            color = self._color_converter.to_color(groups)
            if color is not None:
                yield color_region, color, groups
            match = self._color_regex.search(region_text, end)
