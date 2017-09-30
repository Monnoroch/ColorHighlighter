"""A module with tools for working with colors."""

import colorsys


def normalize_hex_color(color):
    """
    Normalize any hex color to #RRGGBBAA format.

    Arguments:
    - color - the color to normalize.
    Returns normalized color in #RRGGBBAA format.
    """
    while len(color) < 9:
        color += "F"
    return color


def background_color_for_text_workaround(background_color, theme_background_color):  # pylint: disable=invalid-name
    """
    Background color bug workaround for ST.

    If one to set for a scope background color identical to the global background color, it doesn't work properly.
    Because of that, one needs to use this hack, which does a minimal change to the input color's green channel.
    Thus, after this transformation the color will be different from the background color and will be displayed
    correctly. This new color, whle different, is very hard to distinguish from the original color, so from the UX
    perspective, everything's fine.
    Argumetns:
    - background_color - the color to be used as a background color for a scope.
    - theme_background_color - the theme's backgroud color.
    Returns a background_color if it's not the same as the theme_background_color or a slightly modified
    background_color, if it is the same.
    """
    if background_color != theme_background_color:
        return background_color

    second_blue_symbol = background_color[-3]
    if second_blue_symbol == 'F':
        second_blue_symbol = 'E'
    else:
        second_blue_symbol = hex(int(second_blue_symbol, 16) + 1)[2:]
    return background_color[:-3] + second_blue_symbol + background_color[-2:]


def rgb_to_hex(r, g, b):  # pylint: disable=invalid-name
    """
    Convert numeric r, g, b color channels to a hex standard #RRGGBBAA color format.

    Arguments:
    - r - red channel in (0, 255).
    - g - green channel in (0, 255).
    - b - blue channel in (0, 255).
    """
    return "#%02X%02X%02XFF" % (r, g, b)


def complementary_color(color):
    """
    Get a complementary color to the input color.

    For example, white is the complementary color for black, yellow for cyan, etc.
    Argumets:
    - color - color in #RRGGBBAA format.
    Returns the complementary color to the input color.
    """
    (h, l, s) = colorsys.rgb_to_hls(  # pylint: disable=invalid-name
        int(color[1:3], 16) / 255.0, int(color[3:5], 16) / 255.0, int(color[5:7], 16) / 255.0)
    new_l = 1 - l
    if abs(new_l - l) < .15:
        new_l = .15
    (r, g, b) = colorsys.hls_to_rgb(h, new_l, s)  # pylint: disable=invalid-name
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))
