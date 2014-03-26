import sublime, sublime_plugin
import os
import re
import string
import shutil
import colorsys

try:
    import colors
except ImportError:
    ColorHighlighter = __import__('Color Highlighter', fromlist=['colors'])
    colors = ColorHighlighter.colors

version = "4.0"


hex_digits = string.digits + "ABCDEF"

loglist = ["Version: " + version]
PREFIX = "mcol_"
sets_name = "ColorHighlighter.sublime-settings"

ch_settings = sublime.load_settings(sets_name)

def write_file(fl, s):
    f = open(fl, 'w')
    f.write(s)
    f.close()

def read_file(fl):
    f = open(fl, 'r')
    res = f.read()
    f.close()
    return res

# Color formats:
# #FFFFFFFF
# #FFFFFF
# #FFF
# rgb(255,255,255)
# words
# black
#888888
max_len = max(len("#FFB"), len("#FFFFFF"), len("#FFFFFFAA"), len("rgb(199, 255, 255)"), len("rgba(255, 255, 255, 0.555)"))

regex1 = re.compile("[r][g][b][(]\d{1,3}[,][ ]*\d{1,3}[,][ ]*\d{1,3}[)]")
regex2 = re.compile("[#][\dA-F]{8}")
regex3 = re.compile("[#][\dA-F]{6}")
regex4 = re.compile("[#][\dA-F]{3}")
regex5 = re.compile("[r][g][b][a][(]\d{1,3}[,][ ]*\d{1,3}[,][ ]*\d{1,3}[,][ ]*(\d+|\d*\.\d+)[)]")


def tohex(r,g,b):
    sr = "%X" % r
    if len(sr) == 1:
        sr = '0' + sr
    sg = "%X" % g
    if len(sg) == 1:
        sg = '0' + sg
    sb = "%X" % b
    if len(sb) == 1:
        sb = '0' + sb
    return "#%s%s%sFF" % (sr,sg,sb)

def isInColorS(s, pos):
    m = regex1.search(s)
    if m is not None and m.group(0) is not None and m.start(0) <= pos and m.end(0) >= pos:
        s = m.group(0)
        s = s[3+1:-1]
        n = s.find(",")
        r = s[0:n]
        s = s[n+1:]
        n = s.find(",")
        g = s[0:n]
        s = s[n+1:]
        b = s
        return sublime.Region(m.start(0), m.end(0)), tohex(int(r), int(g), int(b))

    m = regex5.search(s)
    if m is not None and m.group(0) is not None and m.start(0) <= pos and m.end(0) >= pos:
        s = m.group(0)
        s = s[4+1:-1]
        n = s.find(",")
        r = s[0:n]
        s = s[n+1:]
        n = s.find(",")
        g = s[0:n]
        s = s[n+1:]
        n = s.find(",")
        b = s[0:n]
        return sublime.Region(m.start(0), m.end(0)), tohex(int(r), int(g), int(b))

    s = s.upper()

    # check #FFFFFFFF
    m = regex2.search(s)
    if m is not None and m.group(0) is not None and m.start(0) <= pos and m.end(0) >= pos:
        return sublime.Region(m.start(0), m.end(0)), m.group(0)

    # check #FFFFFF
    m = regex3.search(s)
    if m is not None and m.group(0) is not None and m.start(0) <= pos and m.end(0) >= pos:
        return sublime.Region(m.start(0), m.end(0)), m.group(0) + "FF"

    # check #FFF
    m = regex4.search(s)
    if m is not None and m.group(0) is not None and m.start(0) <= pos and m.end(0) >= pos:
        s = m.group(0)
        return sublime.Region(m.start(0), m.end(0)), s[0] + s[1]*2 + s[2]*2 + s[3]*2 + "FF"

    return None, None

def get_current_word(view, sel):
    n = sel.begin() - 1
    k = sel.end()
    while k - n <= max_len and (view.substr(n).isalpha() or view.substr(n) == "-"):
        n -= 1
    while k - n <= max_len and (view.substr(k).isalpha() or view.substr(k) == "-"):
        k += 1
    return sublime.Region(n + 1, k)

def isInColor(view, sel):
    b = sel.begin()
    if b != sel.end():
        return None, None

    wd = get_current_word(view, sel)
    res = colors.names_to_hex.get(view.substr(wd))
    if res is not None:
        return wd, res

    lwd, lres = None, None
    for i in range(1, max_len):
        s = view.substr(sublime.Region(b - i, b + i))
        wd, res = isInColorS(s, i)
        if res is None and lres is not None:
            i = i - 1
            return sublime.Region(lwd.begin() + (b - i), lwd.end() + (b - i)), lres
        lwd, lres = wd, res

    if lres is None:
        return None, None

    i = max_len - 1
    return sublime.Region(lwd.begin() + (b - i), lwd.end() + (b - i)), lres

def get_cont_col(col):
    (h, s, v) = colorsys.rgb_to_hsv(int(col[1:3],16)/255.0, int(col[3:5],16)/255.0, int(col[5:7],16)/255.0)
    v1 = v * (s - 1) + 1
    s1 = 0
    if abs(v1) > 1e-10:
        s1 = v * s / v1
    (r, g, b) = colorsys.hsv_to_rgb(h >= 0.5 and h - 0.5 or h + 0.5, s1, v1)
    return "#%02x%02x%02xFF" % (int(r * 255), int(g * 255), int(b * 255)) # true complementary

def region_name(s):
    return PREFIX + s[1:]

def set_scheme(view, cs):
    print("g set_scheme(%d, %s)" % (view.id(), cs))
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
        print("update_view(%d)" % (view.id()))
        if not os.path.exists(os.path.join(sublime.packages_path(), self.fake_scheme)):
            set_scheme(view, self.color_scheme)
        else:
            set_scheme(view, os.path.join('Packages', self.fake_scheme))

    def update(self, view):
        # print("update(%d)" % (view.id()))
        if not self.need_upd:
            return False
        print("do update(%d)" % (view.id()))

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
        print("set_scheme(%d, %s)" % (view.id(), cs))
        set_scheme(view, cs)
        global_logic.on_selection_modified(view)

    def restore_color_scheme(self):
        print("restore_color_scheme()")
        self.colors = []
        self.string = ""
        path = os.path.join(sublime.packages_path(), self.fake_scheme)
        if os.path.exists(path):
            os.remove(path)

    def set_color_scheme(self, cs):
        print("set_color_scheme(%s)" % (cs))
        self.color_scheme = cs
        self.fake_scheme = os.path.join('Color Highlighter', os.path.split(self.color_scheme)[-1])

    def change_color_scheme(self):
        cs = sublime.load_settings('Preferences.sublime-settings').get("color_scheme")
        print("change_color_scheme(%s)" % (cs))
        if cs == self.color_scheme:
            return
        self.restore_color_scheme()
        self.set_color_scheme(cs)
        self.set_scheme(sublime.active_window().active_view(), self.color_scheme)


htmlGen = HtmlGen()

# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        htmlGen.restore_color_scheme()

class Logic:
    regions = {}
    inited = False

    def init(self, view):
        if self.inited:
            return

        print("do init()")
        sets = sublime.load_settings('Preferences.sublime-settings')
        htmlGen.set_color_scheme(sublime.load_settings('Preferences.sublime-settings').get("color_scheme"))
        sublime.load_settings('Preferences.sublime-settings').add_on_change("color_scheme", lambda: htmlGen.change_color_scheme())
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
            wd, col = isInColor(view, s)
            if col is None:
                continue
            htmlGen.add_color(col)
            words.append((wd, col))
        return words

    def on_new(self, view):
        print("on_new(%d)" % (view.id()))
        self.init(view)
        self.init_regions(view)

    def on_activated(self, view):
        print("on_activated(%d)" % (view.id()))
        self.init(view)
        htmlGen.update_view(view)
        self.on_selection_modified(view)

    def on_clone(self, view):
        print("on_clone(%d)" % (view.id()))
        self.on_new(view)

    def on_selection_modified(self, view):
        # print("on_selection_modified(%d)" % (view.id()))
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


def plugin_loaded():
    path = os.path.join(sublime.packages_path(), "Color Highlighter")
    if not os.path.exists(path):
        os.mkdir(path)
