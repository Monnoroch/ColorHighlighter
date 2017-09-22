"""Tests for regions.NormalizedRegion."""

import unittest

from ColorHighlighter.regions import (  # pylint: disable=no-name-in-module,import-error
    NormalizedRegion, deduplicate_regions, intersects, intersects_any)


class IntersectTest(unittest.TestCase):
    """Tests for intersects."""

    def test_intersects(self):
        """Test all cases."""
        region = NormalizedRegion(4, 7)
        self.assertFalse(intersects(NormalizedRegion(1, 3), region))
        self.assertFalse(intersects(NormalizedRegion(2, 4), region))
        self.assertTrue(intersects(NormalizedRegion(4, 4), region))
        self.assertTrue(intersects(NormalizedRegion(3, 5), region))
        self.assertTrue(intersects(NormalizedRegion(4, 7), region))
        self.assertTrue(intersects(NormalizedRegion(5, 8), region))
        self.assertTrue(intersects(NormalizedRegion(7, 7), region))
        self.assertFalse(intersects(NormalizedRegion(7, 9), region))
        self.assertFalse(intersects(NormalizedRegion(8, 10), region))


class IntersectAnyTest(unittest.TestCase):
    """Tests for intersects_any."""

    def test_intersects_any(self):
        """Test all cases."""
        region = NormalizedRegion(4, 7)
        self.assertFalse(intersects_any(region, [NormalizedRegion(1, 3)]))
        self.assertFalse(intersects_any(region, [NormalizedRegion(1, 3), NormalizedRegion(0, 1)]))
        self.assertTrue(intersects_any(region, [NormalizedRegion(3, 5)]))
        self.assertTrue(intersects_any(region, [NormalizedRegion(3, 5), NormalizedRegion(5, 6)]))
        self.assertTrue(intersects_any(region, [NormalizedRegion(3, 5), NormalizedRegion(1, 3)]))


class DeduplicateRegionsTest(unittest.TestCase):
    """Tests for deduplicate_regions."""

    def test_deduplicate(self):
        """Test deduplicating regions."""
        region1 = 1
        region2 = 2
        regions = [region1, region2, region1]
        output = [value for value in deduplicate_regions(regions)]
        self.assertEqual([region1, region2], output)
