"""Tests for IconFactory."""

import os
import subprocess
import unittest

from ColorHighlighter.gutter_icons_color_highlighter import (  # pylint: disable=no-name-in-module,import-error
    IconFactory)
from ColorHighlighter.settings import (  # pylint: disable=no-name-in-module,import-error
    GutterIconsColorHighlighterSettings)

from mockito import mock, verify, when


class IconFactoryTest(unittest.TestCase):
    """Tests for IconFactory."""

    def test_check(self):
        """Test check."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#ffffffff"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenReturn(("".encode("utf-8"), "".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        when(os.path).exists(icon_path).thenReturn(True)
        self.assertTrue(icon_factory.check())

    def test_check_fail(self):
        """Test check failed."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#ffffffff"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenReturn(("".encode("utf-8"), "".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        when(os.path).exists(icon_path).thenReturn(False)
        self.assertFalse(icon_factory.check())

    def test_check_kill_process_on_timeout(self):  # pylint: disable=invalid-name
        """Test check fails when timeouted in Popen even if the test icon file already exists."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#ffffffff"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenRaise(subprocess.TimeoutExpired(None, None))
        when(process).communicate().thenReturn(("output".encode("utf-8"), "error".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        when(os.path).exists(icon_path).thenReturn(True)
        self.assertFalse(icon_factory.check())
        verify(process).kill()
        verify(process).communicate()

    def test_check_kill_process_on_timeout_empty_message(self):  # pylint: disable=invalid-name
        """Test check doesn't fail when timeouted in Popen if stderr is empty."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#ffffffff"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenRaise(subprocess.TimeoutExpired(None, None))
        when(process).communicate().thenReturn(("".encode("utf-8"), "".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        when(os.path).exists(icon_path).thenReturn(True)
        self.assertTrue(icon_factory.check())
        verify(process).kill()
        verify(process).communicate()

    def test_valid_style_set(self):
        """Test that sets of valid icon styles are consistent."""
        self.assertEqual(
            set(GutterIconsColorHighlighterSettings.VALID_STYLES),
            set(IconFactory._convert_styles.keys()))  # pylint: disable=protected-access

    def test_invalid_style(self):
        """Invalid icon style yields none."""
        sublime_icons_path = "test/sublime/icons/path"
        icon_factory = IconFactory("test/icons/path", sublime_icons_path, "", 50, False)
        color = "#color"
        with self.assertRaises(AssertionError):
            icon_factory.get_icon_path("invalid-style", color)

    def test_path_exists(self):
        """Test icon exists."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        icon_factory = IconFactory(icons_path, sublime_icons_path, "test/convert", 50, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        when(os.path).exists(os.path.join(icons_path, icon_name)).thenReturn(True)
        self.assertEqual(os.path.join(sublime_icons_path, icon_name), icon_factory.get_icon_path(style, color))

    def test_cached(self):
        """Test icon path in cache."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        icon_factory = IconFactory(icons_path, sublime_icons_path, "test/convert", 50, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        when(os.path).exists(os.path.join(icons_path, icon_name)).thenReturn(True)
        # Fill in the cache.
        icon_factory.get_icon_path(style, color)
        when(os.path).exists(os.path.join(icons_path, icon_name)).thenReturn(False)
        self.assertEqual(os.path.join(sublime_icons_path, icon_name), icon_factory.get_icon_path(style, color))

    def test_create_icon(self):
        """Test create icon."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        when(os.path).exists(icon_path).thenReturn(False).thenReturn(True)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenReturn(("".encode("utf-8"), "".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        self.assertEqual(os.path.join(sublime_icons_path, icon_name), icon_factory.get_icon_path(style, color))

    def test_create_icon_failed(self):
        """Test could not create icon."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        when(os.path).exists(icon_path).thenReturn(False).thenReturn(False)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenReturn(("".encode("utf-8"), "".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        bad_icon_name = IconFactory._bad_icon_name  # pylint: disable=protected-access
        self.assertEqual(os.path.join(sublime_icons_path, bad_icon_name), icon_factory.get_icon_path(style, color))

    def test_kill_process_on_timeout(self):
        """Test create icon."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        when(os.path).exists(icon_path).thenReturn(False)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenRaise(subprocess.TimeoutExpired(None, None))
        when(process).communicate().thenReturn(("output".encode("utf-8"), "error".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        bad_icon_name = IconFactory._bad_icon_name  # pylint: disable=protected-access
        self.assertEqual(os.path.join(sublime_icons_path, bad_icon_name), icon_factory.get_icon_path(style, color))
        verify(process).kill()
        verify(process).communicate()

    def test_kill_process_on_timeout_but_file_created(self):  # pylint: disable=invalid-name
        """Test create icon."""
        icons_path = "test/icons/path"
        sublime_icons_path = "test/sublime/icons/path"
        convert = "test/convert"
        timeout = 50
        icon_factory = IconFactory(icons_path, sublime_icons_path, convert, timeout, False)
        style = "circle"
        color = "#color"
        icon_name = IconFactory._icon_name_template % (style, color[1:])  # pylint: disable=protected-access
        icon_path = os.path.join(icons_path, icon_name)
        when(os.path).exists(icon_path).thenReturn(False).thenReturn(True)
        convert_command = IconFactory._convert_command_template % (  # pylint: disable=protected-access
            convert, color, IconFactory._convert_styles[style], icon_path)  # pylint: disable=protected-access
        process = mock()
        when(process).communicate(timeout=timeout).thenRaise(subprocess.TimeoutExpired(None, None))
        when(process).communicate().thenReturn(("output".encode("utf-8"), "error".encode("utf-8")))
        when(subprocess).Popen(
            convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).thenReturn(process)
        self.assertEqual(os.path.join(sublime_icons_path, icon_name), icon_factory.get_icon_path(style, color))
        verify(process).kill()
        verify(process).communicate()
