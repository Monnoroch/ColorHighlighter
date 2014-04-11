# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import stat
import re
import colorsys
import subprocess
import threading

try:
    import colors
except ImportError:
    colors = __import__("Color Highlighter", fromlist=["colors"]).colors

version = "6.0.4"

hex_letters = "0123456789ABCDEF"
settings_file = "ColorHighlighter.sublime-settings"


# errors helper

def print_error(err):
    print(err.replace("\\n", "\n"))


# files helpers

def write_file(fl, s):
    f = open(fl, "w")
    f.write(s)
    f.close()

def write_bin_file(fl, s):
    f = open(fl, "wb")
    f.write(s)
    f.close()

def read_file(fl):
    f = open(fl, "r")
    res = f.read()
    f.close()
    return res


# platform helpers

def get_version():
    return int(sublime.version())


def get_platform():
    plat = sublime.platform()
    if plat == "windows":
        plat = "win"
    return plat

def get_ext():
    plat = get_platform()
    if plat == "win":
        return plat + ".exe"
    return plat + "_" + sublime.arch()


# async helpers

if get_version() < 3000:
    class RunAsync(threading.Thread):
        def __init__(self, cb):
            self.cb = cb
            threading.Thread.__init__(self)

        def run(self):
            self.cb()

    def run_async(cb):
        RunAsync(cb).start()

else:
    def run_async(cb):
        sublime.set_timeout_async(cb, 0)


# regex helpers

def conv_from_rgb(col):
    vals = col[4:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]))

def conv_to_rgb(col):
    if col[-2:] == "FF":
        return "rgb(%d,%d,%d)" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16))
    else:
        return "rgba(%da,%d,%d,%d)" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_from_rgbad(col):
    vals = col[5:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]), int(vals[3]))

def conv_to_rgbad(col):
    return "rgba(%d,%d,%d,%d)" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_from_rgbaf(col):
    vals = list(map(lambda s: s.strip(), col[5:-1].split(",")))
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]), int(float(vals[3]) * 255))

def conv_to_rgbaf(col):
    return "rgba(%d,%d,%d,%f)" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16)/255.0)

def conv_from_hsv(col):
    vals = col[4:-1].split(",")
    return tohexhsv(int(vals[0]), int(vals[1]), int(vals[2]))

def conv_to_hsv(col):
    if col[-2:] == "FF":
        (r, g, b) = (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16))
        return "hsv(%d,%d,%d)" % rgb_to_hsv(r, g, b)
    else:
        (r, g, b, a) = (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))
        return "hsva(%d,%d,%d,%d)" % rgb_to_hsv(r, g, b, a)

def conv_from_hsvad(col):
    vals = col[5:-1].split(",")
    return tohexhsv(int(vals[0]), int(vals[1]), int(vals[2]), int(vals[3]))

def conv_to_hsvad(col):
    (r, g, b, a) = (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))
    return "hsva(%d,%d,%d,%d)" % rgb_to_hsv(r, g, b, a)

def conv_from_hsvaf(col):
    vals = list(map(lambda s: s.strip(), col[5:-1].split(",")))
    return tohexhsv(int(vals[0]), int(vals[1]), int(vals[2]), int(float(vals[3]) * 255))

def conv_to_hsvaf(col):
    (r, g, b, a) = (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16)/255.0)
    return "hsva(%d,%d,%d,%f)" % rgb_to_hsv(r, g, b, a)


def conv_from_array_rgb(col):
    vals = col[1:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]))

def conv_to_array_rgb(col):
    if col[:-2] == "FF":
        return "[%d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16))
    else:
        return "[%d, %d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_from_array_rgbad(col):
    vals = col[1:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]), int(vals[3]))

def conv_to_array_rgbad(col):
    return "[%d, %d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_to_array_rgb(col):
    if col[:-2] == "FF":
        return "[%d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16))
    else:
        return "[%d, %d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_from_array_rgbad(col):
    vals = col[1:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]), int(vals[3]))

def conv_to_array_rgbad(col):
    return "[%d, %d, %d, %d]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))

def conv_from_array_rgbaf(col):
    vals = col[1:-1].split(",")
    return tohex(int(vals[0]), int(vals[1]), int(vals[2]), int(float(vals[3]) * 255))

def conv_to_array_rgbaf(col):
    return "[%d, %d, %d, %f]" % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16)/255.0)

def conv_from_hex3(col):
    col = col.upper()
    return "#" + col[1] * 2 + col[2] * 2 + col[3] * 2 + "FF"

def conv_to_hex3(col):
    col = col.upper()
    if col[1] == col[2] and col[3] == col[4] and col[5] == col[6] and col[-2:] == "FF":
        return "#%s%s%s" % (col[1], col[3], col[5])
    return col

def conv_from_hex4(col):
    col = col.upper()
    return "#" + col[1] * 2 + col[2] * 2 + col[3] * 2 + col[4] * 2

def conv_to_hex4(col):
    col = col.upper()
    if col[1] == col[2] and col[3] == col[4] and col[5] == col[6] and col[7] == col[8]:
        return "#%s%s%s%s" % (col[1], col[3], col[5], col[7])
    return col

def conv_from_hex6(col):
    return col.upper() + "FF"

def conv_to_hex6(col):
    col = col.upper()
    if col[-2:] == "FF":
        return col[:-2]
    return col

def conv_from_hex8(col):
    return col.upper()

def conv_to_hex8(col):
    return col.upper()

color_fmts_data = {
    "#3": {
        "r_str": "[#][0-9a-fA-F]{3}",
        "to_hex": conv_from_hex3,
        "from_hex": conv_to_hex3
    },
    "#4": {
        "r_str": "[#][0-9a-fA-F]{4}",
        "to_hex": conv_from_hex4,
        "from_hex": conv_to_hex4
    },
    "#6": {
        "r_str": "[#][0-9a-fA-F]{6}",
        "to_hex": conv_from_hex6,
        "from_hex": conv_to_hex6
    },
    "#8": {
        "r_str": "[#][0-9a-fA-F]{8}",
        "to_hex": conv_from_hex8,
        "from_hex": conv_to_hex8
    },
    "rgb": {
        "r_str": "[r][g][b][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[)]",
        "to_hex": conv_from_rgb,
        "from_hex": conv_to_rgb
    },
    "rgbad": {
        "r_str": "[r][g][b][a][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[)]",
        "to_hex": conv_from_rgbad,
        "from_hex": conv_to_rgbad
    },
    "rgbaf": {
        "r_str": "[r][g][b][a][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*[0|1]?[\.]\d+[ ]*[)]",
        "to_hex": conv_from_rgbaf,
        "from_hex": conv_to_rgbaf
    },
    "hsv": {
        "r_str": "[h][s][v][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[)]",
        "to_hex": conv_from_hsv,
        "from_hex": conv_to_hsv
    },
    "hsvad": {
        "r_str": "[h][s][v][a][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[)]",
        "to_hex": conv_from_hsvad,
        "from_hex": conv_to_hsvad
    },
    "hsvaf": {
        "r_str": "[h][s][v][a][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*[0|1]?[\.]\d+[ ]*[)]",
        "to_hex": conv_from_hsvaf,
        "from_hex": conv_to_hsvaf
    },
    "array_rgb": {
        "r_str": "[\[][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[\]]",
        "to_hex": conv_from_array_rgb,
        "from_hex": conv_to_array_rgb
    },
    "array_rgbad": {
        "r_str": "[\[][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[\]]",
        "to_hex": conv_from_array_rgbad,
        "from_hex": conv_to_array_rgbad
    },
    "array_rgbaf": {
        "r_str": "[\[][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*[0|1]?[\.]\d+[ ]*[\]]",
        "to_hex": conv_from_array_rgbaf,
        "from_hex": conv_to_array_rgbaf
    }
}
regex_order = ["#8", "#6", "#4", "#3"]
for k in color_fmts_data.keys():
    if k not in regex_order:
        regex_order.append(k)

def get_all_colors_rstrs():
    res = ""
    for k in regex_order:
        res += "(?:%s)|" % color_fmts_data[k]["r_str"]
    return res[:-1]

color_fmts_data["all"] = {
    "r_str": "(%s)" % get_all_colors_rstrs(),
    "to_hex": None
}

for k in color_fmts_data.keys():
    color_fmts_data[k]["regex"] = re.compile(color_fmts_data[k]["r_str"])


def find_all(regex, text):
    res = []
    m = regex.search(text)
    while m:
        res.append((m.start(), m.end()))
        m = regex.search(text, m.end())
    return res

# colors helpers

def tohex(r, g, b, a=None):
    if a is None:
        a = 255
    return "#%02X%02X%02X%02X" % (r, g, b, a)
    
def tohexhsv(h, s, v, a=None):
    (r, g, b) = colorsys.hsv_to_rgb(h/255.0, s/255.0, v/255.0)
    return tohex(int(r*255), int(g*255), int(b*255), a)

def rgb_to_hsv(r, g, b, a=None):
    (h, s, v) = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    if a is None:
        return (int(h*255), int(s*255), int(v*255))
    else:
        return (int(h*255), int(s*255), int(v*255), a)

def hsv_to_rgb(h, s, v, a=None):
    (r, g, b) = colorsys.hsv_to_rgb(h/255.0, s/255.0, v/255.0)
    if a is None:
        return (int(r*255), int(g*255), int(b*255))
    else:
        return (int(r*255), int(g*255), int(b*255), a)

def get_cont_col(col):
    (h, s, v) = hsv_to_rgb(int(col[1:3],16), int(col[3:5],16), int(col[5:7],16))
    v1 = v * (s - 1) + 1
    s1 = 0
    if abs(v1) > 1e-10:
        s1 = v * s / v1
    (r, g, b) = colorsys.hsv_to_rgb(h >= 0.5 and h - 0.5 or h + 0.5, s1, v1)
    return tohex(int(r * 255), int(g * 255), int(b * 255)) # true complementary


def get_format(col):
    if col is None or len(col) == 0:
        return None
    if colors.names_to_hex.get(col):
        return "named"
    for k in regex_order:
        if color_fmts_data[k]["regex"].search(col):
            return k
    return None

def conv_to_format(base, col):
    base = base.strip()
    fmt = get_format(base)
    if fmt is None:
        return None

    if fmt == "named":
        for k in colors.names_to_hex.keys():
            if colors.names_to_hex[k] == col:
                return k
        return col

    return color_fmts_data[fmt]["from_hex"](col)

def hex_col_conv(col):
    if col[0] != "#":
        return None
    col = col.upper()

    l = len(col)
    for c in col[1:]:
        if c not in hex_letters:
            return None
    if l == 4:
        return "#" + col[1]*2 + col[2]*2 + col[3]*2 + "FF"
    if l == 5:
        return "#" + col[1]*2 + col[2]*2 + col[3]*2 + col[4]*2
    elif l == 7:
        return col + "FF"
    elif l == 9:
        return col
    return None

def name_to_hex(col, col_vars):
    if col is None or len(col) == 0:
        return None

    res = hex_col_conv(col)
    if res is not None:
        return res

    res = colors.names_to_hex.get(col)
    if res is not None:
        return name_to_hex(res, col_vars)

    if col_vars is None:
        return None
    return name_to_hex(col_vars.get(col), col_vars)

def isInColor(view, sel, col_vars, array_format):
    b = sel.begin()
    if b != sel.end():
        return None, None, None

    word = view.word(b)
    # sass/less variable
    if view.substr(word.begin() - 1) in ["@", "$"]:
        word1 = sublime.Region(word.begin() - 1, word.end())
        res = name_to_hex(view.substr(word1), col_vars)
        if res is not None:
            return word1, res, True
        return None, None, None
    # less variable interpolation
    elif view.substr(word.begin() - 1) == "{" and view.substr(word.begin() - 2) == "@" and view.substr(word.end()) == "}":
        word1 = sublime.Region(word.begin() - 2, word.end() + 1)
        res = name_to_hex("@" + view.substr(word), col_vars)
        if res is not None:
            return word1, res, True
        return None, None, None
    # just color
    elif view.substr(word.begin() - 1) in [" ", ":"]:
        res = name_to_hex(view.substr(word), col_vars)
        if res is not None:
            return word, res, False

    line = view.line(b)
    beg = line.begin()
    matches = find_all(color_fmts_data["all"]["regex"], view.substr(line))
    for s, e in matches:
        s += beg
        e += beg
        if b < s or b > e:
            continue
        for k in regex_order:
            if not array_format and k.startswith("array"):
                continue
            word = sublime.Region(s, e)
            col = view.substr(word)
            if k[0] == "#" and view.substr(word.begin() - 1) not in [" ", ":"]:
                continue
            if color_fmts_data[k]["regex"].search(col):
                return word, color_fmts_data[k]["to_hex"](col), False

    return None, None, None


# regions helper

def region_name(s):
    return "mcol_" + s[1:]

# color scheme helpers

def set_scheme(view, cs):
    sets = view.settings()
    if sets.get("color_scheme") != cs:
        sets.set("color_scheme", cs)
        return True
    return False

def is_vidget(self, view):
    w = view.window()
    if w is None:
        return False
    grp, _ = w.get_view_index(view)
    return grp != -1

def to_abs_cs_path(cs):
    return os.path.join(sublime.packages_path(), os.path.normpath(cs[len("Packages/"):]))

# html generator for color scheme

class HtmlGen:
    colors = []
    color_scheme = None
    fake_scheme = None
    need_upd = False
    string = ""
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
        self.fake_scheme = "Packages/User/Color Highlighter/" + cs.split('/')[-1]

    def load(self, htmlGen):
        self.colors += htmlGen.colors[:]
        self.string += htmlGen.string
        self.need_upd = htmlGen.string != ""

    def add_color(self, col):
        if col in self.colors:
            return
        self.colors.append(col)
        cont = get_cont_col(col)
        self.string += self.gen_string % (region_name(col), col, cont, cont)
        self.need_upd = True

    def update_view(self, view):
        if not os.path.exists(to_abs_cs_path(self.fake_scheme)):
            return set_scheme(view, self.color_scheme)
        else:
            return set_scheme(view, self.fake_scheme)

    def update(self):
        if not self.need_upd:
            return False

        if get_version() >= 3000:
            cont = sublime.load_resource(self.color_scheme)
        else:
            cont = read_file(to_abs_cs_path(self.color_scheme)).decode("utf-8")
        n = cont.find("<array>") + len("<array>")
        cont = cont[:n] + self.string + cont[n:]
        write_bin_file(to_abs_cs_path(self.fake_scheme), cont.encode("utf-8"))

        self.need_upd = False
        return True

    def restore(self):
        self.colors = []
        self.string = ""
        path = to_abs_cs_path(self.fake_scheme)
        if os.path.exists(path):
            os.remove(path)


# less variables parsers

def extract_sass_name_val(line):
    pos = line.find(":")
    if pos == -1:
        return None, None

    var = line[:pos].rstrip()
    col = line[pos+1:].lstrip()
    return var, col

def _extract_sass_fname(name):
    if not name.endswith(".sass"):
        name += ".sass"
    name = os.path.join(os.path.dirname(nm), name)
    if not os.path.exists(name):
        return None
    return name

def _extract_scss_fname(name):
    if not name.endswith(".scss"):
        name += ".scss"
    name = os.path.join(os.path.dirname(nm), name)
    if not os.path.exists(name):
        return None
    return name

def extract_sass_fname(view, line):
    nm = view.file_name()
    if nm is None:
        return None

    line = line[8:-1].strip()[1:-1]
    name = _extract_sass_fname(line)
    if name is None:
        name = _extract_scss_fname(line)
    return name

def find_sass_vars(view, text, cols):
    for line in map(lambda s: s.strip(), text.split("\n")):
        if len(line) < 2 or line[0] != "$":
            continue

        if line.startswith("@import"):
            name = extract_sass_fname(view, line)
            if name != None:
                find_sass_vars(view, read_file(name), cols)
            continue

        var, col = extract_sass_name_val(line)
        if var != None:
            cols[var] = col

def extract_less_name_val(line):
    pos = line.find(":")
    if pos == -1:
        return None, None

    var = line[:pos].rstrip()
    col = line[pos+1:-1].strip()
    return var, col

def extract_less_fname(view, line):
    nm = view.file_name()
    if nm is None:
        return None
    name = line[8:-1].strip()[1:-1]
    if not name.endswith(".less"):
        name += ".less"
    name = os.path.join(os.path.dirname(nm), name)
    if not os.path.exists(name):
        return None
    return name

def find_less_vars(view, text, cols):
    for line in map(lambda s: s.strip(), text.split("\n")):
        if len(line) < 2 or line[0] != "@":
            continue

        if line.startswith("@import"):
            name = extract_less_fname(view, line)
            if name != None:
                find_less_vars(view, read_file(name), cols)
            continue

        var, col = extract_less_name_val(line)
        if var != None:
            cols[var] = col


def get_doc_text(view):
    return view.substr(sublime.Region(0, view.size())) # TODO: better way to select all document


def parse_stylesheet(view, colors):
    nm = view.file_name()
    if nm is None:
        return

    name, ext = os.path.splitext(nm)
    text = get_doc_text(view)
    if ext in [".sass", ".scss"]:
        find_sass_vars(view, text, colors)
    elif ext in [".less"]:
        find_less_vars(view, text, colors)


# event handler, main logic

class Logic:
    views = {}
    settings = {}


    # html generator caching fabric
    color_schemes = {}
    def get_html_gen(self, cs):
        if cs not in self.color_schemes.keys():
            self.color_schemes[cs] = HtmlGen(cs)
        return self.color_schemes[cs]

    # settings change handlers

    def on_g_settings_change(self):
        sets = sublime.load_settings("Preferences.sublime-settings")
        cs = sets.get("color_scheme")
        curr_cs = self.settings["color_scheme"]
        if cs != curr_cs:
            for k in self.views.keys():
                vo = self.views[k]
                if vo["settings"]["color_scheme"] == curr_cs:
                    self.set_scheme_view(vo, cs)
        self.settings["color_scheme"] = cs

    def on_settings_change_view(self, view):
        cs = view.settings().get("color_scheme")
        if not cs.startswith("Packages/User/Color Highlighter/"):
            self.set_scheme_view(self.views[view.id()], cs)

    def on_ch_settings_change(self):
        sets = sublime.load_settings(settings_file)

        enabled = sets.get("enabled")
        if enabled != self.settings["enabled"]:
            self.settings["enabled"] = enabled
            if not enabled and not self.settings["highlight_all"]:
                self.do_disable()
            else:
                self.do_enable()
            self.on_selection_modified(sublime.active_window().active_view())

        style = sets.get("style")
        if style != self.settings["style"]:
            self.settings["style"] = style
            self.on_selection_modified(sublime.active_window().active_view())

        highlight_all = sets.get("highlight_all")
        if highlight_all != self.settings["highlight_all"]:
            self.settings["highlight_all"] = highlight_all
            if not highlight_all and not self.settings["enabled"]:
                self.do_disable()
            else:
                self.do_enable()
            self.on_activated(sublime.active_window().active_view())

        ha_style = sets.get("ha_style")
        if ha_style != self.settings["ha_style"]:
            self.settings["ha_style"] = ha_style
            self.on_activated(sublime.active_window().active_view())

    def do_disable(self):
         for k in self.views.keys():
            vo = self.views[k]
            view = vo["view"]
            if set_scheme(view, vo["settings"]["color_scheme"]):
                self.on_selection_modified(view)

    def do_enable(self):
         for k in self.views.keys():
            vo = self.views[k]
            view = vo["view"]
            if vo["html_gen"].update_view(view):
                self.on_selection_modified(view)

    def set_scheme_view(self, view_obj, cs):
        vsets = view_obj["settings"]
        if vsets["color_scheme"] == cs:
            return
        vsets["color_scheme"] = cs
        htmlGen = self.get_html_gen(cs)
        htmlGen.load(view_obj["html_gen"])
        view_obj["html_gen"] = htmlGen

        view = view_obj["view"]
        if htmlGen.update():
            if htmlGen.update_view(view):
                self.on_selection_modified(view)

    # initers

    inited = False
    def init(self):
        if self.inited:
            return

        sets = sublime.load_settings(settings_file)

        self.settings["enabled"] = sets.get("enabled")
        self.settings["highlight_all"] = sets.get("highlight_all")
        self.settings["style"] = sets.get("style")
        self.settings["ha_style"] = sets.get("ha_style")

        sets.clear_on_change("ColorHighlighter")
        sets.add_on_change("ColorHighlighter", lambda: self.on_ch_settings_change())

        sets = sublime.load_settings("Preferences.sublime-settings")

        self.settings["color_scheme"] = sets.get("color_scheme")

        sets.clear_on_change("ColorHighlighter")
        sets.add_on_change("ColorHighlighter", lambda: self.on_g_settings_change())

        self.inited = True

    def init_view(self, view):
        if view.id() in self.views.keys():
            return True
        sets = view.settings()
        cs = sets.get("color_scheme")
        if cs is None:
            return False # ST2 hack
        htmlGen = self.get_html_gen(cs)
        self.views[view.id()] = {"view": view, "vars": {}, "regions": [], "hl_all_regions": [], "settings" : {"color_scheme": cs}, "html_gen": htmlGen}
        view.settings().add_on_change("ColorHighlighter", lambda v=view: self.on_settings_change_view(v))
        htmlGen.update_view(view)
        return True

    def on_new(self, view):
        self.init()
        self.init_view(view)

    def on_clone(self, view):
        self.on_new(view)

    def on_load(self, view):
        self.on_new(view)

    def on_close(self, view):
        if view.id() in self.views.keys():
            del(self.views[view.id()])

    def on_pre_save(self, view):
        self.on_activated(view)

    def on_activated(self, view):
        self.init()
        if not self.init_view(view):
            return

        view_obj = self.views[view.id()]

        view_obj["vars"] = {}
        self.clean_hl_all_regions(view)

        parse_stylesheet(view, view_obj["vars"])
        if self.settings["highlight_all"]:
            htmlGen = view_obj["html_gen"]
            regs = view_obj["hl_all_regions"]

            res = self.find_all(color_fmts_data["all"]["regex"], get_doc_text(view), view, htmlGen, view_obj["vars"])
            if htmlGen.update():
                htmlGen.update_view(view)

            i = 0
            flags = self.get_regions_ha_flags()
            for s, e, col in res:
                i += 1
                st = "mon_CH_ALL_" + str(i)
                regs.append(st)
                view.add_regions(st, [sublime.Region(s, e)], region_name(col), "", flags)

        self.on_selection_modified(view)

    def on_selection_modified(self, view):
        self.init()
        if not self.init_view(view):
            return

        self.clean_regions(view)
        if self.settings["enabled"]:
            view_obj = self.views[view.id()]

            htmlGen = view_obj["html_gen"]
            words = self._get_words(view, htmlGen, view_obj["vars"])
            if htmlGen.update():
                htmlGen.update_view(view)

            i = 0
            regs = view_obj["regions"]
            flags = self.get_regions_flags()
            for w, col, _ in words:
                i += 1
                s = "mon_CH_" + str(i)
                regs.append(s)
                view.add_regions(s, [w], region_name(col), "", flags)


    def find_all(self, regex, text, view, htmlGen, col_vars):
        res = []
        array_format = self.get_arr_fmt(view)
        m = regex.search(text)
        while m:
            wd, col, var = isInColor(view, sublime.Region(m.start()+1, m.start()+1), col_vars, array_format=array_format)
            if col is not None:
                res.append((wd.begin(), wd.end(), col))
                htmlGen.add_color(col)
            m = regex.search(text, m.end())
        return res

    def _get_regions_flags(self, style):
        if style == "default" or style == "filled":
            return 0
        if get_version() < 3000:
            if style == "outlined":
                return sublime.DRAW_OUTLINED
        else:
            if style == "outlined":
                return sublime.DRAW_NO_FILL
            if style == "underlined" or style == "underlined_solid":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SOLID_UNDERLINE
            elif style == "underlined_strippled":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_STIPPLED_UNDERLINE
            elif style == "underlined_squiggly":
                return sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SQUIGGLY_UNDERLINE
        return 0

    def get_regions_flags(self):
        return self._get_regions_flags(self.settings["style"])

    def get_regions_ha_flags(self):
        return self._get_regions_flags(self.settings["ha_style"])

    def clean_regions(self, view):
        view_obj = self.views[view.id()]
        for s in view_obj["regions"]:
            view.erase_regions(s)
        view_obj["regions"] = []

    def clean_hl_all_regions(self, view):
        view_obj = self.views[view.id()]
        for s in view_obj["hl_all_regions"]:
            view.erase_regions(s)
        view_obj["hl_all_regions"] = []

    def get_arr_fmt(self, view):
        array_format = False
        nm = view.file_name()
        if nm is not None:
            name, ext = os.path.splitext(nm)
            if ext in [".sublime-theme"]:
                array_format = True
        return array_format

    def _get_words(self, view, htmlGen, col_vars):
        words = []
        array_format = self.get_arr_fmt(view)
        for s in view.sel():
            wd, col, var = isInColor(view, s, col_vars, array_format=array_format)
            if col is None:
                continue
            htmlGen.add_color(col)
            words.append((wd, col, var))
        return words

    def get_words(self, view):
        self.init()
        self.init_view(view)
        view_obj = self.views[view.id()]
        view_obj["vars"] = {}
        return self._get_words(view, view_obj["html_gen"], view_obj["vars"])

    def restore(self, files=True):
        self.init()
        for k in self.views.keys():
            vo = self.views[k]
            set_scheme(vo["view"], vo["settings"]["color_scheme"])
        if files:
            for hg in self.color_schemes.keys():
                self.color_schemes[hg].restore()

global_logic = Logic()


# commands

class ChSetSetting(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        sublime.load_settings(settings_file).set(args["setting"], args["value"])
        sublime.save_settings(settings_file)

    def is_visible(self, **args):
        setting = args["setting"]
        global_logic.init()
        if setting == "style":
            if get_version() >= 3000:
                return True
            return args["value"] in ["default", "filled", "outlined"]
        elif setting == "ha_style":
            if get_version() >= 3000:
                return True
            return args["value"] in ["default", "filled", "outlined"]
        elif setting == "enabled":
            return args["value"] != global_logic.settings["enabled"]
        elif setting == "highlight_all":
            return args["value"] != global_logic.settings["highlight_all"]
        return False



# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global_logic.restore()


class ColorPickerCommandImpl(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        m = color_fmts_data["#8"]["regex"].search(args["output"])
        output = m and args["output"][m.start():m.end()] or None
        if output is None or len(output) == 0 or output == args["col"]:
            return

        for val in args["words"].split("\t"):
            w, c, v = self.parse(val)
            if w is None or v:
                continue
            new_col = conv_to_format(self.view.substr(w), output)
            if new_col is None:
                continue
            self.view.replace(edit, w, new_col)

    def parse(self, s):
        pos = s.find(")")
        reg = s[2:pos].split(",")
        rest = s[pos+1:].split(",")
        return (sublime.Region(int(reg[0]), int(reg[1])), rest[1].strip(), rest[2].strip() == "True")


class ColorPickerCommand(sublime_plugin.TextCommand):
    words = []
    col = None
    ext = get_ext()
    output = None

    def _do_run(self):
        path = os.path.join(sublime.packages_path(), "Color Highlighter", "ColorPicker_" + self.ext)
        popen = subprocess.Popen([path, self.col[1:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = popen.communicate()
        self.output = out.decode("utf-8")
        err = err.decode("utf-8")
        if err is not None and len(err) != 0:
            print_error("Color Picker error:\n" + err)


    if get_version() < 3000:
        def run(self, edit):
            run_async(lambda: self._do_run())
            sublime.set_timeout(lambda: self.do_change_col(), 100)

        def do_change_col(self):
            output = self.output
            if output is None:
                sublime.set_timeout(lambda: self.do_change_col(), 100)
                return
            self.call_impl()

    else:
        def run(self, edit):
            run_async(lambda: self.do_run())

        def do_run(self):
            self._do_run()
            self.call_impl()


    def call_impl(self):
        if self.output is not None and len(self.output) == 9 and self.output != 'CANCEL':
            self.view.run_command("color_picker_command_impl", {"output": self.output, "col": self.col, "words": "\t".join(list(map(str, self.words)))})
        self.output = None


    def is_enabled(self):
        self.words = global_logic.get_words(self.view)
        wd = None
        self.col = None
        for w, c, v in self.words:
            if w is not None and not v:
                wd, self.col = w, c
                break
        return wd is not None and self.col is not None


# event listener

class ColorSelection(sublime_plugin.EventListener):
    def on_new(self, view):
        global_logic.on_new(view)

    def on_clone(self, view):
        global_logic.on_clone(view)

    def on_close(self, view):
        global_logic.on_close(view)

    def on_selection_modified(self, view):
        global_logic.on_selection_modified(view)

    def on_activated(self, view):
        global_logic.on_activated(view)

    def on_pre_save(self, view):
        global_logic.on_pre_save(view)


# initers and deiniters

def restore_broken_schemes():
    g_cs = sublime.load_settings("Preferences.sublime-settings").get("color_scheme")
    for w in sublime.windows():
        for v in w.views():
            if not os.path.exists(to_abs_cs_path(v.settings().get("color_scheme"))):
                v.settings().set("color_scheme", g_cs)

def plugin_loaded():
    # Create themes folder
    path = os.path.join(sublime.packages_path(), "User", "Color Highlighter")
    if not os.path.exists(path):
        os.makedirs(path)

    # Create plugin folder
    path = os.path.join(sublime.packages_path(), "Color Highlighter")
    if not os.path.exists(path):
        os.mkdir(path)

    # Copy binary
    bin = "ColorPicker_" + get_ext()
    fpath = os.path.join(path, bin)
    if get_version() >= 3000:
        if not os.path.exists(fpath):
            data = sublime.load_binary_resource('/'.join(["Packages", "Color Highlighter", bin]))
            if len(data) != 0:
                write_bin_file(fpath, data)
                os.chmod(fpath, stat.S_IXUSR|stat.S_IXGRP)
    else:
        if os.path.exists(fpath):
            os.chmod(fpath, stat.S_IXUSR|stat.S_IXGRP)

    # restore themes
    restore_broken_schemes()


# TODO: remove
def plugin_unloaded():
    global_logic.restore(files=False)

if get_version() < 3000:
    plugin_loaded()
