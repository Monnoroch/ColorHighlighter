"""Tests for path module."""

import os
import unittest

from ColorHighlighter import path, sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.settings import COLOR_HIGHLIGHTER_SETTINGS_NAME

from mockito import unstub, when


class NormalizePathForStTest(unittest.TestCase):
    """Tests for normalize_path_for_st."""

    def test_normalize(self):
        """Test normalize returns it's argument."""
        test_path = "/a/b/c.txt"
        self.assertEqual(test_path, path.normalize_path_for_st(test_path))

    def test_normalize_windows(self):
        """Test normalize returns a linux style path in windows."""
        when(sublime).platform().thenReturn("windows")
        self.assertEqual("a/b/c.txt", path.normalize_path_for_st("a\\b\\c.txt"))
        unstub(sublime)


class PackagesPathTest(unittest.TestCase):
    """Tests for packages_path."""

    def test_path(self):
        """Test get relative packages path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages", path.packages_path(path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute packages path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path, path.packages_path(path.ABSOLUTE))
        unstub(sublime)


class DataPathTest(unittest.TestCase):
    """Tests for data_path."""

    def test_path(self):
        """Test get relative data path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/ColorHighlighter", path.data_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_path_package(self):
        """Test get relative data path with a package installation."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(False)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/Color Highlighter", path.data_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute data path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/ColorHighlighter", path.data_path(path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)


class IconsPathTest(unittest.TestCase):
    """Tests for icons_path."""

    def test_path(self):
        """Test get relative icons path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/ColorHighlighter/icons", path.icons_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_path_package(self):
        """Test get relative icons path with a package installation."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(False)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/Color Highlighter/icons", path.icons_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute icons path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/ColorHighlighter/icons", path.icons_path(path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)


class ThemesPathTest(unittest.TestCase):
    """Tests for themes_path."""

    def test_path(self):
        """Test get relative themes path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/ColorHighlighter/themes", path.themes_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_path_package(self):
        """Test get relative themes path with a package installation."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(False)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/Color Highlighter/themes", path.themes_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute themes path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/ColorHighlighter/themes", path.themes_path(path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)


class ColorPickerPathTest(unittest.TestCase):
    """Tests for color_picker_path."""

    def test_path(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/ColorHighlighter/ColorPicker", path.color_picker_path(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute color picker path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/ColorHighlighter/ColorPicker", path.color_picker_path(path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)


class ColorPickerFileTest(unittest.TestCase):
    """Tests for color_picker_file."""

    def test_path(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        platform = "platform"
        arch = "arch"
        when(sublime).platform().thenReturn(platform)
        when(sublime).arch().thenReturn(arch)
        self.assertEqual(
            "Packages/User/ColorHighlighter/ColorPicker/ColorPicker_%s_%s" % (platform, arch),
            path.color_picker_file(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_path_package(self):
        """Test get relative color picker path with a package installation."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(False)
        when(sublime).packages_path().thenReturn(test_path)
        platform = "platform"
        arch = "arch"
        when(sublime).platform().thenReturn(platform)
        when(sublime).arch().thenReturn(arch)
        self.assertEqual(
            "Packages/User/Color Highlighter/ColorPicker/ColorPicker_%s_%s" % (platform, arch),
            path.color_picker_file(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_path_windows(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        when(sublime).platform().thenReturn("windows")
        self.assertEqual(
            "Packages/User/ColorHighlighter/ColorPicker/ColorPicker_win.exe",
            path.color_picker_file(path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute color picker path."""
        test_path = "/a/b/Packages"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        platform = "platform"
        arch = "arch"
        when(sublime).platform().thenReturn(platform)
        when(sublime).arch().thenReturn(arch)
        self.assertEqual(
            test_path + "/User/ColorHighlighter/ColorPicker/ColorPicker_%s_%s" % (platform, arch),
            path.color_picker_file(path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)


class FakeColorSchemeTest(unittest.TestCase):
    """Tests for fake_color_scheme_path."""

    def test_path(self):
        """Test get a fake color scheme path for a color scheme."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            "Packages/User/ColorHighlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.RELATIVE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path(self):
        """Test get absolute themes path."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            test_path + "/User/ColorHighlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)

    def test_absolute_path_package(self):
        """Test get absolute themes path with a package installation."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(False)
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            test_path + "/User/Color Highlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.ABSOLUTE))
        unstub(sublime)
        unstub(os.path)

    def test_path_windows(self):
        """Test get a fake color scheme path for a color scheme on windows."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(os.path).exists(test_path + "/ColorHighlighter/" + COLOR_HIGHLIGHTER_SETTINGS_NAME).thenReturn(True)
        when(sublime).platform().thenReturn("windows")
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            "Packages/User/ColorHighlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.RELATIVE))
        unstub(sublime)
        unstub(os.path)
