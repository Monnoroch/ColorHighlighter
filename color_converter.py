"""The module with a component for converting color text into colors."""

import colorsys


class ColorFormatConverter(object):
    """An interface for converting colors in a specific format to a canonical color representation."""

    def to_color(self, match):
        """
        Convert a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        raise NotImplementedError

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        raise NotImplementedError


class _Sharp8ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp8 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return match["sharp8"]

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        return color


class _Sharp6ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp6 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return match["sharp6"] + "ff"

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        return color[:-2]


class _Sharp4ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp4 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return "#%s%s%s%s" % (
            match["sharp4_R"] * 2, match["sharp4_G"] * 2, match["sharp4_B"] * 2, match["sharp4_A"] * 2)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        return "#%s%s%s%s" % (color[1], color[3], color[5], color[7])


class _Sharp3ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp3 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return "#%s%s%sff" % (match["sharp3_R"] * 2, match["sharp3_G"] * 2, match["sharp3_B"] * 2)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        return "#%s%s%s" % (color[1], color[3], color[5])


class _RgbaColorConverter(ColorFormatConverter):
    """A class for converting colors in rgba representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        r = _parse_decimal_channel(match["rgba_R"])  # pylint: disable=invalid-name
        g = _parse_decimal_channel(match["rgba_G"])  # pylint: disable=invalid-name
        b = _parse_decimal_channel(match["rgba_B"])  # pylint: disable=invalid-name
        a = _parse_float_channel(match["rgba_A"])  # pylint: disable=invalid-name
        if r is None or g is None or b is None or a is None:
            return None
        return "#%02X%02X%02X%02X" % (r, g, b, a)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        a = _channel_to_float(color[7:9])  # pylint: disable=invalid-name
        return "rgba(%d, %d, %d, %s)" % (r, g, b, a)


class _RgbColorConverter(ColorFormatConverter):
    """A class for converting colors in rgb representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        r = _parse_decimal_channel(match["rgb_R"])  # pylint: disable=invalid-name
        g = _parse_decimal_channel(match["rgb_G"])  # pylint: disable=invalid-name
        b = _parse_decimal_channel(match["rgb_B"])  # pylint: disable=invalid-name
        if r is None or g is None or b is None:
            return None
        return "#%02X%02X%02Xff" % (r, g, b)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        return "rgb(%d, %d, %d)" % (r, g, b)


class _HsvaColorConverter(ColorFormatConverter):
    """A class for converting colors in hsva representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        h = _parse_hue_channel(match["hsva_H"])  # pylint: disable=invalid-name
        s = _parse_percent_channel(match["hsva_S"])  # pylint: disable=invalid-name
        v = _parse_percent_channel(match["hsva_V"])  # pylint: disable=invalid-name
        a = _parse_float_channel(match["hsva_A"])  # pylint: disable=invalid-name
        if h is None or s is None or v is None or a is None:
            return None
        r, g, b = _hsv_to_rgb(h, s, v)  # pylint: disable=invalid-name
        return "#%02X%02X%02X%02X" % (r, g, b, a)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        a = _channel_to_float(color[7:9])  # pylint: disable=invalid-name
        h, s, v = _rgb_to_hsv(r, g, b)  # pylint: disable=invalid-name
        return "hsva(%d, %d%%, %d%%, %s)" % (h, s, v, a)


class _HsvColorConverter(ColorFormatConverter):
    """A class for converting colors in hsv representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        h = _parse_hue_channel(match["hsv_H"])  # pylint: disable=invalid-name
        s = _parse_percent_channel(match["hsv_S"])  # pylint: disable=invalid-name
        v = _parse_percent_channel(match["hsv_V"])  # pylint: disable=invalid-name
        if h is None or s is None or v is None:
            return None
        r, g, b = _hsv_to_rgb(h, s, v)  # pylint: disable=invalid-name
        return "#%02X%02X%02Xff" % (r, g, b)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        h, s, v = _rgb_to_hsv(r, g, b)  # pylint: disable=invalid-name
        return "hsv(%d, %d%%, %d%%)" % (h, s, v)


class _HslaColorConverter(ColorFormatConverter):
    """A class for converting colors in hsla representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        h = _parse_hue_channel(match["hsla_H"])  # pylint: disable=invalid-name
        s = _parse_percent_channel(match["hsla_S"])  # pylint: disable=invalid-name
        l = _parse_percent_channel(match["hsla_L"])  # pylint: disable=invalid-name
        a = _parse_float_channel(match["hsla_A"])  # pylint: disable=invalid-name
        if h is None or s is None or l is None or a is None:
            return None
        r, g, b = _hsl_to_rgb(h, s, l)  # pylint: disable=invalid-name
        return "#%02X%02X%02X%02X" % (r, g, b, a)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        a = _channel_to_float(color[7:9])  # pylint: disable=invalid-name
        h, s, l = _rgb_to_hsl(r, g, b)  # pylint: disable=invalid-name
        return "hsla(%d, %d%%, %d%%, %s)" % (h, s, l, a)


class _HslColorConverter(ColorFormatConverter):
    """A class for converting colors in hsl representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        h = _parse_hue_channel(match["hsl_H"])  # pylint: disable=invalid-name
        s = _parse_percent_channel(match["hsl_S"])  # pylint: disable=invalid-name
        l = _parse_percent_channel(match["hsl_L"])  # pylint: disable=invalid-name
        if h is None or s is None or l is None:
            return None
        r, g, b = _hsl_to_rgb(h, s, l)  # pylint: disable=invalid-name
        return "#%02X%02X%02Xff" % (r, g, b)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a canonical color representation.
        Returns a current color representation for the input color.
        """
        r = _channel_to_decimal(color[1:3])  # pylint: disable=invalid-name
        g = _channel_to_decimal(color[3:5])  # pylint: disable=invalid-name
        b = _channel_to_decimal(color[5:7])  # pylint: disable=invalid-name
        h, s, l = _rgb_to_hsl(r, g, b)  # pylint: disable=invalid-name
        return "hsl(%d, %d%%, %d%%)" % (h, s, l)


class ColorConverter(ColorFormatConverter):
    """Class for converting color text into colors."""

    _converters = {
        "sharp8": _Sharp8ColorConverter(),
        "sharp6": _Sharp6ColorConverter(),
        "sharp4": _Sharp4ColorConverter(),
        "sharp3": _Sharp3ColorConverter(),
        "rgba": _RgbaColorConverter(),
        "rgb": _RgbColorConverter(),
        "hsva": _HsvaColorConverter(),
        "hsv": _HsvColorConverter(),
        "hsla": _HslaColorConverter(),
        "hsl": _HslColorConverter()
    }

    def __init__(self, formats):
        """
        Init a ColorConverter.

        Arguments:
        - formats - color formats configuration.
        """
        self._formats = formats

    def to_color(self, match):
        """
        Convert a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        for name in self._formats:
            if match.get(name, None) is not None:
                color = ColorConverter._converters[name].to_color(match)
                if color is None:
                    return None
                return color.lower()
        raise Exception("Match %s could not be canonicalized." % match)

    def from_color(self, color):
        """
        Convert a canonical color representation into a current color representation..

        Arguments:
        - color - a pair of the canonical color representation and a color format.
        Returns a current color representation for the input color.
        """
        color, color_format = color
        converter = self._converters.get(color_format, None)
        if converter is None:
            raise Exception("Unknown color format %s." % color_format)
        return converter.from_color(color)


def _channel_to_decimal(channel):
    return int(channel, 16)


def _channel_to_float(channel):
    value = str(int(channel, 16) / 255.0)
    if value.find(".") == -1:
        return value
    while value[-1] == "0":
        value = value[:-1]
    if value.startswith("0."):
        value = value[1:]
    return value


def _channel_to_percent(channel):
    return int(round((int(channel, 16) * 100) / 255.0))


def _channel_to_hue(channel):
    return int(round((int(channel, 16) * 360) / 255.0))


def _parse_decimal_channel(text):
    value = int(text)
    if value < 0 or value > 255:
        return None
    return value


def _parse_float_channel(text):
    if text == ".":
        return None
    value = float(text)
    if value < 0 or value > 1:
        return None
    return int(round(value * 255.0))


def _parse_percent_channel(text):
    if text == "0":
        return 0.0
    if text[-1] != "%":
        return None
    value = int(text[:-1])
    if value < 0 or value > 100:
        return None
    return value / 100.0


def _parse_hue_channel(text):
    value = int(text)
    if value < 0 or value > 360:
        return None
    if value == 360:
        return 0
    return value / 360.0


def _hsv_to_rgb(h, s, v):  # pylint: disable=invalid-name
    r, g, b = colorsys.hsv_to_rgb(h, s, v)  # pylint: disable=invalid-name
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def _rgb_to_hsv(r, g, b):  # pylint: disable=invalid-name
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)  # pylint: disable=invalid-name
    return int(round(h * 360)), int(round(s * 100)), int(round(v * 100))


def _hsl_to_rgb(h, s, l):  # pylint: disable=invalid-name
    r, g, b = colorsys.hls_to_rgb(h, l, s)  # pylint: disable=invalid-name
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def _rgb_to_hsl(r, g, b):  # pylint: disable=invalid-name
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)  # pylint: disable=invalid-name
    return int(round(h * 360)), int(round(s * 100)), int(round(l * 100))
