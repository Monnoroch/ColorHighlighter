"""A dummy event listener."""


class DummyEventListener(object):
    """
    An event listener that ignores events.

    Supposed to be used in place of any other event listener when it is disabled.
    """

    def __init__(self):
        """Init ColorSelectionListener."""
        pass

    def on_selection_modified(self):
        """Call when view's selection was modified."""
        pass

    def on_load(self):
        """Call when view's content is loaded."""
        pass

    def on_hover(self, point, hover_zone):
        """on_hover event."""
        pass

    def on_modified(self):
        """on_modified event."""
        pass
