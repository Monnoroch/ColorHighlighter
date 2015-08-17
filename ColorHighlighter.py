
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

plugin_name = "Color Highlighter"

try:
    import colors
except ImportError:
    colors = __import__(plugin_name, fromlist=["colors"]).colors


version = "7.0"

# get ST version as int
def get_version():
    return int(sublime.version())

# check, if it's ST3
def is_st3():
    return get_version() >= 3000

# async helpers

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

def region_name(s):
    return "mcol_" + s[1:]

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

class Settings:
    pfname = "Preferences.sublime-settings"
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

        self.prefs = sublime.load_settings(self.pfname)
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

    def on_prefs_settings_change(self, forse=False):
        self.prefs = sublime.load_settings(self.pfname)

        color_scheme = self.prefs.get("color_scheme")
        if forse or self.color_scheme != color_scheme:
            self.color_scheme = color_scheme
            self.callbacks.set_scheme(color_scheme)

def print_error(err):
    print(err.replace("\\n", "\n"))

def create_icon(col):
    fname = "%s.png" % col[1:]
    fpath = os.path.join(icons_path(), fname)
    fpath_full = os.path.join(icons_path(PAbsolute), fname)

    if os.path.exists(fpath_full):
        return fpath

    cmd =  color_highlighter.settings.get("convert_util_path") + ' -type TrueColorMatte -channel RGBA -size 32x32 -alpha transparent xc:none -fill "%s" -draw "circle 15,16 8,10" png32:"%s"'
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

def get_word_css(view, region):
    word = view.word(region)
    chars = "-"
    while view.substr(word.b) in chars and view.substr(word.b + 1).isalnum():
        word = sublime.Region(word.a, view.word(sublime.Region(word.b + 1, word.b + 1)).b)
    while view.substr(word.a - 1) in chars and view.substr(word.a - 2).isalnum():
        word = sublime.Region(view.word(sublime.Region(word.a - 2, word.a - 2)).a, word.b)
    if view.substr(word.a - 1) in "@$":
        word = sublime.Region(word.a - 1, word.b)
    return word

# the class for searching for colors in a region
class ColorFinder:
    # if the @region is in some text, that represents color, return new region, containing that color text and parsed color value in #RRGGBBAA format
    def get_color(self, view, region, variables):
        reg, fmt = self.find_color(view, region, variables)
        if reg is None:
            return None, None

        return reg, self.convert_color(view.substr(reg), variables, fmt)

    # get all colors from region
    def get_colors(self, view, variables, region=None):
        regs = self.find_colors(view, variables, region)
        res = []
        for (reg, fmt) in regs:
            res.append((reg, self.convert_color(view.substr(reg), variables, fmt)))
        return res

    # main functions

    # convert color with type @fmt to #RRGGBBAA
    def convert_color(self, color, variables, fmt=None):
        if fmt == None:
            fmt = self.get_fmt(color, variables)

        if fmt == "@named":
            return colors.names_to_hex[color]
        elif fmt.startswith("@var-"):
            return variables[color]["col"]
        elif fmt == "#8":
            return color
        return None

    # convert color from #RRGGBBAA to different formats
    def convert_back_color(self, color, variables, fmt):
        if fmt == "@named":
            for name in colors.names_to_hex:
                if colors.names_to_hex[name] == color:
                    return name
            return color
        elif fmt.startswith("@var-"):
            for k in variables.keys():
                v = variables[k]
                if v["fmt"] == fmt and color == v["col"]:
                    return k
            return color
        elif fmt == "#8":
            return color
        return None


    regex_str = "[#][0-9a-fA-F]{8}"
    regex = re.compile(regex_str)

    names = ""
    for k in list(colors.names_to_hex.keys()):
        names += k + "|"
    names_regex = re.compile("\\b(" + names[:-1] + ")\\b")

    # get color format type
    def get_fmt(self, color, variables):
        if color in colors.names_to_hex.keys():
            return "@named"
        if color in variables.keys():
            return variables[color]["fmt"]
        m = self.regex.search(color)
        if m:
            return "#8"
        return None

    # if the @region is in some text, that represents color, return new region, containing that color text and format type
    def find_color(self, view, region, variables):
        word = get_word_css(view, region)
        word_str = view.substr(word)

        # TODO: nice regexes?
        if word_str in variables.keys():
            return word, variables[word_str]["fmt"]
        if word_str in colors.names_to_hex.keys():
            return word, "@named"

        line = view.line(region)
        newreg = sublime.Region(max(region.a - 9, line.a), min(region.b + 9, line.b))
        text = view.substr(newreg)
        m = self.regex.search(text)
        while m:
            if newreg.a + m.start() <= region.a and newreg.a + m.end() >= region.b:
                return sublime.Region(newreg.a + m.start(), newreg.a + m.end()), "#8"
            m = self.regex.search(text, m.end())
        return None, None

    vars_prepend = {
        "@var-less": "@",
        "@var-sass": "$",
        "@var-styl": "",
    }

    def vars_conv(self, fmt, val):
        if fmt == "@var-less" or fmt == "@var-sass":
            return val[1:]
        return val

    def find_all(self, regex, region, text, fmt, res):
        m = regex.search(text)
        while m:
            res.append((sublime.Region(region.a + m.start(), region.a + m.end()), fmt));
            m = regex.search(text, m.end())

    # find all colors and their formats in the view region
    def find_colors(self, view, variables, region=None):
        if region is None:
            region = sublime.Region(0, view.size())

        text = view.substr(region)
        res = []
        self.find_all(self.regex, region, text, "#8", res)
        self.find_all(self.names_regex, region, text, "@named", res)
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
                self.find_all(re.compile(self.vars_prepend[fmt] + "\\b(" + var_regexs[fmt] + ")\\b"), region, text, fmt, res)
        return res


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
        print("ColorHighlighterView.enable(%d, %s)" % (self.view.id(), val))
        self.disabled = not val
        if self.disabled:
            self.restore_scheme()

    def get_colors_sel(self):
        vs = self.ch.get_vars(self.view)
        res = []
        for s in self.view.sel():
            region, fmt = self.ch.color_finder.find_color(self.view, s, vs)
            if region is not None:
                col = self.ch.color_finder.convert_color(self.view.substr(region), vs, fmt)
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
                self.view.add_regions(st + "-ico", [region], region_name(col) + "-ico", create_icon(col), sublime.HIDDEN)

        scheme, f = self.ch.add_colors(cols)
        self.set_scheme(scheme, f)

    def on_activated(self):
        print("on_activated(%d)" % self.view.id())
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
                self.view.add_regions(st + "-ico", [reg], region_name(col) + "-ico", create_icon(col), sublime.HIDDEN)

        scheme, f = self.ch.add_colors(cols)
        self.set_scheme(scheme, f)

    def on_close(self):
        print("on_close(%d)" % self.view.id(), "changing color scheme to " + self.ch.color_scheme)
        self.restore_scheme()

    def on_settings_change(self):
        cs = self.view.settings().get("color_scheme")
        print("ColorHighlighterView.on_settings_change: ", cs)

    def set_scheme(self, val, force=False):
        if force or self.view.settings().get("color_scheme") != val:
            print("set_scheme(%d, %s)" % (self.view.id(), val))
            self.view.settings().set("color_scheme", val)

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
            return False

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
        print("set_scheme(%s)" % val)
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
        print("add_view(%d, %s)" % (view.id(), view.file_name()))
        v = ColorHighlighterView(self, view)
        v.enable(self.valid_fname(view.file_name()))
        if self.started:
            v.set_scheme(self.scheme_name())
        self.views[view.id()] = v

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
        print("get_regions_flags", style)
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
        self.add_view(view)

    def on_clone(self, view):
        self.add_view(view)

    def on_load(self, view):
        self.add_view(view)

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

    # vars extract

    vars_file_cache = {}
    vars_view_cache = {}

    def parse_vars_text(self, text, fname, dirname, ext, cache):
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

            on_line(fname, line, i - 1, vs)


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
        self.parse_vars_text(view.substr(0, view.size()), "@view:" + str(view.id()), "", "", obj)

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

        text = v["text"]
        if text in variables.keys():
            v["col"] = self.get_col(text, variables)
        else:
            v["col"] = self.color_finder.convert_color(text, {})
        return v["col"]

color_highlighter = None

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

def read_file(fl):
    with codecs.open(fl, "r", "utf-8") as f:
        return f.read()

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

# main event listener
class ColorSelection(sublime_plugin.EventListener):
    def on_new(self, view):
        color_highlighter.on_new(view)

    def on_clone(self, view):
        color_highlighter.on_clone(view)

    def on_load(self, view):
        color_highlighter.on_load(view)

    def on_close(self, view):
        color_highlighter.on_close(view)

    def on_selection_modified(self, view):
        color_highlighter.on_selection_modified(view)

    def on_modified(self, view):
        color_highlighter.on_modified(view)

    def on_post_save(self, view):
        color_highlighter.on_post_save(view)

    def on_activated(self, view):
        color_highlighter.on_activated(view)

    def on_query_context(self, view, key, op, operand, match_all):
        if not key.startswith('color_highlighter.'):
            return None
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
            new_col = color_highlighter.color_finder.convert_back_color(col, vs, fmt)
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
            print("SEND DATA: ", "\t".join(list(map(str, self.words))))
            self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], x[1], self.output)), self.words))})
        self.output = None

class BaseColorConvertCommand(ColorCommand):
    def do_run(self, new_fmt):
        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

class ColorConvertCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        panel = self.view.window().show_input_panel("Format: ", fmt, self.do_run, self.on_change, self.clear)
        panel.sel().add(sublime.Region(0, panel.size()))

class ColorConvertNextCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        formats = list(filter(lambda f, fmt=fmt: f == fmt or (not f.startswith("@var-")), color_highlighter.settings.get("formats").keys()))
        print(formats)
        new_fmt = formats[0]
        i = 0
        for f in formats:
            if f == fmt:
                if i < len(formats) - 1:
                    new_fmt = formats[i + 1]
                break
            i += 1

        print(new_fmt)
        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

class ColorConvertPrevCommand(BaseColorConvertCommand):
    def run(self, edit):
        self.vs = color_highlighter.get_vars(self.view)
        fmt = color_highlighter.color_finder.get_fmt(self.view.substr(self.words[0][0]), self.vs)
        formats = list(filter(lambda f, fmt=fmt: f == fmt or (not f.startswith("@var-")), color_highlighter.settings.get("formats").keys()))
        print(formats)
        new_fmt = formats[len(formats) - 1]
        i = 0
        for f in formats:
            if f == fmt:
                if i > 0:
                    new_fmt = formats[i - 1]
                break
            i += 1

        print(new_fmt)
        self.view.run_command("ch_replace_color", {"words": "\t".join(map(lambda x: str((x[0], new_fmt, x[2])), self.words))})
        self.clear()

# #FF0000FF
# #00FF00FF

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
                f.write(sublime.load_binary_resource(color_picker_path()))
        else:
            shutil.copy(color_picker_path(PAbsolute), cpupath)
        os.chmod(cpupath, chflags)

    global color_highlighter
    color_highlighter = ColorHighlighter()

# unload all the stuff
def plugin_unloaded():
    color_highlighter.unload()

# ST2 support. Maby need set_timeout?
if not is_st3():
    plugin_loaded()
