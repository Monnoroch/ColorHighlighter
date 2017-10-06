"""A color highlighters that uses phantom sets to highlight colors."""

try:
    from . import st_helper
    from .color_highlighter import ColorHighlighter
except ValueError:
    import st_helper
    from color_highlighter import ColorHighlighter


if st_helper.running_in_st():
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

    if st_helper.is_st3():
        _phantom_styles = {
            "right": sublime.LAYOUT_INLINE,
            "left": sublime.LAYOUT_INLINE,
            "below": sublime.LAYOUT_BELOW
        }

    _inline_styles = {"right": True, "left": True}

    def __init__(self, view, name, style, length, debug):  # pylint: disable=too-many-arguments
        """
        Create a phantom color highlighter.

        Arguments:
        - view - a view to highlight colors in.
        - name - the name of the color highlighter.
        - style - the style of the phantoms.
        - length - the length of the block in the "inline" mode.
        - debug - whether to enable debug mode.
        """
        assert style in self._phantom_styles
        self._view = view
        self._name = name
        self._style = style
        self._length = length
        self._debug = debug

    def highlight_region(self, context, value):
        """
        Highlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to highlight, it's color).
        Returns True, if highlighted, False otherwise.
        """
        (region, color) = value
        html = self._generate_phantom_html(region, color)
        if self._debug:
            print("ColorHighlighter: action=highlight highlighter=PhantomColorHighlighter region=%s color=%s"
                  % (str(region), str(color)))
        self._view.add_phantom(
            PhantomColorHighlighter.phantom_key_template % (self._name, region.a, region.b),
            self._get_region(region), html,
            self._phantom_styles[self._style], None)

    def unhighlight_region(self, context, value):
        """
        Unhighlight a region.

        Arguments:
        - context - a dict with color highlighter run data.
        - value - tuple (region to unhighlight, it's color).
        """
        (region, _) = value
        self._view.erase_phantoms(PhantomColorHighlighter.phantom_key_template % (self._name, region.a, region.b))

    def _get_region(self, region):
        if self._style == "below":
            return region.region()
        elif self._style == "right":
            return sublime.Region(region.b, region.b)
        elif self._style == "left":
            return sublime.Region(region.a, region.a)

    def _generate_phantom_html(self, region, color):
        if self._style == "below":
            size = region.length()
        elif self._style in self._inline_styles:
            size = self._length
        return PhantomColorHighlighter.html_template % (color, PhantomColorHighlighter.space_symbol * size)
