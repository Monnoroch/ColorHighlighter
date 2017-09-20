"""Tests for path module."""

import unittest

from color_highlighter import path, sublime  # pylint: disable=no-name-in-module

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
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/color_highlighter", path.data_path(path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute data path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/color_highlighter", path.data_path(path.ABSOLUTE))
        unstub(sublime)


class IconsPathTest(unittest.TestCase):
    """Tests for icons_path."""

    def test_path(self):
        """Test get relative icons path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/color_highlighter/icons", path.icons_path(path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute icons path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/color_highlighter/icons", path.icons_path(path.ABSOLUTE))
        unstub(sublime)


class ThemesPathTest(unittest.TestCase):
    """Tests for themes_path."""

    def test_path(self):
        """Test get relative themes path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/color_highlighter/themes", path.themes_path(path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute themes path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/color_highlighter/themes", path.themes_path(path.ABSOLUTE))
        unstub(sublime)


class ColorPickerPathTest(unittest.TestCase):
    """Tests for color_picker_path."""

    def test_path(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual("Packages/User/color_highlighter/ColorPicker", path.color_picker_path(path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute color picker path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(test_path + "/User/color_highlighter/ColorPicker", path.color_picker_path(path.ABSOLUTE))
        unstub(sublime)


class ColorPickerFileTest(unittest.TestCase):
    """Tests for color_picker_file."""

    def test_path(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        platform = "platform"
        arch = "arch"
        when(sublime).platform().thenReturn(platform)
        when(sublime).arch().thenReturn(arch)
        self.assertEqual(
            "Packages/User/color_highlighter/ColorPicker/ColorPicker_%s_%s" % (platform, arch),
            path.color_picker_file(path.RELATIVE))
        unstub(sublime)

    def test_path_windows(self):
        """Test get relative color picker path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        when(sublime).platform().thenReturn("windows")
        self.assertEqual(
            "Packages/User/color_highlighter/ColorPicker/ColorPicker_win.exe",
            path.color_picker_file(path.RELATIVE))

    def test_absolute_path(self):
        """Test get absolute color picker path."""
        test_path = "/a/b/Packages"
        when(sublime).packages_path().thenReturn(test_path)
        platform = "platform"
        arch = "arch"
        when(sublime).platform().thenReturn(platform)
        when(sublime).arch().thenReturn(arch)
        self.assertEqual(
            test_path + "/User/color_highlighter/ColorPicker/ColorPicker_%s_%s" % (platform, arch),
            path.color_picker_file(path.ABSOLUTE))
        unstub(sublime)


class FakeColorSchemeTest(unittest.TestCase):
    """Tests for fake_color_scheme_path."""

    def test_path(self):
        """Test get a fake color scheme path for a color scheme."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            "Packages/User/color_highlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.RELATIVE))
        unstub(sublime)

    def test_absolute_path(self):
        """Test get absolute themes path."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            test_path + "/User/color_highlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.ABSOLUTE))
        unstub(sublime)

    def test_path_windows(self):
        """Test get a fake color scheme path for a color scheme on windows."""
        test_path = "/a/b/Packages"
        scheme = "Scheme.tmTheme"
        when(sublime).platform().thenReturn("windows")
        when(sublime).packages_path().thenReturn(test_path)
        self.assertEqual(
            "Packages/User/color_highlighter/themes/" + scheme,
            path.fake_color_scheme_path("Color/" + scheme, path.RELATIVE))
        unstub(sublime)
