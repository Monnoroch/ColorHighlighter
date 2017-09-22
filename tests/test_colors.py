"""Tests for colors module."""

import unittest

from ColorHighlighter import colors  # pylint: disable=no-name-in-module


class NormalizeHexColorTest(unittest.TestCase):
    """Tests for normalize_hex_color."""

    def test_noop(self):
        """Normalizing a normalized color is a noop."""
        test_color = "#FFFFFFFF"
        self.assertEqual(test_color, colors.normalize_hex_color(test_color))

    def test_normalize(self):
        """Normalize color."""
        self.assertEqual("#FFFFFFFF", colors.normalize_hex_color("#FFFF"))


class BackgroundColorForTextWorkaroundTest(unittest.TestCase):
    """Tests for background_color_for_text_workaround."""

    def test_noop(self):
        """Normalizing a non-background color is a noop."""
        test_color = "#FFFFFFFF"
        self.assertEqual(test_color, colors.background_color_for_text_workaround(test_color, test_color + "F"))

    def test_normalize_f(self):
        """Normalize color with F in the second green channel half-byte."""
        test_color = "#FFFFFFFF"
        self.assertEqual("#FFFFFEFF", colors.background_color_for_text_workaround(test_color, test_color))

    def test_normalize(self):
        """Normalize color with something other than F in the second green channel half-byte."""
        test_color = "#FFFFF1FF"
        self.assertEqual("#FFFFF2FF", colors.background_color_for_text_workaround(test_color, test_color))


class RgbToHexTest(unittest.TestCase):
    """Tests for rgb_to_hex."""

    def test_convert(self):
        """Convert r, g, b to #RRGGBBAA."""
        self.assertEqual("#FFFFFFFF", colors.rgb_to_hex(255, 255, 255))


class ComplementaryColorTest(unittest.TestCase):
    """Tests for complementary_color."""

    def test_convert(self):
        """Convert r, g, b to #RRGGBBAA."""
        self.assertEqual("#FFFFFFFF", colors.complementary_color("#000000FF"))

    def test_ignore_alpha(self):
        """Convert r, g, b to #RRGGBBAA."""
        self.assertEqual("#FFFFFFFF", colors.complementary_color("#000000AA"))
