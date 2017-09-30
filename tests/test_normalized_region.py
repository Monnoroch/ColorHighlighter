"""Tests for regions.NormalizedRegion."""

import unittest

from ColorHighlighter import sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.regions import NormalizedRegion  # pylint: disable=no-name-in-module,import-error

from mockito import mock, when


class _RegionMock(object):  # pylint: disable=too-few-public-methods
    def __init__(self, a, b):
        self.a = a  # pylint: disable=invalid-name
        self.b = b  # pylint: disable=invalid-name


class NormalizedRegionTest(unittest.TestCase):
    """Tests for NormalizedRegionTest."""

    def test_begin_end(self):
        """Test normal region."""
        a = 10  # pylint: disable=invalid-name
        b = 20  # pylint: disable=invalid-name
        region = NormalizedRegion(a, b)
        self.assertEqual(a, region.a)
        self.assertEqual(b, region.b)
        self.assertEqual(10, region.length())

    def test_begin_end_inversed(self):
        """Test normal region."""
        a = 20  # pylint: disable=invalid-name
        b = 10  # pylint: disable=invalid-name
        region = NormalizedRegion(a, b)
        self.assertEqual(b, region.a)
        self.assertEqual(a, region.b)
        self.assertEqual(10, region.length())

    def test_region(self):
        """Test normal region."""
        a = 10  # pylint: disable=invalid-name
        b = 20  # pylint: disable=invalid-name
        region = NormalizedRegion(_RegionMock(a, b))
        self.assertEqual(a, region.a)
        self.assertEqual(b, region.b)
        self.assertEqual(10, region.length())

    def test_inversed_region(self):
        """Test inversed region."""
        a = 20  # pylint: disable=invalid-name
        b = 10  # pylint: disable=invalid-name
        region = NormalizedRegion(_RegionMock(a, b))
        self.assertEqual(b, region.a)
        self.assertEqual(a, region.b)
        self.assertEqual(10, region.length())

    def test_region_call(self):
        """Test region call."""
        a = 10  # pylint: disable=invalid-name
        b = 20  # pylint: disable=invalid-name
        mock_region = mock()
        region = NormalizedRegion(_RegionMock(a, b))
        when(sublime).Region(a, b).thenReturn(mock_region)
        self.assertEqual(mock_region, region.region())

    def test_equal(self):
        """Test region equals operator."""
        region = NormalizedRegion(10, 20)
        other_region = NormalizedRegion(10, 30)
        self.assertEqual(region, region)
        self.assertNotEqual(region, other_region)

    def test_str(self):
        """Test region string operator."""
        region = NormalizedRegion(10, 20)
        self.assertEqual("(10, 20)", str(region))

    def test_hash(self):
        """Test region hash operator."""
        region = NormalizedRegion(10, 20)
        self.assertEqual(30, hash(region))
