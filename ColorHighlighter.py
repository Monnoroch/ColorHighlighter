import sublime, sublime_plugin
import os
import re
import colorsys

try:
    import colors
except ImportError:
    colors = __import__("Color Highlighter", fromlist=["colors"]).colors

version = "4.0"

def write_file(fl, s):
    f = open(fl, "w")
    f.write(s)
    f.close()

def read_file(fl):
    f = open(fl, "r")
    res = f.read()
    f.close()
    return res


def tohex(r, g, b):
    return "#%02X%02X%02XFF" % (r, g, b)

def tohexa(r, g, b, a):
    return "#%02X%02X%02X%02X" % (r, g, b, a)


regex_rgb = re.compile("[r][g][b][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[)]")
regex_rgba = re.compile("[r][g][b][a][(][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*(?:\d{1,3}|[0]?\.\d+)[ ]*[)]")
regex_array = re.compile("[\[][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}[ ]*[,][ ]*\d{1,3}(?:[ ]*|[,][ ]*(?:\d{1,3}|[0]?\.\d+)[ ]*)[\]]")


colors_by_view = {}

def conv_to_hex(view, col):
    if col is None or len(col) == 0:
        return None

    if col[0] == "#":
        l = len(col)
        if l == 4:
            return "#" + col[1]*2 + col[2]*2 + col[3]*2 + "FF"
        if l == 5:
            return "#" + col[1]*2 + col[2]*2 + col[3]*2 + col[4]*2
        elif l == 7:
            return col + "FF"
        elif l == 9:
            return col
        else:
            return None

    res = colors.names_to_hex.get(col)
    if res is not None:
        return conv_to_hex(view, res)

    cs = colors_by_view.get(view.id())
    if cs is None:
        return None

    return conv_to_hex(view, cs.get(col))


def parse_col_rgb(col):
    vals = list(map(lambda s: int(s.strip()), col[4:-1].split(",")))
    return tohex(vals[0], vals[1], vals[2])

def parse_col_rgba(col):
    vals = list(map(lambda s: s.strip(), col[5:-1].split(",")))
    return tohexa(int(vals[0]), int(vals[1]), int(vals[2]), vals[3].find(".") != -1 and int(float(vals[3]) * 255) or int(vals[3]))

def parse_col_array(col):
    vals = col[1:-1].split(",")
    if len(vals) == 3:
        return tohex(int(vals[0]), int(vals[1]), int(vals[2]))
    elif len(vals) == 4:
        return tohexa(int(vals[0]), int(vals[1]), int(vals[2]), vals[3].find(".") != -1 and int(float(vals[3]) * 255) or int(vals[3]))

def isInColor(view, sel, array_format):
    b = sel.begin()
    if b != sel.end():
        return None, None

    word = view.word(b)
    # sass/less variable
    if view.substr(word.begin() - 1) in ["@", "$"]:
        word1 = sublime.Region(word.begin() - 1, word.end())
        res = conv_to_hex(view, view.substr(word1))
        if res is not None:
            return word1, res
        return None, None
    # less variable interpolation
    elif view.substr(word.begin() - 1) == "{" and view.substr(word.begin() - 2) == "@" and view.substr(word.end()) == "}":
        word1 = sublime.Region(word.begin() - 2, word.end() + 1)
        res = conv_to_hex(view, "@" + view.substr(word))
        if res is not None:
            return word1, res
        return None, None
    # hex colors
    elif view.substr(word.begin() - 1) == "#" and view.substr(word.begin() - 2) not in ["&"]:
        word1 = sublime.Region(word.begin() - 1, word.end())
        res = conv_to_hex(view, view.substr(word1))
        if res is not None:
            return word1, res
        return None, None

    # just color
    res = conv_to_hex(view, view.substr(word))
    if res is not None:
        return word, res

    # rgb(...)
    line = view.line(b)
    line_txt = view.substr(line)
    for m in regex_rgb.findall(line_txt):
        start = line_txt.find(m) + line.begin()
        end = start + len(m)
        if b > start and b < end:
            return sublime.Region(start, end), parse_col_rgb(m)

    # rgba(...)
    for m in regex_rgba.findall(line_txt):
        start = line_txt.find(m) + line.begin()
        end = start + len(m)
        if b > start and b < end:
            return sublime.Region(start, end), parse_col_rgba(m)

    if array_format:
        for m in regex_array.findall(line_txt):
            start = line_txt.find(m) + line.begin()
            end = start + len(m)
            if b > start and b < end:
                return sublime.Region(start, end), parse_col_array(m)

    return None, None


def get_cont_col(col):
    (h, s, v) = colorsys.rgb_to_hsv(int(col[1:3],16)/255.0, int(col[3:5],16)/255.0, int(col[5:7],16)/255.0)
    v1 = v * (s - 1) + 1
    s1 = 0
    if abs(v1) > 1e-10:
        s1 = v * s / v1
    (r, g, b) = colorsys.hsv_to_rgb(h >= 0.5 and h - 0.5 or h + 0.5, s1, v1)
    return tohex(int(r * 255), int(g * 255), int(b * 255)) # true complementary


def region_name(s):
    return "mcol_" + s[1:]


def set_scheme(view, cs):
    # print("g set_scheme(%d, %s)" % (view.id(), cs))
    sets = view.settings()
    if sets.get("color_scheme") != cs:
        sets.set("color_scheme", cs)


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

    def add_color(self, col):
        if col in self.colors: return
        self.colors.append(col)
        cont = get_cont_col(col)
        self.string += self.gen_string % (region_name(col), col, cont, cont)
        self.need_upd = True

    def update_view(self, view):
        # print("update_view(%d)" % (view.id()))
        if not os.path.exists(os.path.join(sublime.packages_path(), self.fake_scheme)):
            set_scheme(view, self.color_scheme)
        else:
            set_scheme(view, os.path.join("Packages", self.fake_scheme))

    def update(self, view):
        # # print("update(%d)" % (view.id()))
        if not self.need_upd:
            return False
        # print("do update(%d)" % (view.id()))

        cont = sublime.load_resource(self.color_scheme)
        n = cont.find("<array>") + len("<array>")
        try:
            cont = cont[:n] + self.string + cont[n:]
        except UnicodeDecodeError:
            cont = cont[:n] + self.string.encode("utf-8") + cont[n:]

        write_file(os.path.join(sublime.packages_path(), self.fake_scheme), cont)

        self.need_upd = False
        return True

    def set_scheme(self, view, cs):
        # print("set_scheme(%d, %s)" % (view.id(), cs))
        set_scheme(view, cs)
        global_logic.on_selection_modified(view)

    def restore_color_scheme(self):
        # print("restore_color_scheme()")
        self.colors = []
        self.string = ""
        path = os.path.join(sublime.packages_path(), self.fake_scheme)
        if os.path.exists(path):
            os.remove(path)

    def set_color_scheme(self, cs):
        # print("set_color_scheme(%s)" % (cs))
        self.color_scheme = cs
        self.fake_scheme = os.path.join("Color Highlighter", os.path.split(self.color_scheme)[-1])

    def change_color_scheme(self):
        cs = sublime.load_settings("Preferences.sublime-settings").get("color_scheme")
        # print("change_color_scheme(%s)" % (cs))
        if cs == self.color_scheme:
            return
        self.restore_color_scheme()
        self.set_color_scheme(cs)
        self.set_scheme(sublime.active_window().active_view(), self.color_scheme)

htmlGen = HtmlGen()


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


def parse_stylesheet(view):
    nm = view.file_name()
    if nm is None:
        return

    name, ext = os.path.splitext(nm)
    text = view.substr(sublime.Region(0, 9999999))
    cols = {}
    if ext in [".sass", ".scss"]:
        find_sass_vars(view, text, cols)
    elif ext in [".less"]:
        find_less_vars(view, text, cols)

    global colors_by_view
    colors_by_view[view.id()] = cols


class Logic:
    regions = {}
    inited = False

    def init(self, view):
        if self.inited:
            return

        # print("do init()")
        sets = sublime.load_settings("Preferences.sublime-settings")
        htmlGen.set_color_scheme(sublime.load_settings("Preferences.sublime-settings").get("color_scheme"))
        sublime.load_settings("Preferences.sublime-settings").add_on_change("color_scheme", lambda: htmlGen.change_color_scheme())
        self.inited = True

    def init_regions(self, view):
        if view.id() not in self.regions.keys():
            self.regions[view.id()] = []

    def clean_regions(self, view):
        for s in self.regions[view.id()]:
            view.erase_regions(s)
        self.regions[view.id()] = []

    def get_words(self, view):
        words = []
        for s in view.sel():
            array_format = False
            nm = view.file_name()
            if nm is not None:
                name, ext = os.path.splitext(nm)
                if ext in [".sublime-theme"]:
                    array_format = True
            wd, col = isInColor(view, s, array_format=array_format)
            if col is None:
                continue
            htmlGen.add_color(col)
            words.append((wd, col))
        return words

    def on_new(self, view):
        # print("on_new(%d)" % (view.id()))
        self.init(view)

    def on_activated(self, view):
        # print("on_activated(%d)" % (view.id()))
        parse_stylesheet(view)
        self.init(view)
        htmlGen.update_view(view)
        self.on_selection_modified(view)

    def on_clone(self, view):
        # print("on_clone(%d)" % (view.id()))
        self.on_new(view)

    def on_selection_modified(self, view):
        # # print("on_selection_modified(%d)" % (view.id()))
        self.init(view)
        self.init_regions(view)
        self.clean_regions(view)
        words = self.get_words(view)
        if htmlGen.update(view):
            htmlGen.update_view(view)
        i = 0
        for w, c in words:
            i += 1
            s = "mon_CH_" + str(i)
            self.regions[view.id()].append(s)
            view.add_regions(s, [w], region_name(c))

global_logic = Logic()


class ColorSelection(sublime_plugin.EventListener):
    def on_new(self, view):
        global_logic.on_new(view)

    def on_clone(self, view):
        global_logic.on_clone(view)

    def on_selection_modified(self, view):
        global_logic.on_selection_modified(view)

    def on_activated(self, view):
        global_logic.on_activated(view)


# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        htmlGen.restore_color_scheme()


def plugin_loaded():
    path = os.path.join(sublime.packages_path(), "Color Highlighter")
    if not os.path.exists(path):
        os.mkdir(path)
