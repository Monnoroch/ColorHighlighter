"""A color highlighters that uses phantom sets to highlight colors."""

try:
    from .st_helper import running_in_st
    from .debug import DEBUG
    from .color_highlighter import ColorHighlighter
except ValueError:
    from st_helper import running_in_st
    from debug import DEBUG
    from color_highlighter import ColorHighlighter


if running_in_st():
    import sublime  # pylint: disable=import-error
else:
    from . import sublime


class PhantomColorHighlighter(ColorHighlighter):
    """
    A color highlighter that highlights colors using phantoms.

    Only supported on ST3.
    """

    phantom_key_template = "CH_phantom_%s_%d_%d"

    html_template = '''
<body>
    <style>
        * {
            background-color: %s;
        }
    </style>
    %s
</body>
'''
    space_symbol = "&nbsp;"

    def __init__(self, view, name):
        """
        Create a phantom color highlighter.

        Arguments:
        - view - a view to highlight colors in.
        - name - the name of the color highlighter.
        """
        self._view = view
        self._name = name

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        (region, color) = value
        html = _generate_phantom_html(region, color)
        if DEBUG:
            print("ColorHighlighter: action=highlight highlighter=PhantomColorHighlighter region=%s color=%s"
                  % (str(region), str(color)))
        self._view.add_phantom(
            PhantomColorHighlighter.phantom_key_template % (self._name, region.a, region.b), region.region(), html,
            sublime.LAYOUT_BELOW, None)

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        (region, _) = value
        self._view.erase_phantoms(PhantomColorHighlighter.phantom_key_template % (self._name, region.a, region.b))


def _generate_phantom_html(region, color):
    return PhantomColorHighlighter.html_template % (color, PhantomColorHighlighter.space_symbol * region.length())
