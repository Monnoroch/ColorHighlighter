"""Tests for load_resource module."""

import builtins
import codecs
import os
import unittest

from ColorHighlighter import path, st_helper, sublime  # pylint: disable=no-name-in-module
from ColorHighlighter.load_resource import (  # pylint: disable=no-name-in-module,import-error
    get_binary_resource_size, load_binary_resource, load_resource)

from mockito import ANY, mock, unstub, verify, when


class LoadResourceTest(unittest.TestCase):
    """Tests for load_resource."""

    def test_st3(self):
        """In ST3 load_resource just calls sublime.load_resource."""
        when(st_helper).is_st3().thenReturn(True)
        test_path = "test/path"
        content = "content"
        when(sublime).load_resource(test_path).thenReturn(content)
        self.assertEqual(content, load_resource(test_path))
        verify(sublime).load_resource(test_path)
        unstub(sublime)

    def test_st2(self):
        """In ST2 load_resource reads the resource's file."""
        when(st_helper).is_st3().thenReturn(False)
        test_path = "Packages/test/path"
        content = "content"
        file = mock()
        when(file).read().thenReturn(content)
        when(file).__enter__().thenReturn(file)
        when(file).__exit__()
        when(codecs).open(ANY, ANY, ANY).thenReturn(file)
        when(sublime).packages_path().thenReturn("/sublime/Packages")
        self.assertEqual(content, load_resource(test_path))
        test_absolute_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), test_path)
        verify(codecs).open(test_absolute_path, "r", "utf-8")
        verify(file).read()
        unstub(sublime, codecs)


class LoadBinaryResourceTest(unittest.TestCase):
    """Tests for load_binary_resource."""

    def test_st3(self):
        """In ST3 load_binary_resource just calls sublime.load_binary_resource."""
        when(st_helper).is_st3().thenReturn(True)
        test_path = "test/path"
        content = "content"
        when(sublime).load_binary_resource(test_path).thenReturn(content)
        self.assertEqual(content, load_binary_resource(test_path))
        verify(sublime).load_binary_resource(test_path)
        unstub(sublime)

    def test_st2(self):
        """In ST2 load_binary_resource reads the resource's file."""
        when(st_helper).is_st3().thenReturn(False)
        test_path = "Packages/test/path"
        content = "content"
        file = mock()
        when(file).read().thenReturn(content)
        when(file).__enter__().thenReturn(file)
        when(file).__exit__()
        when(builtins).open(ANY, ANY).thenReturn(file)
        when(sublime).packages_path().thenReturn("/sublime/Packages")
        self.assertEqual(content, load_binary_resource(test_path))
        test_absolute_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), test_path)
        verify(builtins).open(test_absolute_path, "rb")
        verify(file).read()
        unstub(sublime, builtins)


class GetBinaryResourceSizeTest(unittest.TestCase):
    """Tests for get_binary_resource_size."""

    def test_st3(self):
        """In ST3 get_binary_resource_size just calls sublime.load_binary_resource."""
        when(st_helper).is_st3().thenReturn(True)
        test_path = "test/path"
        content = "content"
        when(sublime).load_binary_resource(test_path).thenReturn(content)
        self.assertEqual(len(content), get_binary_resource_size(test_path))
        verify(sublime).load_binary_resource(test_path)
        unstub(sublime)

    def test_st2(self):
        """In ST2 get_binary_resource_size reads the resource's file."""
        when(st_helper).is_st3().thenReturn(False)
        test_path = "Packages/test/path"
        file_size = 17
        when(os.path).getsize(ANY).thenReturn(file_size)
        when(sublime).packages_path().thenReturn("/sublime/Packages")
        self.assertEqual(file_size, get_binary_resource_size(test_path))
        test_absolute_path = os.path.join(os.path.dirname(path.packages_path(path.ABSOLUTE)), test_path)
        verify(os.path).getsize(test_absolute_path)
        unstub(sublime, os.path)
