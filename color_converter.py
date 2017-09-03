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


class _Sharp6ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp6 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return match["sharp6"] + "FF"


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


class _Sharp3ColorConverter(ColorFormatConverter):
    """A class for converting colors in sharp3 representation to a canonical one."""

    def to_color(self, match):
        """
        Get a color match into a canonical color representation.

        Arguments:
        - match - a dict with matched color formats.
        Returns a canonical color representation for the match.
        """
        return "#%s%s%sFF" % (match["sharp3_R"] * 2, match["sharp3_G"] * 2, match["sharp3_B"] * 2)


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
        return "#%02X%02X%02XFF" % (r, g, b)


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
        return "#%02X%02X%02XFF" % (r, g, b)


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
        return "#%02X%02X%02XFF" % (r, g, b)


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
                return ColorConverter._converters[name].to_color(match)


def _parse_decimal_channel(text):
    value = int(text)
    if value < 0 or value > 255:
        return None
    return value


def _parse_float_channel(text):
    value = float(text)
    if value < 0 or value > 1:
        return None
    return int(round(value * 255.0))


def _parse_percent_channel(text):
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


def _hsl_to_rgb(h, s, l):  # pylint: disable=invalid-name
    r, g, b = colorsys.hls_to_rgb(h, l, s)  # pylint: disable=invalid-name
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
