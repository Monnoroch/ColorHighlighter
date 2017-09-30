"""Tests for flushing_file module."""

import unittest

from mockito import mock, verify

from .flushing_file import FlushingFile


class FlushingFileTest(unittest.TestCase):
    """Tests for FlushingFile."""

    def test_write(self):  # pylint: disable=no-self-use
        """
        Test write.

        Test that the write method calls write and flush on a wrapped file.
        """
        file = mock()
        flushing_file = FlushingFile(file)
        message = "test message"
        flushing_file.write(message)
        verify(file).write(message)
        verify(file).flush()
