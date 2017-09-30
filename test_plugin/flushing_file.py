"""
Flushing file.

A module with the FlushingFile component that wraps a file and flushes it on writes.
"""


class FlushingFile(object):
    """
    Flushing file.

    A wrapper around a file that flushes every time anything is written.
    """

    def __init__(self, file):
        """
        Flushing file constructor.

        Arguments:
        file -- a file to wrap.
        """
        self.file = file

    def write(self, message):
        """
        Write to a file.

        Arguments:
        message -- a message to write.
        """
        self.file.write(message)
        self.file.flush()
