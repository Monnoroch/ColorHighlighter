
# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import stat
import re
import colorsys
import subprocess
import threading
import shutil
import codecs
import time

plugin_name = "Color Highlighter"

try:
    import colors
except ImportError:
    colors = __import__(plugin_name, fromlist=["colors"]).colors


version = "7.0"

### ST version helpers

# get ST version as int
def get_version():
    return int(sublime.version())

# check, if it's ST3
def is_st3():
    return get_version() >= 3000

### async helpers

if is_st3():
    def run_async(cb):
        sublime.set_timeout_async(cb, 0)
else:
    class RunAsync(threading.Thread):
        def __init__(self, cb):
            self.cb = cb
            threading.Thread.__init__(self)

        def run(self):
            self.cb()

    def run_async(cb):
        RunAsync(cb).start()

# python helpers

if is_st3():
    def is_str(val):
        return type(val) == str
else:
    def is_str(val):
        t = type(val)
        return t == str or t == unicode

if sublime.platform() == "windows":
    def conv_path(path):
        return path.replace("\\", "/")
else:
    def conv_path(path):
        return path

### Paths helpers

PRelative = True
PAbsolute = False

# get relative or absolute packages path
def packages_path(rel=PRelative):
    path = sublime.packages_path()
    if rel:
        path = os.path.basename(path)
    return path

# get relative or absolute data path
def data_path(rel=PRelative):
    return os.path.join(packages_path(rel), "User", plugin_name)

# get relative or absolute icons path
def icons_path(rel=PRelative):
    return os.path.join(data_path(rel), "icons")

# get relative or absolute themes path
def themes_path(rel=PRelative):
    return os.path.join(data_path(rel), "themes")

# get color picker binary file name
def color_picker_file():
    suff = None
    platf = sublime.platform()
    if platf == "windows":
        suff = "win.exe"
    else:
        suff = platf + "_" + sublime.arch()

    return os.path.join("ColorPicker", "ColorPicker_" + suff)

# get relative or absolute color picker binary path
def color_picker_path(rel=PRelative):
    return os.path.join(packages_path(rel), plugin_name, color_picker_file())

# get relative or absolute themes path
def color_picker_user_path(rel=PRelative):
    return os.path.join(data_path(rel), color_picker_file())

# create directory if not exists
def create_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

### Theme builder

def region_name(s):
    return "mcol_" + s[1:]

def read_file(fl):
    with codecs.open(fl, "r", "utf-8") as f:
        return f.read()

# html generator for color scheme
class HtmlGen:
    colors = {}
    to_add = []
    color_scheme = None
    color_scheme_abs = None
    fake_scheme = None
    fake_scheme_abs = None
    gen_string = """
<dict>
<key>name</key>
<string>mon_color</string>
<key>scope</key>
<string>%s</string>
<key>settings</key>
<dict>
<key>background</key>
<string>%s</string>
<key>caret</key>
<string>%s</string>
<key>foreground</key>
<string>%s</string>
</dict>
</dict>\n
"""

    def __init__(self, cs):
        self.color_scheme = cs
        self.color_scheme_abs = os.path.join(os.path.dirname(packages_path(PAbsolute)), self.color_scheme)

        base = os.path.basename(cs)
        self.fake_scheme = os.path.join(themes_path(), base)
        self.fake_scheme_abs = os.path.join(themes_path(PAbsolute), base)

    def flush(self):
        any = False
        for col in self.to_add:
            if col in self.colors.keys():
                continue

            self.colors[col] = self.get_cont_col(col)
            any = True

        if any:
            data = None
            if get_version() >= 3000:
                data = sublime.load_resource(self.color_scheme)
            else:
                data = read_file(self.color_scheme_abs).decode("utf-8")

            n = data.find("<array>") + len("<array>")
            with codecs.open(self.fake_scheme_abs, "wb") as f:
                f.write(data[:n].encode("utf-8"))
                for col in self.colors.keys():
                    cont = self.colors[col]
                    f.write((self.gen_string % (region_name(col), col, cont, cont)).encode("utf-8"))
                f.write(data[n:].encode("utf-8"))
        self.to_add = []
        return any

    def add_color(self, col):
        self.to_add.append(col)

    def scheme_name(self):
        if len(self.colors) == 0:
            return self.color_scheme
        else:
            return self.fake_scheme

    def get_cont_col(self, col):
        (h, l, s) = colorsys.rgb_to_hls(int(col[1:3],16)/255.0, int(col[3:5],16)/255.0, int(col[5:7],16)/255.0)
        l1 = 1 - l
        if abs(l1 - l) < .15:
            l1 = .15
        (r, g, b) = colorsys.hls_to_rgb(h, l1, s)
        return self.tohex(int(r * 255), int(g * 255), int(b * 255)) # true complementary

    def tohex(self, r, g, b, a=None):
        if a is None:
            a = 255
        return "#%02X%02X%02X%02X" % (r, g, b, a)

### Setting helper

pref_fname = "Preferences.sublime-settings"

class Settings:
    fname = "ColorHighlighter.sublime-settings"
    callbacks = None
    obj = None
    prefs = None

    enabled = None
    style = None
    file_exts = None
    color_scheme = None

    def __init__(self, callbacks):
        self.callbacks = callbacks
        self.obj = sublime.load_settings(self.fname)
        self.obj.clear_on_change("ColorHighlighter")
        self.obj.add_on_change("ColorHighlighter", lambda: self.on_ch_settings_change())

        self.prefs = sublime.load_settings(pref_fname)
        self.prefs.clear_on_change("ColorHighlighter")
        self.prefs.add_on_change("ColorHighlighter", lambda: self.on_prefs_settings_change())

    def has(self, name):
        return self.obj.has(name)

    def get(self, name, default=None):
        return self.obj.get(name, default)

    def set(self, name, val):
        self.obj.set(name, val)

    def erase(self, name):
        self.obj.erase(name)

    def save(self):
        sublime.save_settings(self.fname)

    def on_ch_settings_change(self, forse=False):
        self.obj = sublime.load_settings(self.fname)

        enabled = self.obj.get("enabled")
        if forse or self.enabled != enabled:
            self.enabled = enabled
            self.callbacks.enable(enabled)

        style = self.obj.get("style")
        if forse or self.style != style:
            self.style = style
            self.callbacks.set_style(style)

        ha_style = self.obj.get("ha_style")
        if forse or self.ha_style != ha_style:
            self.ha_style = ha_style
            self.callbacks.set_ha_style(ha_style)

        file_exts = self.obj.get("file_exts")
        if forse or self.file_exts != file_exts:
            self.file_exts = file_exts
            self.callbacks.set_exts(file_exts)

        icons = self.obj.get("icons")
        if forse or self.icons != icons:
            self.icons = icons
            self.callbacks.set_icons(icons)

        ha_icons = self.obj.get("ha_icons")
        if forse or self.ha_icons != ha_icons:
            self.ha_icons = ha_icons
            self.callbacks.set_ha_icons(ha_icons)

        formats = self.obj.get("formats")
        if forse or self.formats != formats:
            self.formats = formats
            self.callbacks.set_formats(formats, self.obj.get("channels"))

    def on_prefs_settings_change(self, forse=False):
        self.prefs = sublime.load_settings(pref_fname)

        color_scheme = self.prefs.get("color_scheme")
        if forse or self.color_scheme != color_scheme:
            self.color_scheme = color_scheme
            self.callbacks.set_scheme(color_scheme)


### Color finder

class ColorConverter:
    conf = None
    regex = None
    regex_cache = {}

    def set_conf(self, conf, channels):
        self.conf = conf
        self.regex = self._build_regex(conf, channels)

    def _build_regex(self, conf, channels): # -> regex object
        res = []
        for fmt in conf.keys():
            val = conf[fmt]
            if "regex" not in val.keys():
                continue
            res.append((val["order"], "(?P<" + fmt + ">" + val["regex"] + ")"))
        res.sort(key=lambda x: x[0])
        return re.compile("|".join(map(lambda x: x[1], res)))

    def _get_regex(self, regex): # -> regex object
        if not is_str(regex):
            return regex

        if regex in self.regex_cache.keys():
            return self.regex_cache[regex]
        res = re.compile(regex)
        self.regex_cache[regex] = res
        return res

    def _match_regex(self, regex, text): # -> match result
        m = self._get_regex(regex).search(text)
        if m:
            return m.groupdict()
        return None

    def _conv_val_chan(self, val, typ):
        if typ == "empty":
            return "FF"
        elif typ == "hex1":
            return val*2
        elif typ == "hex2":
            return val
        elif typ == "dec":
            res = hex(int(val))[2:].upper()
            if len(res) == 1:
                res = "0" + res
            return res
        elif typ == "float":
            res = hex(int(round(float(val) * 255.0)))[2:].upper()
            if len(res) == 1:
                res = "0" + res
            return res
        elif typ == "perc":
            res = hex(int(round(float(int(val[:-1]) * 255) / 100.0)))[2:].upper()
            if len(res) == 1:
                res = "0" + res
            return res
        return None

    def _conv_val_chan_back(self, val, typ):
        if typ == "hex1" and val[0] == val[1]:
            return val[0]
        elif typ == "dec":
            return str(int(val, 16))
        elif typ == "float":
            return str(int(val, 16) / 255.0)
        elif typ == "perc":
            return str(round((int(val, 16) * 100.0) / 255.0)) + "%"
        return val


    def hue_to_flt(self, val):
        h = int(val)
        if h == 360:
            return 0
        return h / 360.0

    def per_to_flt(self, val):
        return int(val[:-1])/100.0

    def tohex(self, r, g, b):
        return "#%02X%02X%02X" % (r, g, b)

    def _chans_to_col(self, chans): # -> col
        if chans[0][1] == "hue" and chans[1][1] == "saturation" and chans[2][1] == "value":
            (r, g, b) = colorsys.hsv_to_rgb(self.hue_to_flt(chans[0][0]), self.per_to_flt(chans[1][0]), self.per_to_flt(chans[2][0]))
            (vr, vg, vb) = (round(int(r*255)), round(int(g*255)), round(int(b*255)))
            return self.tohex(vr, vg, vb) + self._conv_val_chan(chans[3][0], chans[3][1])

        if chans[0][1] == "hue" and chans[1][1] == "saturation" and chans[2][1] == "lightness":
            (r, g, b) = colorsys.hls_to_rgb(self.hue_to_flt(chans[0][0]), self.per_to_flt(chans[2][0]), self.per_to_flt(chans[1][0]))
            (vr, vg, vb) = (round(int(r*255)), round(int(g*255)), round(int(b*255)))
            return self.tohex(vr, vg, vb) + self._conv_val_chan(chans[3][0], chans[3][1])


        res = "#"
        for c in chans:
            res += self._conv_val_chan(c[0], c[1])
        return res

    def _get_match_fmt(self, match): # -> fmt
        for fmt in self.conf.keys():
            if fmt in match.keys() and match[fmt] is not None:
                return fmt
        return None

    def _get_color_fmt(self, color): # -> fmt
        match = self._match_regex(self.regex, color)
        if match is not None:
            return self._get_match_fmt(match)
        return None

    def _get_chans(self, match, fmt): # -> chans
        types = self.conf[fmt]["types"]
        chans = ["R", "G", "B", "A"]
        res = []
        for i in range(0, 4):
            fmtch = fmt + chans[i]
            typ = types[i]
            if is_str(typ):
                res.append([match.get(fmtch, -1), typ])
            else:
                done = False
                for t in typ:
                    r = match.get(fmtch + t)
                    if r is not None:
                        res.append([r, t])
                        done = True
                        break
                if not done:
                    res.append([match.get(fmtch, -1), "empty"])

        for c in res:
            if c[0] is None:
                return None
        return res

    def _col_to_chans_match(self, col, fmt, match): # -> chans
        types_orig = self.conf[fmt]["types"]

        # easy way: choose the first channel type
        # TODO: better way!
        chs = ["R", "G", "B", "A"]
        types = []
        for i in range(0, len(types_orig)):
            to = types_orig[i]
            if is_str(to):
                types.append(to)
            else:
                fmtch = fmt + chs[i]
                done = False
                for t in types_orig[i]:
                    if match.get(fmtch + t, -1) is not None:
                        done = True
                        types.append(t)
                        break
                if not done:
                    types.append(t)

        chans = [[col[1:3], types[0]], [col[3:5], types[1]], [col[5:7], types[2]]]
        if types[3] != "empty":
            chans.append([col[7:9], types[3]])
        else:
            chans.append(["FF", types[3]])

        if chans[0][1] == "hue" and chans[1][1] == "saturation" and chans[2][1] == "value":
            (nh, ns, nv) = colorsys.rgb_to_hsv(int(chans[0][0], 16)/255.0, int(chans[1][0], 16)/255.0, int(chans[2][0], 16)/255.0)
            return (str(int(nh * 360)), str(int(ns * 100)) + '%', str(int(nv * 100)) + '%')

        if chans[0][1] == "hue" and chans[1][1] == "saturation" and chans[2][1] == "lightness":
            (nh, nv, ns) = colorsys.rgb_to_hls(int(chans[0][0], 16)/255.0, int(chans[1][0], 16)/255.0, int(chans[2][0], 16)/255.0)
            return (str(int(nh * 360)), str(int(ns * 100)) + '%', str(int(nv * 100)) + '%')

        for c in chans:
            c[0] = self._conv_val_chan_back(c[0], c[1])
        return chans

    def _get_color_fmt_chans(self, color): # -> fmt, chans
        match = self._match_regex(self.regex, color)
        if match is not None:
            for fmt in self.conf.keys():
                if fmt in match.keys() and match[fmt] is not None:
                    chans = self._get_chans(match, fmt)
                    if chans is None:
                        return None, None
                    return fmt, chans
        return None, None

    def _get_color_fmt_col(self, color): # -> fmt, col
        fmt, chans = self._get_color_fmt_chans(color)
        if fmt is None:
            return None, None
        return fmt, self._chans_to_col(chans)

    def _get_color_chans(self, color, fmt): # -> chans
        match = self._match_regex(self.conf[fmt]["regex"], color)
        if match is not None:
            return self._get_chans(match, fmt)
        return None

    def _get_color_col(self, color, fmt): # -> col
        chans = self._get_color_chans(color, fmt)
        if chans is None:
            return None
        return self._chans_to_col(chans)

    def get_color_fmt_col(self, color, fmt=None): # -> fmt, col
        if fmt is None:
            return fmt, self._get_color_fmt_col(color)
        else:
            return fmt, self._get_color_col(color, fmt)

    def get_col_color(self, col, fmt, example): # -> color
        if fmt == "sharp8":
            return col
        m = self._get_regex(self.conf[fmt]["regex"]).search(example)
        if m:
            chans = self._col_to_chans_match(col, fmt, m.groupdict())
            chs = ["R", "G", "B", "A"]
            offset = 0
            for i in range(0, 4):
                fmtch = fmt + chs[i]
                start = m.start(fmtch)
                end = m.end(fmtch)
                example = example[:start + offset] + chans[i][0] + example[end + offset:]
                offset += len(chans[i][0]) - (end - start)
            return example
        return None

    def append_text_reg_fmt_col(self, text, offset, res): # -> [(reg, fmt, col)]
        m = self.regex.search(text)
        while m:
            match = m.groupdict()
            fmt = self._get_match_fmt(match)
            if fmt is not None:
                chans = self._get_chans(match, fmt)
                if chans is not None:
                    res.append((sublime.Region(offset + m.start(), offset + m.end()), fmt, self._chans_to_col(chans)));
            m = self.regex.search(text, m.end())
        return res

    def get_text_reg_fmt_col(self, text, offset): # -> [(reg, fmt, col)]
        return self.append_text_reg_fmt_col(text, offset, [])

    def get_view_reg_fmt_col(self, view, region=None): # -> [(reg, fmt, col)]
        if region is None:
            region = sublime.Region(0, view.size())
        return self.get_text_reg_fmt_col(view.substr(region), region.begin())

    def find_text_reg_fmt_col(self, text, offset, reg_in): # -> (reg, fmt, col)
        m = self.regex.search(text)
        while m:
            if offset + m.start() <= reg_in.begin() and offset + m.end() >= reg_in.end():
                match = m.groupdict()
                fmt = self._get_match_fmt(match)
                if fmt is not None:
                    chans = self._get_chans(match, fmt)
                    if chans is not None:
                        return sublime.Region(offset + m.start(), offset + m.end()), fmt, self._chans_to_col(chans)
            m = self.regex.search(text, m.end())
        return None, None, None

    def find_view_reg_fmt_col(self, view, region, reg_in): # -> (reg, fmt, col)
        return self.find_text_reg_fmt_col(view.substr(region), region.begin(), reg_in)


# the class for searching for colors in a region
class ColorFinder:
    conv = ColorConverter()

    names = ""
    for k in list(colors.names_to_hex.keys()):
        names += k + "|"
    names_regex = re.compile("\\b(" + names[:-1] + ")\\b")

    # if the @region is in some text, that represents color, return new region, containing that color text and parsed color value in #RRGGBBAA format
    def get_color(self, view, region, variables): # -> (reg, col)
        reg, fmt, col = self.find_color(view, region, variables)
        if reg is None:
            return None, None
        return reg, col

    # get all colors from region
    def get_colors(self, view, variables, region=None): # -> [(reg, col)]
        regs = self.find_colors(view, variables, region)
        res = []
        for (reg, _, col) in regs:
            res.append((reg, col))
        return res

    # convert color with type @fmt to #RRGGBBAA
    def convert_color(self, color, variables, fmt=None): # -> col
        chans = None
        if fmt is None:
            fmt, chans = self.get_fmt(color, variables)
            if fmt is None:
                return None

        if fmt == "@named":
            return colors.names_to_hex[color]
        elif fmt.startswith("@var-"):
            return variables[color]["col"]

        if chans is None:
            chans = self.conv._get_color_chans(color, fmt)
            if chans is None:
                return None
        return self.conv._chans_to_col(chans)

    # convert color to #RRGGBBAA
    def convert_color_novars(self, color): # -> col
        fmt, chans = self.get_fmt_novars(color)
        if fmt is None:
            return None
        if fmt == "@named":
            return colors.names_to_hex[color]
        return self.conv._chans_to_col(chans)

    # convert color from #RRGGBBAA to different formats
    def convert_back_color(self, col, variables, fmt, example): # -> color
        if fmt == "@named":
            for name in colors.names_to_hex:
                if colors.names_to_hex[name] == col:
                    return name
            return col
        elif fmt.startswith("@var-"):
            for k in variables.keys():
                v = variables[k]
                if v["fmt"] == fmt and col == v["col"]:
                    return k
            return col
        return self.conv.get_col_color(col, fmt, example)

    def get_fmt(self, color, variables): # -> fmt, chans
        if color in colors.names_to_hex.keys():
            return "@named", None
        if color in variables.keys():
            return variables[color]["fmt"], None
        return self.conv._get_color_fmt_chans(color)

    def get_fmt_novars(self, color): # -> fmt, chans
        if color in colors.names_to_hex.keys():
            return "@named", None
        return self.conv._get_color_fmt_chans(color)

    def get_word_css(self, view, region):
        word = view.word(region)
        chars = "-"
        while view.substr(word.b) in chars and view.substr(word.b + 1).isalnum():
            word = sublime.Region(word.a, view.word(sublime.Region(word.b + 1, word.b + 1)).b)
        while view.substr(word.a - 1) in chars and view.substr(word.a - 2).isalnum():
            word = sublime.Region(view.word(sublime.Region(word.a - 2, word.a - 2)).a, word.b)
        if view.substr(word.a - 1) in "@$":
            word = sublime.Region(word.a - 1, word.b)
        return word

    # if the @region is in some text, that represents color, return new region, containing that color text and format type
    def find_color(self, view, region, variables): # -> (reg, fmt, col)
        word = self.get_word_css(view, region)
        word_str = view.substr(word)

        # TODO: nice regexes?
        if word_str in variables.keys():
            v = variables[word_str]
            return word, v["fmt"], v["col"]
        if word_str in colors.names_to_hex.keys():
            return word, "@named", colors.names_to_hex[word_str]

        line = view.line(region)
        return self.conv.find_text_reg_fmt_col(view.substr(line), line.begin(), region)

    # if the @region is in some text, that represents color, return new region, containing that color text and format type
    def find_color_var(self, view, region, variables): # -> (reg, fmt, col)
        word = self.get_word_css(view, region)
        word_str = view.substr(word)
        if word_str in variables.keys():
            v = variables[word_str]
            return word, v["fmt"], v["col"]
        return None, None, None

    vars_prepend = {
        "@var-less": "@",
        "@var-sass": "$",
        "@var-styl": "",
    }

    def vars_conv(self, fmt, val):
        if fmt == "@var-less" or fmt == "@var-sass":
            return val[1:]
        return val

    def find_all_name(self, regex, region, text, res):
        m = regex.search(text)
        while m:
            res.append((sublime.Region(region.a + m.start(), region.a + m.end()), "@named", colors.names_to_hex[text[m.start() : m.end()]]));
            m = regex.search(text, m.end())

    def find_all_vars(self, regex, region, text, fmt, variables, res):
        m = regex.search(text)
        while m:
            res.append((sublime.Region(region.a + m.start(), region.a + m.end()), fmt, variables[text[m.start() : m.end()]]["col"]));
            m = regex.search(text, m.end())

    # find all colors and their formats in the view region
    def find_colors(self, view, variables, region=None): # -> [(reg, fmt, col)]
        if region is None:
            region = sublime.Region(0, view.size())

        text = view.substr(region)
        res = []
        self.find_all_name(self.names_regex, region, text, res)
        if len(variables) != 0:
            var_regexs = {}
            varss = list(variables.keys())
            varss.sort(key=len, reverse=True)
            for v in varss:
                fmt = variables[v]["fmt"]
                v = self.vars_conv(fmt, v)
                if fmt not in var_regexs.keys():
                    var_regexs[fmt] = v
                else:
                    var_regexs[fmt] += "|"
                    var_regexs[fmt] += v
            for fmt in var_regexs.keys():
                regex = self.conv._get_regex(self.vars_prepend[fmt] + "\\b(" + var_regexs[fmt] + ")\\b")
                self.find_all_vars(regex, region, text, fmt, variables, res)

        return self.conv.append_text_reg_fmt_col(text, region.begin(), res)

    def set_conf(self, conf, channels):
        self.conv.set_conf(conf, channels)

### Main logic classes

def print_error(err):
    print(err.replace("\\n", "\n"))

# main program
class ColorHighlighterView:
    ch = None
    view = None
    disabled = True
    regions = []
    ha_regions = []

    def __init__(self, ch, view):
        self.ch = ch
        self.view = view

    def enable(self, val=True):
        self.disabled = not val
        if self.disabled:
            self.restore_scheme()

    def get_colors_sel(self):
        vs = self.ch.get_vars(self.view)
        res = []
        for s in self.view.sel():
            region, fmt, col = self.ch.color_finder.find_color(self.view, s, vs)
            if region is not None:
                res.append((region, fmt, col))
        return res

    def get_colors_sel_var(self):
        vs = self.ch.get_vars(self.view)
        res = []
        for s in self.view.sel():
            region, fmt, col = self.ch.color_finder.find_color_var(self.view, s, vs)
            if region is not None:
                res.append((region, fmt, col))
        return res

    def on_selection_modified(self):
        self.clear()
        if self.ch.style == "disabled":
            return

        vs = self.ch.get_vars(self.view)

        flags = self.ch.flags
        i = 0
        cols = []
        for s in self.view.sel():
            region, col = self.ch.color_finder.get_color(self.view, s, vs)
            if region is None:
                continue

            cols.append(col)
            i += 1
            st = "mon_CH_" + str(i)
            if self.ch.style != "none":
                self.regions.append(st)
                self.view.add_regions(st, [region], region_name(col), "", flags)
            if self.ch.icons:
                self.regions.append(st + "-ico")
                self.view.add_regions(st + "-ico", [region], region_name(col) + "-ico", conv_path(self.ch.create_icon(col)), sublime.HIDDEN)

        scheme, f = self.ch.add_colors(cols)
        self.set_scheme(scheme, f)

    def on_activated(self):
        self.on_selection_modified()

        self.ha_clear()
        if self.ch.ha_style == "disabled":
            return

        vs = self.ch.get_vars(self.view)
        flags = self.ch.ha_flags
        cols = []
        i = 0
        for (reg, col) in self.ch.color_finder.get_colors(self.view, vs):
            cols.append(col)
            i += 1
            st = "mon_CH_ALL_" + str(i)
            if self.ch.ha_style != "none":
                self.ha_regions.append(st)
                self.view.add_regions(st, [reg], region_name(col), "", flags)
            if self.ch.ha_icons:
                self.ha_regions.append(st + "-ico")
                self.view.add_regions(st + "-ico", [reg], region_name(col) + "-ico", conv_path(self.ch.create_icon(col)), sublime.HIDDEN)

        scheme, f = self.ch.add_colors(cols)
        self.set_scheme(scheme, f)

    def on_close(self):
        self.restore_scheme()

    def on_settings_change(self):
        cs = self.view.settings().get("color_scheme")

    def set_scheme(self, val, force=False):
        if force or self.view.settings().get("color_scheme") != val:
            self.view.settings().set("color_scheme", conv_path(val))

    def restore_scheme(self):
        self.set_scheme(self.ch.color_scheme)
        self.clear()
        self.ha_clear()

    def clear(self):
        for reg in self.regions:
            self.view.erase_regions(reg)
        self.regions = []

    def ha_clear(self):
        for reg in self.ha_regions:
            self.view.erase_regions(reg)
        self.ha_regions = []

def on_line_less(fname, line, i, res):
    if line[0] != "@":
        return

    var, col, pos = extract_less_sass_name_val(line)
    if var != None:
        res[var] = {"text": col, "file": fname, "line": i, "pos": pos, "fmt": "@var-less"}

def on_line_sass(fname, line, i, res):
    if line[0] != "$":
        return

    var, col, pos = extract_less_sass_name_val(line)
    if var != None:
        res[var] = {"text": col, "file": fname, "line": i, "pos": pos, "fmt": "@var-sass"}

def on_line_styl(fname, line, i, res):
    var, col, pos = extract_styl_name_val(line)
    if var != None:
        res[var] = {"text": col, "file": fname, "line": i, "pos": pos, "fmt": "@var-styl"}

def extract_import(line):
    l = len(line)
    i = len("@import")
    while i < l and line[i] not in "'\"":
        i += 1
    i += 1
    start = i
    if start >= l:
        return None

    while i < l and line[i] not in "'\"":
        i += 1
    end = i
    if end >= l:
        return None

    return line[start:end]

def extract_less_sass_name_val(line):
    pos = line.find(":")
    if pos == -1:
        return None, None, None

    var = line[:pos].rstrip()
    col = line[pos+1:-1].strip()
    return var, col, line.find(col)

def extract_styl_name_val(line):
    pos = line.find("=")
    if pos == -1:
        return None, None, None

    var = line[:pos].strip()
    if var == "":
        return None, None, None
    for c in var:
        if not c.isalpha() and c != "-" and c != "_":
            return None, None, None
    col = line[pos+1:].strip()
    return var, col, line.find(col)

# main program
class ColorHighlighter:
    settings = None
    is_disabled = True
    style = None
    ha_style = None
    flags = None
    ha_flags = None
    color_scheme = None
    icons = None
    ha_icons = None

    views = {}
    color_finder = None

    color_schemes = {}

    started = False

    def __init__(self):
        self.settings = Settings(self)
        for wnd in sublime.windows():
            for v in wnd.views():
                self.add_view(v)

        self.color_finder = ColorFinder()
        self.settings.on_ch_settings_change(True)
        self.settings.on_prefs_settings_change(True)
        self.started = True

    def enable(self, val=True):
        self.is_disabled = not val
        if self.is_disabled:
            self.unload()
        else:
            if self.started:
                self.reset_scheme()
            self.redraw()
            self.ha_redraw()

    def set_style(self, val):
        self.style = val
        self.flags = self.get_regions_flags(self.style)
        self.redraw()

    def set_ha_style(self, val):
        self.ha_style = val
        self.ha_flags = self.get_regions_flags(self.ha_style)
        self.ha_redraw()

    def valid_fname(self, fname):
        if self.settings.get("file_exts") == "all":
            return True
        if fname is None or fname == "":
            return True
        return os.path.splitext(fname)[1] in self.settings.get("file_exts")

    def set_exts(self, val):
        for k in self.views:
            v = self.views[k]
            v.enable(self.valid_fname(v.view.file_name()))

    def redraw(self):
        if not self.started:
            return
        for k in self.views:
            v = self.views[k]
            v.on_selection_modified()

    def ha_redraw(self):
        if not self.started:
            return
        for k in self.views:
            v = self.views[k]
            v.on_activated()

    def set_icons(self, val):
        self.icons = val
        self.redraw()

    def set_ha_icons(self, val):
        self.ha_icons = val
        self.ha_redraw()

    def set_scheme(self, val):
        self.color_scheme = val
        if val not in self.color_schemes.keys():
            self.color_schemes[val] = HtmlGen(val)
        self.reset_scheme()

    def reset_scheme(self):
        scheme = self.scheme_name()
        for k in self.views:
            v = self.views[k]
            v.set_scheme(scheme)

    def add_colors(self, cols):
        gen = self.color_schemes[self.color_scheme]
        for col in cols:
            gen.add_color(col)
        res = gen.flush()
        return gen.scheme_name(), res

    def add_view(self, view):
        v = ColorHighlighterView(self, view)
        v.enable(self.valid_fname(view.file_name()))
        if self.started:
            v.set_scheme(self.scheme_name())
        self.views[view.id()] = v
        return v

    def scheme_name(self):
        if self.color_scheme in self.color_schemes.keys():
            return self.color_schemes[self.color_scheme].scheme_name()
        return self.color_scheme

    def disabled(self, view):
        if self.is_disabled:
            return True
        if view.id() not in self.views:
            return True
        return self.views[view.id()].disabled

    def get_regions_flags(self, style):
        if is_st3():
            if style == "default" or style == "filled":
                return sublime.DRAW_NO_OUTLINE
            if style == "outlined":
                return sublime.DRAW_NO_FILL
            if style == "underlined" or style == "underlined_solid":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SOLID_UNDERLINE
            elif style == "underlined_strippled":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_STIPPLED_UNDERLINE
            elif style == "underlined_squiggly":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SQUIGGLY_UNDERLINE
        else:
            if style == "default" or style == "filled":
                return 0
            if style == "outlined":
                return sublime.DRAW_OUTLINED

        return 0

    def on_new(self, view):
        v = self.add_view(view)
        # Need on_activate for ST2, it has an odd events order (activate, then load)
        if not is_st3():
            v.on_activated()

    def on_clone(self, view):
        v = self.add_view(view)
        # Need on_activate for ST2, it has an odd events order (activate, then load)
        if not is_st3():
            v.on_activated()

    def on_load(self, view):
        v = self.add_view(view)
        # Need on_activate for ST2, it has an odd events order (activate, then load)
        if not is_st3():
            v.on_activated()

    def on_close(self, view):
        if self.disabled(view):
            return

        self.views[view.id()].on_close()
        del(self.views[view.id()])

    def on_selection_modified(self, view):
        if self.disabled(view):
            return

        self.views[view.id()].on_selection_modified()

    def on_modified(self, view):
        if view.id() in self.vars_view_cache.keys():
            del(self.vars_view_cache[view.id()])

        fn = view.file_name()
        if fn is not None and fn in self.vars_file_cache.keys():
            del(self.vars_file_cache[fn])

    def on_post_save(self, view):
        self.on_activated(view)

    def on_activated(self, view):
        if self.disabled(view):
            return
        self.views[view.id()].on_activated()

    def unload(self):
        for k in self.views:
            v = self.views[k]
            v.restore_scheme()

    def get_colors_sel(self, view):
        if self.disabled(view):
            return []
        return self.views[view.id()].get_colors_sel()

    def get_colors_sel_var(self, view):
        if self.disabled(view):
            return []
        return self.views[view.id()].get_colors_sel_var()

    def create_icon(self, col):
        if sublime.platform() == "windows":
            fname = col[1:]
        else:
            fname = "%s.png" % col[1:]
        fpath = os.path.join(icons_path(), fname)
        fpath_full = os.path.join(icons_path(PAbsolute), fname)

        if os.path.exists(fpath_full):
            return fpath

        cmd =  self.settings.get("convert_util_path") + ' -type TrueColorMatte -channel RGBA -size 32x32 -alpha transparent xc:none -fill "%s" -draw "circle 15,16 8,10" png32:"%s"'
        popen = subprocess.Popen(cmd % (col, fpath_full), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _, err = popen.communicate()
        try:
            err = err.decode("utf-8")
        except UnicodeDecodeError as ex:
            err = str(ex)
        if err is not None and len(err) != 0:
            print_error("convert error:\n" + err)

        if os.path.exists(fpath_full): # might not...
            return fpath
        return ""

    # vars extract

    vars_file_cache = {}
    vars_view_cache = {}

    def parse_vars_text(self, text, in_fname, dirname, ext, cache):
        vs = {}
        files = []
        i = 0

        on_line = lambda fname, line, i, vs: 0
        if ext == ".less":
            on_line = on_line_less
        elif ext in [".sass", ".scss"]:
            on_line = on_line_sass
        elif ext == ".styl":
            on_line = on_line_styl

        for line in map(lambda s: s.strip(), text.split("\n")):
            i += 1
            if len(line) < 2:
                continue

            if line.startswith("@import"):
                fname = extract_import(line)
                if fname is not None:
                    if os.path.splitext(fname)[1] == "":
                        fname += ext
                    if not os.path.isabs(fname):
                        fname = os.path.normpath(os.path.join(dirname, fname))
                    files.append(fname)
                continue

            on_line(in_fname, line, i, vs)


        cache["vars"] = vs
        cache["files"] = files
        for f in files:
            self.parse_vars_file(f)

    def parse_vars_file(self, fname):
        if fname in self.vars_file_cache.keys():
            return
        if not os.path.exists(fname):
            return

        obj = {}
        self.vars_file_cache[fname] = obj
        self.parse_vars_text(read_file(fname), fname, os.path.dirname(fname), os.path.splitext(fname)[1], obj)

    def parse_vars_view(self, view):
        if view.id() in self.vars_view_cache.keys():
            return

        obj = {}
        self.vars_view_cache[view.id()] = obj
        self.parse_vars_text(view.substr(sublime.Region(0, view.size())), "@view:" + str(view.id()), "", "", obj)

    def _get_vars(self, obj, res):
        vs = obj["vars"]
        for k in vs.keys():
            res[k] = vs[k]

        fs = obj["files"]
        for f in fs:
            self.get_file_vars(f, res)

    def get_file_vars(self, fname, res):
        self._get_vars(self.vars_file_cache[fname], res)

    def get_view_vars(self, view, res):
        self._get_vars(self.vars_view_cache[view.id()], res)

    def get_vars(self, view):
        fn = view.file_name()
        if fn is not None:
            self.parse_vars_file(fn)
            res = {}
            self.get_file_vars(fn, res)
        else:
            self.parse_vars_view(view)
            res = {}
            self.get_view_vars(view, res)

        # map text to colors
        for k in res.keys():
            self.get_col(k, res)
        return res

    def get_col(self, key, variables):
        v = variables[key]
        if "col" in v.keys():
            return v["col"]

        color = v["text"]
        if color in variables.keys():
            v["col"] = self.get_col(color, variables)
        else:
            v["col"] = self.color_finder.convert_color_novars(color)
        return v["col"]

    def build_chan_regex(self, chstr, fmt, chan, channels): # -> str, list
        lst = chstr.split("|")
        if len(lst) == 1:
            return channels[chstr], chstr

        fmt = "(?P<" + fmt + chan + "%s>%s)|"
        res = ""
        for l in lst:
            res += fmt % (l, channels[l])
        return res[:-1], lst

    def fix_regexes(self, formats, channels):
        for fmt in formats.keys():
            val = formats[fmt]
            if "regex" not in val.keys():
                continue

            types = []
            s = val["regex"]
            pos = s.find("(?P<R>")
            if pos == -1:
                raise ValueError("Regex must contain R channel!")
            pos += len("(?P<R>")
            start = pos
            while s[pos] != ")":
               pos += 1
            chan = s[start:pos]
            chanrx, lst = self.build_chan_regex(chan, fmt, "R", channels)
            types.append(lst)
            s = s.replace("(?P<R>" + chan + ")", "(?P<" + fmt + "R>" + chanrx + ")")

            pos = s.find("(?P<G>")
            if pos == -1:
                raise ValueError("Regex must contain G channel!")
            pos += len("(?P<G>")
            start = pos
            while s[pos] != ")":
               pos += 1
            chan = s[start:pos]
            chanrx, lst = self.build_chan_regex(chan, fmt, "G", channels)
            types.append(lst)
            s = s.replace("(?P<G>" + chan + ")", "(?P<" + fmt + "G>" + chanrx + ")")

            pos = s.find("(?P<B>")
            if pos == -1:
                raise ValueError("Regex must contain B channel!")
            pos += len("(?P<B>")
            start = pos
            while s[pos] != ")":
               pos += 1
            chan = s[start:pos]
            chanrx, lst = self.build_chan_regex(chan, fmt, "B", channels)
            types.append(lst)
            s = s.replace("(?P<B>" + chan + ")", "(?P<" + fmt + "B>" + chanrx + ")")

            pos = s.find("(?P<A>")
            if pos == -1:
                types.append("empty")
            else:
                pos += len("(?P<A>")
                start = pos
                while s[pos] != ")":
                   pos += 1
                chan = s[start:pos]
                chanrx, lst = self.build_chan_regex(chan, fmt, "A", channels)
                types.append(lst)
                s = s.replace("(?P<A>" + chan + ")", "(?P<" + fmt + "A>" + chanrx + ")")
            val["regex"] = s
            val["types"] = types

    def set_formats(self, formats, channels):
        to_del = []
        for fmt in formats.keys():
            val = formats[fmt]
            if "disable" in val.keys():
                to_del.append(fmt)
        for fmt in to_del:
            del(formats[fmt])


        self.fix_regexes(formats, channels)
        self.order_formats(formats)
        for k in channels.keys():
            self.get_chan(k, channels, {})
        self.color_finder.set_conf(formats, channels)

    def get_chan(self, k, channels, doing):
        if k in doing.keys():
            raise ValueError("Reccurent dependencies!")

        doing[k] = True
        obj = channels[k]
        if obj not in channels.keys():
            del(doing[k])
            return
        self.get_chan(obj, channels, doing)
        channels[k] = channels[obj]
        del(doing[k])

    def order_formats(self, formats):
        deps = {
            "": {
                "deps": {}
            }
        }
        for k in formats.keys():
            obj = formats[k]
            if "regex" in obj.keys():
                deps[k] = {
                    "rlen": len(obj["regex"]),
                }
                if "after" in obj.keys():
                    ds = obj["after"]
                    if is_str(ds):
                        deps[k]["deps"] = {
                            ds: True,
                        }
                    else:
                        deps[k]["deps"] = {}
                        for d in ds:
                            deps[k]["deps"][d] = True

                deps[""]["deps"][k] = True

        self.get_deps("", deps, {})
        arr = []
        for k in deps.keys():
            if k != "":
                arr.append((k, deps[k]["rlen"], deps[k]["deps_arr"]))
        arr.sort(key=cmp_to_key(deps_order))
        i = 0
        for (k, _, _) in arr:
            formats[k]["order"] = i
            i += 1

    def get_deps(self, k, deps, doing):
        if k in doing.keys():
            raise ValueError("Reccurent dependencies!")

        doing[k] = True
        obj = deps[k]
        if "deps_arr" in obj.keys():
            del(doing[k])
            return

        if "deps" not in obj.keys():
            obj["deps_arr"] = {}
            del(doing[k])
            return

        da = {}
        ds = obj["deps"]
        for d in ds.keys():
            da[d] = True
            self.get_deps(d, deps, doing)

        for d in ds:
            for v in deps[d]["deps_arr"]:
                da[v] = True
        obj["deps_arr"] = da
        del(doing[k])


def deps_order(a, b):
    keyA, rlenA, depsA = a
    keyB, rlenB, depsB = b
    if keyB in depsA.keys():
        return 1
    if keyA in depsB.keys():
        return -1

    if rlenA != rlenB:
        return rlenB - rlenA

    if keyB > keyA:
        return 1
    elif keyB < keyA:
        return -1
    return 0

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

color_highlighter = None

# main event listener
class ColorSelection(sublime_plugin.EventListener):
    def on_new(self, view):
        if color_highlighter is not None:
            color_highlighter.on_new(view)

    def on_clone(self, view):
        if color_highlighter is not None:
            color_highlighter.on_clone(view)

    def on_load(self, view):
        if color_highlighter is not None:
            color_highlighter.on_load(view)

    def on_close(self, view):
        if color_highlighter is not None:
            color_highlighter.on_close(view)

    def on_selection_modified(self, view):
        if color_highlighter is not None:
            color_highlighter.on_selection_modified(view)

    def on_modified(self, view):
        if color_highlighter is not None:
            color_highlighter.on_modified(view)

    def on_post_save(self, view):
        if color_highlighter is not None:
            color_highlighter.on_post_save(view)

    def on_activated(self, view):
        if color_highlighter is not None:
            color_highlighter.on_activated(view)

    def on_query_context(self, view, key, op, operand, match_all):
        if not key.startswith('color_highlighter.'):
            return None
        if color_highlighter is not None:
            return color_highlighter.settings.get("default_keybindings")


# commands

# command to change setting
class ChSetSetting(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        color_highlighter.settings.set(args["setting"], args["value"])
        color_highlighter.settings.save()

    def is_visible(self, **args):
        setting = args["setting"]

        if setting == "default_keybindings":
            return args["value"] != color_highlighter.settings.get(setting)

        if setting == "enabled":
            return args["value"] != (not color_highlighter.is_disabled)

        if is_st3():
            if setting in ["style", "ha_style"]:
                return True
            if setting == "icons":
                return args["value"] != color_highlighter.icons
            if setting == "ha_icons":
                return args["value"] != color_highlighter.ha_icons
        else:
            if setting in ["style", "ha_style"]:
                return args["value"] in ["disabled", "none", "default", "filled", "outlined"]
            if setting in ["ha_icons", "icons"]:
                return False
        return False

# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        color_highlighter.unload()

class ChReplaceColor(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        print("ChReplaceColor:", args)
        vs = color_highlighter.get_vars(self.view)
        offset = 0
        for val in args["words"].split("\t"):
            reg, fmt, col = self.parse_word(val)
            new_col = color_highlighter.color_finder.convert_back_color(col, vs, fmt, self.view.substr(reg))
            if new_col is None:
                continue
            self.view.replace(edit, sublime.Region(offset + reg.a, offset + reg.b), new_col)
            offset += len(new_col) - (reg.b - reg.a)

    def parse_word(self, s):
        pos = s.find(")")
        reg = s[2:pos].split(",")
        rest = s[pos+1:-1].split(",")
        return (sublime.Region(int(reg[0]), int(reg[1])), rest[1].strip()[1:-1], rest[2].strip()[1:-1])

class ColorCommand(sublime_plugin.TextCommand):
    words = []
    vs = None

    def clear(self):
        self.words = []
        self.vs = None

    def is_enabled(self):
        self.words = color_highlighter.get_colors_sel(self.view)
        return len(self.words) != 0

class ColorPickerCommand(ColorCommand):
    output = None

    def _do_run(self):
        col = self.words[0][2][1:]
        popen = subprocess.Popen([color_picker_user_path(PAbsolute), col], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = popen.communicate()
        self.output = out.decode("utf-8")
        err = err.decode("utf-8")
        if err is not None and len(err) != 0:
            print_error("Color Picker error:\n" + err)

    if is_st3():
        def run(self, edit):
            run_async(lambda: self.do_run())

        def do_run(self):
            self._do_run()
            self.call_impl()
    else:
        def run(self, edit):
            run_async(lambda: self._do_run())
            sublime.set_timeout(lambda: self.do_change_col(), 100)

        def do_change_col(self):
            output = self.output
            if output is None:
                sublime.set_timeout(lambda: self.do_change_col(), 100)
                return
            self.call_impl()

    def call_impl(self):
        if self.output is not None and len(self.output) == 9 and self.output != 'CANCEL':
            self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], x[1], self.output)), self.words))})
        self.output = None

class BaseColorConvertCommand(ColorCommand):
    def do_run(self, new_fmt):
        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

class ColorConvertCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt, _ = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        panel = self.view.window().show_input_panel("Format: ", fmt, self.do_run, None, self.clear)
        panel.sel().add(sublime.Region(0, panel.size()))

class ColorConvertNextCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt, _ = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        formats = list(filter(lambda f, fmt=fmt: f == fmt or (not f.startswith("@var-")), color_highlighter.settings.get("formats").keys()))
        new_fmt = formats[0]
        i = 0
        for f in formats:
            if f == fmt:
                if i < len(formats) - 1:
                    new_fmt = formats[i + 1]
                break
            i += 1

        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

class ColorConvertPrevCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt, _ = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        formats = list(filter(lambda f, fmt=fmt: f == fmt or (not f.startswith("@var-")), color_highlighter.settings.get("formats").keys()))
        new_fmt = formats[len(formats) - 1]
        i = 0
        for f in formats:
            if f == fmt:
                if i > 0:
                    new_fmt = formats[i - 1]
                break
            i += 1

        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

class GoToVarDefinitionCommand(ColorCommand):
    def run(self, edit):
        reg, _, _ = self.words[0]
        self.vs = color_highlighter.get_vars(self.view)
        obj = self.vs[self.view.substr(reg)]
        view = self.view.window().open_file(obj["file"] + ":%d:%d" % (obj["line"], obj["pos"] + 1), sublime.ENCODED_POSITION|sublime.TRANSIENT)
        self.clear()

    def is_enabled(self):
        self.words = color_highlighter.get_colors_sel_var(self.view)
        return len(self.words) != 0 and self.words[0][1].startswith("@var-")

# initialize all the stuff
def plugin_loaded():
    # Create folders
    create_if_not_exists(data_path(PAbsolute))
    create_if_not_exists(os.path.join(data_path(PAbsolute), os.path.dirname(color_picker_file())))
    create_if_not_exists(icons_path(PAbsolute))
    create_if_not_exists(themes_path(PAbsolute))

    # Setup CP binary
    chflags = stat.S_IXUSR|stat.S_IXGRP|stat.S_IRUSR|stat.S_IRUSR|stat.S_IWUSR|stat.S_IWGRP
    cpupath = color_picker_user_path(PAbsolute)
    if not os.path.exists(cpupath):
        if is_st3():
            with codecs.open(cpupath, "wb") as f:
                f.write(sublime.load_binary_resource(conv_path(color_picker_path())))
        else:
            shutil.copy(color_picker_path(PAbsolute), cpupath)
        os.chmod(cpupath, chflags)

    global color_highlighter
    color_highlighter = ColorHighlighter()

# unload all the stuff
def plugin_unloaded():
    if color_highlighter is not None:
        color_highlighter.unload()

# ST2 support. Maby need set_timeout?
if not is_st3():
    def plugin_loaded_wait():
        if sublime.load_settings(pref_fname).get("color_scheme") != None:
            plugin_loaded()
        else:
            sublime.set_timeout(plugin_loaded_wait, 100)

    plugin_loaded_wait()
