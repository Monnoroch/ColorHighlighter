
# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import stat
import re
import colorsys
import subprocess
import threading
import shutil

try:
    import colors
except ImportError:
    colors = __import__("Color Highlighter", fromlist=["colors"]).colors


version = "6.5.4"

hex_letters = "0123456789ABCDEF"
settings_file = "ColorHighlighter.sublime-settings"
low_letters = "abcdefghijklmnopqrstuvwxyz"


data_path = "Packages/User/Color Highlighter/"
icons_path = data_path + "icons/"
themes_path = data_path + "themes/"

full_data_path = None
full_icons_path = None
full_themes_path = None

# errors helper

def print_error(err):
    print(err.replace("\\n", "\n"))

# files helpers

def write_file(fl, s):
    with open(fl, "w") as f:
        f.write(s)

def write_bin_file(fl, s):
    with open(fl, "wb") as f:
        f.write(s)

def read_file(fl):
    with open(fl, "r") as f:
        return f.read()


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

def per_to_flt(val):
    return int(val[:-1])/100.0

def hue_to_flt(val):
    h = int(val)
    if h == 360:
        return 0
    return h / 360.0

def flt_to_int(val):
    return int(float(val)*255)

def tohex_hsva(k, h, s, v, a=None):
    (vh, vs, vv) = (hue_to_flt(h), per_to_flt(s), per_to_flt(v))
    if k.startswith("hsv"):
        (r, g, b) = colorsys.hsv_to_rgb(vh, vs, vv)
    else:
        (r, g, b) = colorsys.hls_to_rgb(vh, vv, vs)
    (vr, vg, vb) = (int(r*255), int(g*255), int(b*255))
    if a is None:
        return tohex(vr, vg, vb)
    else:
        return tohex(vr, vg, vb, flt_to_int(a))

def fromhex_hsva(k, col):
    (fr, fg, fb) = (int(col[1:3], 16)/255.0, int(col[3:5], 16)/255.0, int(col[5:7], 16)/255.0)
    if k.startswith("hsv"):
        (nh, ns, nv) = colorsys.rgb_to_hsv(fr, fg, fb)
    else:
        (nh, nv, ns) = colorsys.rgb_to_hls(fr, fg, fb)
    return (str(int(nh * 360)), str(int(ns * 100)) + '%', str(int(nv * 100)) + '%')


def hex_to_flt(h):
    return str(int(h, 16)/255.0)

def hex_to_int(h):
    return str(int(h, 16))


def conv_from_rgb_gen(k, col):
    (r, g, b) = color_fmts_data[k]["m_regex"].search(col).groups()
    return tohex(int(r), int(g), int(b))

def conv_to_rgb_gen(k, base, col):
    s = color_fmts_data[k]["m_regex"].search(base)
    (nr, ng, nb) = (hex_to_int(col[1:3]), hex_to_int(col[3:5]), hex_to_int(col[5:7]))
    if col.endswith("FF"):
        return base[:s.start(k[0])] + nr + base[s.end(k[0]):s.start(k[1])] + ng + base[s.end(k[1]):s.start(k[2])] + nb + base[s.end(k[2]):]
    else:
        na = hex_to_flt(col[7:9])
        return base[:s.start(k[0])].replace(k + "(", k + "a(") + nr + base[s.end(k[0]):s.start(k[1])] + ng + base[s.end(k[1]):s.start(k[2])] + nb + ", " + na + base[s.end(k[2]):]

def conv_from_rgba_gen(k, col):
    (r, g, b, a) = color_fmts_data[k]["m_regex"].search(col).groups()
    return tohex(int(r), int(g), int(b), flt_to_int(a))

def conv_to_rgba_gen(k, base, col):
    s = color_fmts_data[k]["m_regex"].search(base)
    (nr, ng, nb, na) = (hex_to_int(col[1:3]), hex_to_int(col[3:5]), hex_to_int(col[5:7]), hex_to_flt(col[7:9]))
    return base[:s.start(k[0])]+ nr + base[s.end(k[0]):s.start(k[1])] + ng + base[s.end(k[1]):s.start(k[2])] + nb + base[s.end(k[2]):s.start(k[3])] + na + base[s.end(k[3]):]

def conv_from_hsv_gen(k, col):
    (h, s, v) = color_fmts_data[k]["m_regex"].search(col).groups()
    return tohex_hsva(k, h, s, v)

def conv_to_hsv_gen(k, base, col):
    se = color_fmts_data[k]["m_regex"].search(base)
    (nh, ns, nv) = fromhex_hsva(k, col)
    if col.endswith("FF"):
        return base[:se.start(k[0])] + nh + base[se.end(k[0]):se.start(k[1])] + ns + base[se.end(k[1]):se.start(k[2])] + nv + base[se.end(k[2]):]
    else:
        na = hex_to_flt(col[7:9])
        return base[:se.start(k[0])].replace(k + "(", k + "a(") + nh + base[se.end(k[0]):se.start(k[1])] + ns + base[se.end(k[1]):se.start(k[2])] + nv + ", " + na + base[se.end(k[2]):]

def conv_from_hsva_gen(k, col):
    (h, s, v, a) = color_fmts_data[k]["m_regex"].search(col).groups()
    return tohex_hsva(k, h, s, v, a)

def conv_to_hsva_gen(k, base, col):
    se = color_fmts_data[k]["m_regex"].search(base)
    (nh, ns, nv) = fromhex_hsva(k, col)
    na =  hex_to_flt(col[7:9])
    return base[:se.start(k[0])]+ nh + base[se.end(k[0]):se.start(k[1])] + ns + base[se.end(k[1]):se.start(k[2])] + nv + base[se.end(k[2]):se.start(k[3])] + na + base[se.end(k[3]):]


def compress_hex4(col):
    if col[1] == col[2] and col[3] == col[4] and col[5] == col[6] and col[7] == col[8]:
        return "#%s%s%s%s" % (col[1], col[3], col[5], col[7])
    return col

def compress_hex(col):
    if col.endswith("FF"):
        if col[1] == col[2] and col[3] == col[4] and col[5] == col[6]:
            return "#%s%s%s" % (col[1], col[3], col[5])
        return col[:-2]
    return compress_hex4(col)


def conv_from_hex3(col):
    col = col.upper()
    return "#" + col[1] * 2 + col[2] * 2 + col[3] * 2 + "FF"

def conv_to_hex3(base, col):
    return compress_hex(col.upper())

def conv_from_hex4(col):
    col = col.upper()
    return "#" + col[1] * 2 + col[2] * 2 + col[3] * 2 + col[4] * 2

def conv_to_hex4(base, col):
    return compress_hex4(col.upper())

def conv_from_hex6(col):
    return col.upper() + "FF"

def conv_to_hex6(base, col):
    col = col.upper()
    if col[-2:] == "FF":
        return col[:-2]
    return col

def conv_from_hex8(col):
    return col.upper()

def conv_to_hex8(base, col):
    return col.upper()

def conv_from_named(col):
    res = colors.names_to_hex.get(col)
    if res is not None:
        return res
    return None

def conv_to_named_base(base, col):
    for k in colors.names_to_hex.keys():
        if colors.names_to_hex[k] == col:
            return k
    return None

def conv_to_named(base, col):
    b = conv_to_named_base(base, col)
    if b is not None:
        return b
    return col[:-2]

rgx_value_float = "(?:[0|1])|(?:[1][\.]?[0]*)|(?:[0]?[\.]\d*)"
rgx_value_int = "\d{1,3}"
rgx_value_per = "\d{1,3}[%]"
value_regex = "(?:%s)|(?:%s)|(?:%s)" % (rgx_value_int, rgx_value_float, rgx_value_per)
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
        "r_str": "[r][g][b][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_int, rgx_value_int),
        "m_str": "[r][g][b][(][ ]*(?P<r>%s)[ ]*[,][ ]*(?P<g>%s)[ ]*[,][ ]*(?P<b>%s)[ ]*[)]" % (rgx_value_int, rgx_value_int, rgx_value_int),
        "to_hex": lambda col: conv_from_rgb_gen("rgb", col),
        "from_hex": lambda base, col: conv_to_rgb_gen("rgb", base, col)
    },
    "rgba": {
        "r_str": "[r][g][b][a][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_int, rgx_value_int, rgx_value_float),
        "m_str": "[r][g][b][a][(][ ]*(?P<r>%s)[ ]*[,][ ]*(?P<g>%s)[ ]*[,][ ]*(?P<b>%s)[ ]*[,][ ]*(?P<a>%s)[ ]*[)]" % (rgx_value_int, rgx_value_int, rgx_value_int, rgx_value_float),
        "to_hex": lambda col: conv_from_rgba_gen("rgba", col),
        "from_hex": lambda base, col: conv_to_rgba_gen("rgba", base, col)
    },
    "hsv": {
        "r_str": "[h][s][v][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per),
        "m_str": "[h][s][v][(][ ]*(?P<h>%s)[ ]*[,][ ]*(?P<s>%s)[ ]*[,][ ]*(?P<v>%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per),
        "to_hex": lambda col: conv_from_hsv_gen("hsv", col),
        "from_hex": lambda base, col: conv_to_hsv_gen("hsv", base, col)
    },
    "hsva": {
        "r_str": "[h][s][v][a][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per, rgx_value_float),
        "m_str": "[h][s][v][a][(][ ]*(?P<h>%s)[ ]*[,][ ]*(?P<s>%s)[ ]*[,][ ]*(?P<v>%s)[ ]*[,][ ]*(?P<a>%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per, rgx_value_float),
        "to_hex": lambda col: conv_from_hsva_gen("hsva", col),
        "from_hex": lambda base, col: conv_to_hsva_gen("hsva", base, col)
    },
    "hsl": {
        "r_str": "[h][s][l][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per),
        "m_str": "[h][s][l][(][ ]*(?P<h>%s)[ ]*[,][ ]*(?P<s>%s)[ ]*[,][ ]*(?P<l>%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per),
        "to_hex": lambda col: conv_from_hsv_gen("hsl", col),
        "from_hex": lambda base, col: conv_to_hsv_gen("hsl", base, col)
    },
    "hsla": {
        "r_str": "[h][s][l][a][(][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per, rgx_value_float),
        "m_str": "[h][s][l][a][(][ ]*(?P<h>%s)[ ]*[,][ ]*(?P<s>%s)[ ]*[,][ ]*(?P<l>%s)[ ]*[,][ ]*(?P<a>%s)[ ]*[)]" % (rgx_value_int, rgx_value_per, rgx_value_per, rgx_value_float),
        "to_hex": lambda col: conv_from_hsva_gen("hsla", col),
        "from_hex": lambda base, col: conv_to_hsva_gen("hsla", base, col)
    },
    "rgb_array": {
        "r_str": "[\[][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[\]]" % (value_regex, value_regex, value_regex),
        "m_str": "[\[][ ]*(?P<r>%s)[ ]*[,][ ]*(?P<g>%s)[ ]*[,][ ]*(?P<b>%s)[ ]*[\]]" % (value_regex, value_regex, value_regex),
        "to_hex": lambda col: conv_from_rgb_gen("rgb_array", col),
        "from_hex": lambda base, col: conv_to_rgba_gen("rgb_array", base, col)
    },
    "rgba_array": {
        "r_str": "[\[][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[,][ ]*(?:%s)[ ]*[\]]" % (value_regex, value_regex, value_regex, value_regex),
        "m_str": "[\[][ ]*(?P<r>%s)[ ]*[,][ ]*(?P<g>%s)[ ]*[,][ ]*(?P<b>%s)[ ]*[,][ ]*(?P<a>%s)[ ]*[\]]" % (value_regex, value_regex, value_regex, value_regex),
        "to_hex": lambda col: conv_from_rgba_gen("rgba_array", col),
        "from_hex": lambda base, col: conv_to_rgba_gen("rgba_array", base, col)
    },
    "named": {
        "to_hex": conv_from_named,
        "from_hex": conv_to_named
    }
}

regex_order = ["#8", "#6", "#4", "#3"]
for k in color_fmts_data.keys():
    if k not in regex_order and "r_str" in color_fmts_data[k].keys():
        regex_order.append(k)

def get_all_colors_rstrs():
    res = ""
    for k in regex_order:
        if "r_str" in color_fmts_data[k].keys():
            res += "(?:%s)|" % color_fmts_data[k]["r_str"]
    return res[:-1]

color_fmts_data["all"] = {
    "r_str": "(%s)" % get_all_colors_rstrs(),
    "m_str": "",
    "to_hex": None
}

for k in color_fmts_data.keys():
    if "r_str" in color_fmts_data[k].keys():
        color_fmts_data[k]["regex"] = re.compile(color_fmts_data[k]["r_str"])
    if "m_str" in color_fmts_data[k].keys():
        color_fmts_data[k]["m_regex"] = re.compile(color_fmts_data[k]["m_str"])


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

def get_cont_col(col):
    (h, s, v) = colorsys.rgb_to_hsv(int(col[1:3],16)/255.0, int(col[3:5],16)/255.0, int(col[5:7],16)/255.0)
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
        b = conv_to_named_base("", col)
        if b is not None:
            return b
        return compress_hex4(col)
    return color_fmts_data[fmt]["from_hex"](base, col)

def convert_format(base, col):
    return conv_to_format(base, color_fmts_data[get_format(col)]["to_hex"](col))

def name_to_hex(col, col_vars):
    if col is None or len(col) == 0:
        return None

    res = colors.names_to_hex.get(col)
    if res is not None:
        return name_to_hex(res, col_vars)

    res = col_vars.get(col)
    if res is not None:
        return name_to_hex(res["col"], col_vars)

    fmt = get_format(col)
    if fmt is None:
        return None

    return color_fmts_data[fmt]["to_hex"](col)

def get_word(view, reg):
    beg = view.word(reg.begin()).begin()
    while view.substr(beg - 1) == "-":
        beg = view.word(beg - 2).begin()

    end = view.word(reg.end()).end()
    while view.substr(end) == "-":
        end = view.word(end + 1).end()

    return sublime.Region(beg, end)


bound_symbols = ["\n", "\t", " ", ";", ":", ",", "\'", "\"", ">", "<", "(", ")"]
def isInColor(view, sel, col_vars, array_format):
    b = sel.begin()
    if b != sel.end():
        return None, None, None

    word = get_word(view, sel)
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
    elif view.substr(word.begin() - 1) in [" ", ":" , "\"", "\'"]:
        res = name_to_hex(view.substr(word), col_vars)
        if res is not None:
            return word, res, False
    # styl variable
    else:
        word1 = sublime.Region(word.begin(), word.end())
        res = name_to_hex(view.substr(word1), col_vars)
        if res is not None:
            return word1, res, True

    line = view.line(b)
    beg = line.begin()
    matches = find_all(color_fmts_data["all"]["regex"], view.substr(line))
    for s, e in matches:
        s += beg
        e += beg
        if b < s or b > e:
            continue
        for k in regex_order:
            if not array_format and k.endswith("array"):
                continue
            word = sublime.Region(s, e)
            col = view.substr(word)
            if k[0] == "#" and (view.substr(word.begin() - 1) not in bound_symbols or view.substr(word.end()) not in bound_symbols):
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

def to_abs_cs_path(cs):
    return os.path.join(sublime.packages_path(), os.path.normpath(cs[len("Packages/"):]))

# html generator for color scheme

class HtmlGen:
    colors = None
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
        self.fake_scheme = themes_path + cs.split('/')[-1]
        self.colors = []

    def load(self, htmlGen):
        new_cols = [x for x in htmlGen.colors if x not in self.colors]
        for col in new_cols:
            cont = get_cont_col(col)
            self.string += self.gen_string % (region_name(col), col, cont, cont)
        self.colors += new_cols
        self.need_upd = len(new_cols) != 0

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

import_regex = re.compile("[\"|\''](?P<name>.*)[\"|\'']")

def extract_sass_name_val(line):
    pos = line.find(":")
    if pos == -1:
        return None, None, None

    var = line[:pos].rstrip()
    col = line[pos+1:-1].strip()
    return var, col, line.find(col)

def _extract_sass_fname(dirname, name, ext):
    if not name.endswith(ext):
        name += ext
    name = os.path.join(dirname, name)
    if not os.path.exists(name):
        return None
    return name

def extract_sass_fname(dirname, line):
    se = import_regex.search(line)
    if not se:
        return None
    name = line[se.start("name"):se.end("name")]
    res = _extract_sass_fname(dirname, name, ".sass")
    if res is None:
        res = _extract_sass_fname(dirname, name, ".scss")
    if res is None:
        name = "_" + line[se.start("name"):se.end("name")]
        res = _extract_sass_fname(dirname, name, ".sass")
    if res is None:
        res = _extract_sass_fname(dirname, name, ".scss")
    return res

def find_sass_vars(dirname, fname, text, cols):
    i = 0
    for line in map(lambda s: s.strip(), text.split("\n")):
        i += 1
        if len(line) < 2:
            continue

        if line.startswith("@import"):
            name = extract_sass_fname(dirname, line)
            if name != None:
                find_sass_vars(dirname, name, read_file(name), cols)
            continue

        if line[0] != "$":
            continue

        var, col, pos = extract_sass_name_val(line)
        if var != None:
            cols[var] = {"col": col, "file": fname, "line": i - 1, "pos": pos}


def extract_less_name_val(line):
    pos = line.find(":")
    if pos == -1:
        return None, None, None

    var = line[:pos].rstrip()
    col = line[pos+1:-1].strip()
    return var, col, line.find(col)

def extract_less_fname(dirname, line):
    se = import_regex.search(line)
    if not se:
        return None
    name = line[se.start("name"):se.end("name")]
    if not name.endswith(".less"):
        name += ".less"
    res = os.path.join(dirname, name)
    if not os.path.exists(res):
        return None
    return res

def find_less_vars(dirname, fname, text, cols):
    i = 0
    for line in map(lambda s: s.strip(), text.split("\n")):
        i += 1
        if len(line) < 2 or line[0] != "@":
            continue

        if line.startswith("@import"):
            name = extract_less_fname(dirname, line)
            if name != None:
                find_less_vars(dirname, name, read_file(name), cols)
            continue

        var, col, pos = extract_less_name_val(line)
        if var != None:
            cols[var] = {"col": col, "file": fname, "line": i, "pos": pos}


def extract_styl_fname(dirname, line):
    se = import_regex.search(line)
    if not se:
        return None
    name = line[se.start("name"):se.end("name")]
    if not name.endswith(".styl"):
        name += ".styl"
    res = os.path.join(dirname, name)
    if not os.path.exists(res):
        return None
    return res

def extract_styl_name_val(line):
    pos = line.find("=")
    if pos == -1:
        return None, None, None

    var = line[:pos].strip()
    col = line[pos+1:].strip()
    return var, col, line.find(col)

def find_styl_vars(dirname, fname, text, cols):
    i = 0
    for line in map(lambda s: s.strip(), text.split("\n")):
        i += 1
        if len(line) < 2:
            continue

        if line.startswith("@import"):
            name = extract_styl_fname(dirname, line)
            if name != None:
                find_styl_vars(dirname, name, read_file(name), cols)
            continue

        var, col, pos = extract_styl_name_val(line)
        if var != None:
            cols[var] = {"col": col, "file": fname, "line": i, "pos": pos}


def get_doc_text(view):
    return view.substr(sublime.Region(0, view.size())) # TODO: better way to select all document


def parse_stylesheet(view, colors):
    nm = view.file_name()
    if nm is None:
        return
    dirname = os.path.dirname(nm)

    name, ext = os.path.splitext(nm)
    text = get_doc_text(view)
    if ext in [".sass", ".scss"]:
        find_sass_vars(dirname, nm, text, colors)
    elif ext in [".less"]:
        find_less_vars(dirname, nm, text, colors)
    elif ext in [".styl"]:
        find_styl_vars(dirname, nm, text, colors)


def create_icon(col):
    fname = icons_path + "%s.png" % col[1:]
    full_name = os.path.join(full_icons_path, "%s.png" % col[1:])
    if os.path.exists(full_name):
        return fname
    cmd = sublime.load_settings(settings_file).get("convert_util_path") + ' -type TrueColorMatte -channel RGBA -size 32x32 -alpha transparent xc:none -fill "%s" -draw "circle 15,16 8,10" png32:"%s"'
    popen = subprocess.Popen(cmd % (col, full_name), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    _, err = popen.communicate()
    try:
        err = err.decode("utf-8")
    except UnicodeDecodeError as ex:
        err = str(ex)
    if err is not None and len(err) != 0:
        print_error("convert error:\n" + err)
    if os.path.exists(full_name):
        return fname
    return ""


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
        if cs == curr_cs:
            return
        for k in self.views.keys():
            vo = self.views[k]
            if vo["settings"]["color_scheme"] == curr_cs:
                self.set_scheme_view(vo, cs)
        self.settings["color_scheme"] = cs

    def on_settings_change_view(self, view):
        cs = view.settings().get("color_scheme")
        vo = self.views[view.id()]
        if vo["settings"]["color_scheme"] == cs:
            return
        if not cs.startswith(themes_path):
            self.set_scheme_view(vo, cs)

    def on_ch_settings_change(self):
        sets = sublime.load_settings(settings_file)

        enabled = sets.get("enabled")
        if enabled != self.settings["enabled"]:
            self.settings["enabled"] = enabled
            if not enabled:
                self.do_disable()
            else:
                self.do_enable()

        style = sets.get("style")
        if style != self.settings["style"]:
            self.settings["style"] = style
            self.on_selection_modified(sublime.active_window().active_view())

        ha_style = sets.get("ha_style")
        if ha_style != self.settings["ha_style"]:
            self.settings["ha_style"] = ha_style
            self.on_activated(sublime.active_window().active_view())

        icons_all = sets.get("icons_all")
        if icons_all != self.settings["icons_all"]:
            self.settings["icons_all"] = icons_all
            self.on_activated(sublime.active_window().active_view())

        icons = sets.get("icons")
        if icons != self.settings["icons"]:
            self.settings["icons"] = icons
            self.on_selection_modified(sublime.active_window().active_view())

        color_formats = sets.get("color_formats")
        if color_formats != self.settings["color_formats"]:
            self.settings["color_formats"] = color_formats
            self.settings["color_fmts"] = list(map(get_format, color_formats))

        file_exts = sets.get("file_exts")
        if file_exts != self.settings["file_exts"]:
            self.settings["file_exts"] = file_exts
            self.on_activated(sublime.active_window().active_view())
            self.on_selection_modified(sublime.active_window().active_view())

    def do_disable(self):
         for k in self.views.keys():
            vo = self.views[k]
            view = vo["view"]
            if set_scheme(view, vo["settings"]["color_scheme"]):
                self.on_activated(view)
                self.on_selection_modified(view)

    def do_enable(self):
         for k in self.views.keys():
            vo = self.views[k]
            view = vo["view"]
            if vo["html_gen"].update_view(view):
                self.on_activated(view)
                self.on_selection_modified(view)

    def set_scheme_view(self, view_obj, cs):
        view_obj["settings"]["color_scheme"] = cs
        htmlGen = self.get_html_gen(cs)
        htmlGen.load(view_obj["html_gen"])
        view_obj["html_gen"] = htmlGen

        view = view_obj["view"]
        htmlGen.update()
        htmlGen.update_view(view)

    # initers

    inited = False
    def init(self):
        if self.inited:
            return

        sets = sublime.load_settings(settings_file)
        if get_version() < 3000:
            if sets.get("ha_style").startswith("underlined"):
                sets.set("ha_style", "outlined")
            if sets.get("icons"):
                sets.set("icons", False)
            if sets.get("icons_all"):
                sets.set("icons_all", False)
            sublime.save_settings(settings_file)

        for k in ["enabled", "style", "ha_style", "icons_all", "icons", "color_formats", "file_exts"]:
            self.settings[k] = sets.get(k)

        self.settings["color_fmts"] = list(map(get_format, self.settings["color_formats"]))

        sets.clear_on_change("ColorHighlighter")
        sets.add_on_change("ColorHighlighter", lambda: self.on_ch_settings_change())

        sets = sublime.load_settings("Preferences.sublime-settings")

        self.settings["color_scheme"] = sets.get("color_scheme")

        sets.clear_on_change("ColorHighlighter")
        sets.add_on_change("ColorHighlighter", lambda: self.on_g_settings_change())

        self.inited = True

        for w in sublime.windows():
            for v in w.views():
                self.init_view(v)

    def init_view(self, view):
        if view.settings().get('is_widget'):
            return False
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
            view.settings().clear_on_change("ColorHighlighter")
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

        if not self.settings["enabled"] or not self.valid_fname(view.file_name()):
            return

        if self.settings["ha_style"] != "disabled":
            parse_stylesheet(view, view_obj["vars"])

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
                if self.settings["ha_style"] != "none":
                    regs.append(st)
                    view.add_regions(st, [sublime.Region(s, e)], region_name(col), "", flags)
                if self.settings["icons_all"]:
                    regs.append(st + "-ico")
                    view.add_regions(st + "-ico", [sublime.Region(s, e)], region_name(col) + "-ico", create_icon(col), sublime.HIDDEN)

        self.on_selection_modified(view)

    def valid_fname(self, fname):
        if self.settings["file_exts"] == "all":
            return True

        if fname is None or fname == "":
            return False

        (_, ext) = os.path.splitext(fname)
        return ext in self.settings["file_exts"]

    def on_selection_modified(self, view):
        self.init()
        if not self.init_view(view):
            return

        self.clean_regions(view)
        if not self.settings["enabled"] or not self.valid_fname(view.file_name()):
            return

        if self.settings["style"] != "disabled":
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
                st = "mon_CH_" + str(i)
                if self.settings["style"] != "none":
                    regs.append(st)
                    view.add_regions(st, [w], region_name(col), "", flags)
                if self.settings["icons"]:
                    regs.append(st + "-ico")
                    view.add_regions(st + "-ico", [w], region_name(col) + "-ico", create_icon(col), sublime.HIDDEN)


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

        varss = list(col_vars.keys())
        varss.sort(key=len, reverse=True)
        symbols = list(colors.names_to_hex.keys()) + varss
        tlen = len(text)
        for k in symbols:
            l = len(k)
            pos = 0
            ind = text.find(k, pos)
            while ind != -1:
                if (ind + l == tlen or text[ind + l] not in low_letters) and (ind == 0 or text[ind - 1] not in low_letters):
                    wd, col, var = isInColor(view, sublime.Region(ind+1, ind+1), col_vars, array_format=array_format)
                    if col is not None:
                        res.append((wd.begin(), wd.end(), col))
                        htmlGen.add_color(col)
                pos = ind + l
                ind = text.find(k, pos)
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
        return self._get_words(view, view_obj["html_gen"], view_obj["vars"])

    def restore(self, files=True):
        self.init()
        for k in self.views.keys():
            vo = self.views[k]
            set_scheme(vo["view"], vo["settings"]["color_scheme"])
        if files:
            for hg in self.color_schemes.keys():
                self.color_schemes[hg].restore()

    def remove_callbacks(self):
        for k in self.views.keys():
            self.views[k]["view"].settings().clear_on_change("ColorHighlighter")

        sublime.load_settings(settings_file).clear_on_change("ColorHighlighter")
        sublime.load_settings("Preferences.sublime-settings").clear_on_change("ColorHighlighter")

global_logic = Logic()


# commands

class ChSetSetting(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        sublime.load_settings(settings_file).set(args["setting"], args["value"])
        sublime.save_settings(settings_file)

    def is_visible(self, **args):
        setting = args["setting"]
        global_logic.init()

        if setting == "default_keybindings":
            return args["value"] != sublime.load_settings(settings_file).get(setting)

        if setting in ["enabled"]:
            return args["value"] != global_logic.settings[setting]

        if get_version() >= 3000:
            if setting in ["style", "ha_style"]:
                return True
            if setting in ["icons_all", "icons"]:
                return args["value"] != global_logic.settings[setting]
        else:
            if setting in ["style", "ha_style"]:
                return args["value"] in ["default", "filled", "outlined"]
            if setting in ["icons_all", "icons"]:
                return False
        return False



# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global_logic.restore()


def parse_word(s):
    pos = s.find(")")
    reg = s[2:pos].split(",")
    rest = s[pos+1:].split(",")
    return (sublime.Region(int(reg[0]), int(reg[1])), rest[1].strip(), rest[2].strip() == "True")


class ColorPickerCommandImpl(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        m = color_fmts_data["#8"]["regex"].search(args["output"])
        output = m and args["output"][m.start():m.end()] or None
        if output is None or len(output) == 0 or output == args["col"]:
            return

        for val in args["words"].split("\t"):
            w, c, v = parse_word(val)
            if w is None or v:
                continue
            new_col = conv_to_format(self.view.substr(w), output)
            if new_col is None:
                continue
            self.view.replace(edit, w, new_col)

class ColorPickerCommand(sublime_plugin.TextCommand):
    words = []
    col = None
    ext = get_ext()
    output = None

    def _do_run(self):
        path = os.path.join(full_data_path, "ColorPicker_" + self.ext)
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
        self.col = None
        for w, c, v in self.words:
            if w is not None and not v:
                _, self.col = w, c
                return True
        return False


def reg_to_str(reg):
    return "%d,%d" % (reg.begin(), reg.end())

def reg_from_str(st):
    w = st.split(",")
    return sublime.Region(int(w[0]), int(w[1]))

class ColorConvertCommandImpl(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        wd = reg_from_str(args["word"])
        new_col = convert_format(args["format"], self.view.substr(wd))
        if new_col is None:
            return
        self.view.replace(edit, wd, new_col)

class ColorConvertCommand(sublime_plugin.TextCommand):
    words = []
    wd = None

    formats = {
        "named": "white",
        "rgb": "rgb(255, 255, 255)",
        "rgba": "rgba(255, 255, 255, 1)",
        "hsv": "hsv(0, 0%, 100%)",
        "hsva": "hsva(0, 0%, 100%, 1)",
        "hsl": "hsl(0, 100%, 100%)",
        "hsla": "hsla(0, 100%, 100%, 1)"
    }

    def do_run(self, edit, fmt, txt):
        psfmt = self.formats.get(fmt)
        if psfmt is not None:
            fmt = psfmt
        if fmt != txt:
            for w, c, v in self.words:
                if w is None or v:
                    continue
                self.view.run_command("color_convert_command_impl", {"format": fmt, "word": reg_to_str(w)})
        self.clear()

    def clear(self):
        self.words = []
        self.wd = None

    def run(self, edit):
        txt = self.view.substr(self.wd)
        panel = self.view.window().show_input_panel("Format: ", txt, lambda fmt, e=edit, t=txt: self.do_run(e, fmt, t), None, self.clear)
        panel.sel().add(sublime.Region(0, panel.size()))

    def is_enabled(self):
        self.words = global_logic.get_words(self.view)
        self.wd = None
        for w, c, v in self.words:
            if w is not None and not v:
                self.wd, _ = w, c
                return True
        return False

class ColorConvertNextCommand(sublime_plugin.TextCommand):
    words = []

    def clear(self):
        self.words = []

    def run(self, edit):
        samples = global_logic.settings["color_fmts"]
        l = len(samples)

        for w, c, v in self.words:
            if w is None or v:
                continue
            fmt = get_format(self.view.substr(w))
            val = -1
            for i in range(0, l):
                if fmt == samples[i]:
                    val = i + 1
                    break
            if val == l:
                val = 0
            if val == -1:
                continue
            self.view.run_command("color_convert_command_impl", {"format": global_logic.settings["color_formats"][val], "word": reg_to_str(w)})
        self.clear()

    def is_enabled(self):
        self.words = global_logic.get_words(self.view)
        for w, c, v in self.words:
            if w is not None and not v:
                return True
        return False


class ColorConvertPrevCommand(sublime_plugin.TextCommand):
    words = []

    def clear(self):
        self.words = []

    def run(self, edit):
        samples = global_logic.settings["color_fmts"]
        l = len(samples)

        for w, c, v in self.words:
            if w is None or v:
                continue
            fmt = get_format(self.view.substr(w))
            val = -1
            for i in range(0, l):
                if fmt == samples[i]:
                    val = i - 1
                    break
            if val == -1:
                val = l - 1
            if val == -1:
                continue
            self.view.run_command("color_convert_command_impl", {"format": global_logic.settings["color_formats"][val], "word": reg_to_str(w)})
        self.clear()

    def is_enabled(self):
        self.words = global_logic.get_words(self.view)
        for w, c, v in self.words:
            if w is not None and not v:
                return True
        return False

class GoToVarDefinitionCommand(sublime_plugin.TextCommand):
    words = []

    def clear(self):
        self.words = []

    def run(self, edit):
        w, c, v = self.words[0]
        var = global_logic.views[self.view.id()]["vars"][self.view.substr(w)]
        wnd = self.view.window()
        view = wnd.open_file(var["file"] + ":%d:%d" % (var["line"], var["pos"] + 1), sublime.ENCODED_POSITION|sublime.TRANSIENT)

    def is_enabled(self):
        self.words = global_logic.get_words(self.view)
        for w, c, v in self.words:
            if w is not None and v:
                return True
        return False

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

    def on_query_context(self, view, key, op, operand, match_all):
        if not key.startswith('color_highlighter.'):
            return None
        return sublime.load_settings(settings_file).get("default_keybindings")



# initers and deiniters

def restore_broken_schemes():
    g_cs = sublime.load_settings("Preferences.sublime-settings").get("color_scheme")
    for w in sublime.windows():
        for v in w.views():
            if not os.path.exists(to_abs_cs_path(v.settings().get("color_scheme"))):
                set_scheme(v, g_cs)

def plugin_loaded():
    global full_data_path, full_icons_path, full_themes_path
    full_data_path = os.path.join(sublime.packages_path()[:-len("Packages")], os.path.normpath(data_path))
    full_icons_path = os.path.join(full_data_path, "icons")
    full_themes_path = os.path.join(full_data_path, "themes")
    # Create folders
    if not os.path.exists(full_data_path):
        os.mkdir(full_data_path)
    if not os.path.exists(full_icons_path):
        os.mkdir(full_icons_path)
    if not os.path.exists(full_themes_path):
        os.mkdir(full_themes_path)

    # Copy binary
    binary = "ColorPicker_" + get_ext()
    chflags = stat.S_IXUSR|stat.S_IXGRP|stat.S_IRUSR|stat.S_IRUSR|stat.S_IWUSR|stat.S_IWGRP
    fpath = os.path.join(full_data_path, binary)
    if get_version() >= 3000:
        if not os.path.exists(fpath):
            data = sublime.load_binary_resource('/'.join(["Packages", "Color Highlighter", "ColorPicker", binary]))
            if len(data) != 0:
                write_bin_file(fpath, data)
                os.chmod(fpath, chflags)
    else:
        if not os.path.exists(fpath):
            shutil.copy(os.path.join(sublime.packages_path(), "Color Highlighter", "ColorPicker", binary), fpath)
            os.chmod(fpath, chflags)

    # restore themes
    restore_broken_schemes()


# TODO: remove
def plugin_unloaded():
    global_logic.restore(files=False)
    global_logic.remove_callbacks()

if get_version() < 3000:
    plugin_loaded()
