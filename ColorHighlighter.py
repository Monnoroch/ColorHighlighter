import os
import string

import sublime
import sublime_plugin

# TODO: import ColorHighlighter.colors for ST3
from colors import names_to_hex

version = "3.0"

# Constants
PACKAGES_PATH = sublime.packages_path()

hex_digits = string.digits + "ABCDEF"

loglist = ["Version: " + version]
PREFIX = "mcol_"
sets_name = "ColorHighlighter.sublime-settings"

ch_settings = sublime.load_settings(sets_name)


def log(s):
    global loglist
    loglist.append(s)
    #print s


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

colors_re = r'(\b%s\b|%s)|%s|%s' % (
    r'\b|\b'.join(names_to_hex.keys()),
    r'#[0-9a-f]{8}\b|#[0-9a-f]{6}\b',
    r'rgb\(([0-9]+),\s*([0-9]+),\s*([0-9]+)\)',
    r'rgba\(([0-9]+),\s*([0-9]+),\s*([0-9]+),\s*([0-9]+(\.\d+)?)\)',
)


def tohex(r, g, b, a):
    sr = '%X' % r
    if len(sr) == 1:
        sr = '0' + sr
    sg = '%X' % g
    if len(sg) == 1:
        sg = '0' + sg
    sb = '%X' % b
    if len(sb) == 1:
        sb = '0' + sb
    sa = '%X' % int(a * 255)
    if len(sa) == 1:
        sa = '0' + sa
    return '#%s%s%s%s' % (sr, sg, sb, sa)


class HtmlGen:
    colors = {}
    color_scheme = None
    need_upd = False
    need_restore = False
    need_backup = False
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

    def get_y(self, col):
        return (0.3 * int(col[1:3], 16) + 0.59 * int(col[3:5], 16) + 0.11 * int(col[5:7], 16)) * (int(col[7:9], 16) / 255.0)

    def get_cont_col(self, col):
        if self.get_y(col) > 255.0 / 2:
            return '#000000FF'
        return '#FFFFFFFF'

    def region_name(self, s):
        return PREFIX + s[1:]

    def add_color(self, col):
        if col not in self.colors:
            cont = self.get_cont_col(col)
            name = self.region_name(col)
            self.string += self.gen_string % (name, col, cont, cont)
            self.need_upd = True
            self.colors[col] = name
        return self.colors[col]

    def need_update(self):
        return self.need_upd

    def update(self, view):
        if not self.need_upd:
            return
        self.need_upd = False

        cs = self.color_scheme
        if cs is None:
            self.color_scheme = view.settings().get('color_scheme')
            cs = self.color_scheme
        # do not support empty color scheme
        if not cs:
            log("Empty scheme, can't backup")
            return
        # extract name
        cs = cs[cs.find('/'):]
        cont = None
        if os.path.exists(PACKAGES_PATH + cs + ".chback"):
            cont = read_file(PACKAGES_PATH + cs + ".chback")
            log("Already backuped")
        else:
            cont = read_file(PACKAGES_PATH + cs)
            write_file(PACKAGES_PATH + cs + ".chback", cont)  # backup
            log("Backup done")

        # edit cont
        n = cont.find("<array>") + len("<array>")
        try:
            cont = cont[:n] + self.string + cont[n:]
        except UnicodeDecodeError:
            cont = cont[:n] + self.string.encode("utf-8") + cont[n:]

        write_file(PACKAGES_PATH + cs, cont)
        self.need_restore = True

    def restore_color_scheme(self):
        if not self.need_restore:
            return
        self.need_restore = False
        cs = self.color_scheme
        # do not support empty color scheme
        if not cs:
            log("Empty scheme, can't restore")
            return
        # extract name
        cs = cs[cs.find('/'):]
        if os.path.exists(PACKAGES_PATH + cs + ".chback"):
            log("Starting restore scheme: " + cs)
            # TODO: move to other thread
            write_file(PACKAGES_PATH + cs, read_file(PACKAGES_PATH + cs + ".chback"))
            self.colors = []
            self.string = ""
            log("Restore done.")
        else:
            log("No backup :(")

    def set_color_scheme(self, view):
        self.color_scheme = view.settings().get('color_scheme')
        self.need_backup = True

    def change_color_scheme(self, view):
        cs = view.settings().get('color_scheme')
        if cs != self.color_scheme:
            self.restore_color_scheme()
            self.set_color_scheme(view)
            self.update(view)

htmlGen = HtmlGen()

# Commands

# # treat hex vals as colors
# class HexValsAsColorsCommand(sublime_plugin.WindowCommand):
#   def run(self):
#       ch_settings.set("hex_values", not ch_settings.get("hex_values"))
#       sublime.save_settings(sets_name)

#   def is_checked(self):
#       return ch_settings.get("hex_values")

# # treat hex vals as colors
# class XHexValsAsColorsCommand(sublime_plugin.WindowCommand):
#   def run(self):
#       ch_settings.set("0x_hex_values", not ch_settings.get("0x_hex_values"))
#       sublime.save_settings(sets_name)

#   def is_checked(self):
#       return ch_settings.get("0x_hex_values")


# command to print log
class chlogCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        res = ""
        for l in loglist:
            res += l + "\n"
        if res == "":
            return
        log("Log printed.")
        #self.view.insert(edit, 0, res + "\n\n\n")


# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        htmlGen.restore_color_scheme()

all_regs = []
inited = False


class ColorSelection(sublime_plugin.EventListener):
    def on_new(self, view):
        global inited
        if inited:
            return
        inited = True
        sets = view.settings()
        htmlGen.set_color_scheme(view)
        sets.add_on_change('color_scheme', lambda self=self, view=view: htmlGen.change_color_scheme(view))
        # htmlGen.change_color_scheme(view)

    def on_clone(self, view):
        self.on_new(view)

    # def on_close(self, view):
    #   htmlGen.restore_color_scheme()

    def on_load(self, view):
        self.on_modified(view)

    def on_modified(self, view):
        words = {}
        found = []
        ranges = view.find_all(colors_re, sublime.IGNORECASE, r'\1\2\5,\3\6,\4\7,\8', found)
        for i, col in enumerate(found):
            col = col.rstrip(',')
            col = col.split(',')
            if len(col) == 1:
                col = col[0]
                col = names_to_hex.get(col.lower(), col.upper())
                if len(col) == 4:
                    col = '#' + col[1] * 2 + col[2] * 2 + col[3] * 2 + 'FF'
                elif len(col) == 7:
                    col += 'FF'
            else:
                r = int(col[0])
                g = int(col[1])
                b = int(col[2])
                if r >= 256 or g >= 256 or b >= 256:
                    continue
                if len(col) == 4:
                    a = float(col[3])
                    if a > 1.0:
                        continue
                else:
                    a = 1.0
                col = tohex(r, g, b, a)
            name = htmlGen.add_color(col)
            if name not in words:
                words[name] = [ranges[i]]
            else:
                words[name].append(ranges[i])

        if htmlGen.need_update():
            htmlGen.update(view)

        global all_regs
        for s in all_regs:
            view.erase_regions(s)
        all_regs = []

        for name, w in words.items():
            all_regs.append(name)
            view.add_regions(name, w, name)
