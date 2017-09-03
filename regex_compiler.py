"""A module with tools for paths."""

import copy
import functools
import re

try:
    from . import st_helper
except ValueError:
    import st_helper


def compile_regex(config):
    """
    Build a regex from the config.

    Arguments:
    config -- a dict with two dicts inside: channels and formats. Channels are named definitions of how a channel might
    look. Formats use channel names to define how colors look and how to extract channels from them.
    Returns a regex for the input config.
    """
    channels = _normalize_channels(config.channels)
    channels["empty"] = ""
    formats = _normalize_regexes(config.formats, channels)
    formats = _normalize_dependencies(formats)
    if st_helper.is_st3():
        sorted_formats = sorted(formats.items(), key=functools.cmp_to_key(_order_formats))
    else:
        sorted_formats = sorted(formats.items(), cmp=_order_formats)
    regexes = "|".join(map(lambda name_format_pair: name_format_pair[1].regex, sorted_formats))
    return re.compile(regexes)


def _normalize_dependencies(formats):
    normalized_formats = copy.deepcopy(formats)
    for name in formats:
        after = {}
        _expand_after(formats, name, after, {})
        normalized_formats[name].after = after.keys()
    return normalized_formats


def _expand_after(formats, name, after_dict, used_names):
    if name in used_names:
        # TODO(monnoroch): explain in more detail which channels depend on each other.  # pylint: disable=fixme
        raise ValueError("Reccurent dependencies between formats!")
    used_names[name] = True

    if name not in formats:
        raise ValueError("Format %s does not exist." % name)

    for after_name in formats[name].after:
        after_dict[after_name] = True
        _expand_after(formats, after_name, after_dict, used_names)
    del used_names[name]


def _normalize_regexes(formats, channels):
    formats = copy.deepcopy(formats)
    for name in formats:
        color_format = formats[name]
        color_format.regex = _normalize_regex(color_format.regex, channels, name)
    return formats


def _order_formats(format1, format2):
    format_name1, format1 = format1
    format_name2, format2 = format2
    if format_name2 in format1.after:
        return 1
    if format_name1 in format2.after:
        return -1
    return len(format1.regex) - len(format2.regex)


def _normalize_regex(regex, channels, format_name):
    group_str_template = "(?P<%s>"
    group_template = "(?P<%s>%s)"
    groups = re.compile(regex).groupindex.keys()
    for group in groups:
        group_str = group_str_template % group
        group_start = regex.find(group_str)
        assert group_start != -1
        start = group_start + len(group_str)
        end = regex.find(")", start)
        assert end != -1
        channel_names = regex[start:end]
        group_channels = []
        for channel_name in channel_names.split("|"):
            channel = channels.get(channel_name, None)
            if channel is None:
                raise ValueError("Regex %s uses a non-existent channel %s for group %s." % (regex, channel_name, group))
            group_channels.append(channel)
        regex = regex.replace(
            group_template % (group, channel_names),
            group_template % ("%s_%s" % (format_name, group), "|".join(group_channels)))
    return group_template % (format_name, regex)


def _normalize_channels(channels):
    normalized_channels = {}
    for name in channels:
        normalized_channels[name] = _get_channel_value(channels, name, {})
    return normalized_channels


def _get_channel_value(channels, name, used_names):
    if name in used_names:
        # TODO(monnoroch): explain in more detail which channels depend on each other.  # pylint: disable=fixme
        raise ValueError("Reccurent dependencies between channels!")
    used_names[name] = True

    value = channels[name]
    if value in channels:
        return _get_channel_value(channels, value, used_names)
    return value
