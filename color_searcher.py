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

        Given a region, return another region with the color text that contains the initial region or None, if the
        original region is not in the color text.
        Arguments:
        - view - the view to look in.
        - region - the initial region to look around.
        Yields pairs of NormalizedRegion-s and a colors that are in this region.
        """
        region_text = view.substr(region.region())
        match = self._color_regex.search(region_text)
        while match:
            start = match.start()
            end = match.end()
            color_region = regions.NormalizedRegion(region.a + start, region.a + end)
            color = self._color_converter.to_color(match.groupdict())
            if color is not None:
                yield color_region, color
            match = self._color_regex.search(region_text, end)
