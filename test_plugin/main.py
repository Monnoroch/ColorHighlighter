"""
Test plugin.

A plugin for sublime text that redirects all console output to /opt/sublime_text.log.
"""

import sys

try:
    from .flushing_file import FlushingFile
except ValueError:
    from flushing_file import FlushingFile

OUTPUT_FILE = FlushingFile(open("/opt/sublime_text.log", "w"))

sys.stdout = OUTPUT_FILE
sys.stderr = OUTPUT_FILE

print("Start!")
