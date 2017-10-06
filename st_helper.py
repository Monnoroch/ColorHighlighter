"""Helper functions for checking for Sublime Text."""

try:
    import sublime  # noqa: F401  # pylint: disable=unused-import
    SUBLIME_IMPORTED = True  # For prod.
except ImportError:
    SUBLIME_IMPORTED = False  # For tests.


def running_in_st():
    """Whether the code runs in ST or not."""
    return SUBLIME_IMPORTED


def version():
    """Return a ST version. Return 0 if not running in ST."""
    if not running_in_st():
        return 0

    return int(sublime.version())


def is_st3():
    """
    Whether the code runs in ST3 or not.

    Plugin development is mainly for ST3, so tests execute ST3 code.
    """
    if not running_in_st():
        return True

    return version() >= 3000


def st_version():
    """Return a string representation of a major ST version."""
    if running_in_st():
        if is_st3():
            major_version = "st3"
        else:
            major_version = "st2"
    else:
        major_version = "none"
    return major_version
