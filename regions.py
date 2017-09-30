"""Helper functions for manipulating regions."""

try:
    from .st_helper import running_in_st
except ValueError:
    from st_helper import running_in_st


if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


class NormalizedRegion(object):
    """
    A convenient wrapper around sublime.Region.

    Regions can have their end smaller than their beginning. This happens, for example, when the user selects from
    right to left. This function normalizes such regions to have their end always before their beginning.
    """

    def __init__(self, a, b=None):
        """
        Initialize a region with a sublime.Region.

        Arguments:
        a -- a sublime.Region to normalize or the regions's beginning.
        b -- the regions's end. Only set if a is the regions's beginning.
        """
        if b is None:
            # a is a sublime.Region.
            b = a.b
            a = a.a
        else:
            a = a
            b = b

        if a > b:
            self.a = b  # pylint: disable=invalid-name
            self.b = a  # pylint: disable=invalid-name
        else:
            self.a = a  # pylint: disable=invalid-name
            self.b = b  # pylint: disable=invalid-name

    def length(self):
        """Get the normalizer region's length."""
        return self.b - self.a

    def region(self):
        """Return a sublime.Region for this normalized region."""
        return sublime.Region(self.a, self.b)

    def __eq__(self, other):
        """Compare normalized regions for equality."""
        if not isinstance(other, NormalizedRegion):
            return False
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        """Get the normalized regions hash."""
        return hash(self.a) ^ hash(self.b)

    def __str__(self):
        """Get the normalided regions string representation."""
        return "(%d, %d)" % (self.a, self.b)

    def __repr__(self):
        """Get the normalided regions string representation."""
        return self.__str__()


def intersects(region1, region2):
    """
    Check if two regions intersect.

    If regions share an end, they don't intersect unless one of the regions has zero length in which case they do
    intersect.

    Arguments:
    region1 -- a first region.
    region2 -- a second region.
    Returns True if regions intersect and False otherwise.
    """
    if region1.a == region1.b:
        return region2.a <= region1.a and region2.b >= region1.b
    if region2.a == region2.b:
        return region1.a <= region2.a and region1.b >= region2.b
    if region1.a >= region2.b:
        return False
    if region1.b <= region2.a:
        return False
    return True


def intersects_any(input_region, regions):
    """
    Check a region intersects with any of the other regions.

    If regions share an end, they don't intersect unless one of the regions has zero length in which case they do
    intersect.

    Arguments:
    input_region -- a region to check.
    regions -- a list of regions.
    Returns True if the first region intersects with any of the other regions and False otherwise.
    """
    for region in regions:
        if intersects(input_region, region):
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
    return processed_regions.keys()
