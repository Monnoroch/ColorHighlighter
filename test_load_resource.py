"""Tests for load_resource module."""

try:
    from .st_helper import running_in_st
except ValueError:
    from st_helper import running_in_st


if not running_in_st():

    import unittest
    from mockito import mock, when, verify, ANY
    import codecs
    import os

    from .load_resource import load_resource
    from . import path
    from . import st_helper

    from . import sublime

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
