import time
import threading
from functools import partial

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
    r'#[0-9a-f]{8}\b|#[0-9a-f]{6}\b|#[0-9a-f]{3}\b',
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

    def on_modified(self, view):
        queue_highlight_colors(view)

    def on_load(self, view):
        if view.is_scratch() or view.settings().get('colorhighlighter') is False or view.settings().get('colorhighlighter') == 'save-only':
            return

        queue_highlight_colors(view, event='on_load')

    def on_post_save(self, view):
        if view.is_scratch() or view.settings().get('colorhighlighter') is False:
            return

        queue_highlight_colors(view, preemptive=True, event='on_post_save')

    def on_selection_modified(self, view):
        if view.is_scratch():
            return
        delay_queue(1000)  # on movement, delay queue (to make movement responsive)


TIMES = {}       # collects how long it took the color highlighter to complete
COLOR_HIGHLIGHTS = {}  # Highlighted regions


def highlight_colors(view, **kwargs):
    vid = view.id()
    start = time.time()

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

    end = time.time()
    TIMES[vid] = (end - start) * 1000  # Keep how long it took to color highlight


################################################################################
# Queue connection

QUEUE = {}       # views waiting to be processed by color highlighter

# For snappier color highlighting, different delays are used for different color highlighting times:
# (color highlighting time, delays)
DELAYS = (
    (50, (50, 100)),
    (100, (100, 300)),
    (200, (200, 500)),
    (400, (400, 1000)),
    (800, (800, 2000)),
    (1600, (1600, 3000)),
)


def get_delay(t, view):
    delay = 0

    for _t, d in DELAYS:
        if _t <= t:
            delay = d
        else:
            break

    delay = delay or DELAYS[0][1]

    # If the user specifies a delay greater than the built in delay,
    # figure they only want to see marks when idle.
    minDelay = int(view.settings().get('colorhighlighter_delay', 0) * 1000)

    return (minDelay, minDelay) if minDelay > delay[1] else delay


def _update_view(view, filename, **kwargs):
    # It is possible that by the time the queue is run,
    # the original file is no longer being displayed in the view,
    # or the view may be gone. This happens especially when
    # viewing files temporarily by single-clicking on a filename
    # in the sidebar or when selecting a file through the choose file palette.
    valid_view = False
    view_id = view.id()

    for window in sublime.windows():
        for v in window.views():
            if v.id() == view_id:
                valid_view = True
                break

    if not valid_view or view.is_loading() or (view.file_name() or '').encode('utf-8') != filename:
        return

    try:
        highlight_colors(view, **kwargs)
    except RuntimeError, ex:
        print ex


def queue_highlight_colors(view, timeout=-1, preemptive=False, event=None):
    '''Put the current view in a queue to be examined by a color highlighter'''

    if preemptive:
        timeout = busy_timeout = 0
    elif timeout == -1:
        timeout, busy_timeout = get_delay(TIMES.get(view.id(), 100), view)
    else:
        busy_timeout = timeout

    kwargs = {'timeout': timeout, 'busy_timeout': busy_timeout, 'preemptive': preemptive, 'event': event}
    queue(view, partial(_update_view, view, (view.file_name() or '').encode('utf-8'), **kwargs), kwargs)


def _callback(view, filename, kwargs):
    kwargs['callback'](view, filename, **kwargs)


def background_color_highlighter():
    __lock_.acquire()

    try:
        callbacks = QUEUE.values()
        QUEUE.clear()
    finally:
        __lock_.release()

    for callback in callbacks:
        sublime.set_timeout(callback, 0)

################################################################################
# Queue dispatcher system:

queue_dispatcher = background_color_highlighter
queue_thread_name = 'background color highlighter'
MAX_DELAY = 10


def queue_loop():
    '''An infinite loop running the color highlighter in a background thread meant to
       update the view after user modifies it and then does no further
       modifications for some time as to not slow down the UI with color highlighting.'''
    global __signaled_, __signaled_first_

    while __loop_:
        #print 'acquire...'
        __semaphore_.acquire()
        __signaled_first_ = 0
        __signaled_ = 0
        #print 'DISPATCHING!', len(QUEUE)
        queue_dispatcher()


def queue(view, callback, kwargs):
    global __signaled_, __signaled_first_
    now = time.time()
    __lock_.acquire()

    try:
        QUEUE[view.id()] = callback
        timeout = kwargs['timeout']
        busy_timeout = kwargs['busy_timeout']

        if now < __signaled_ + timeout * 4:
            timeout = busy_timeout or timeout

        __signaled_ = now
        _delay_queue(timeout, kwargs['preemptive'])

        if not __signaled_first_:
            __signaled_first_ = __signaled_
            #print 'first',
        #print 'queued in', (__signaled_ - now)
    finally:
        __lock_.release()


def _delay_queue(timeout, preemptive):
    global __signaled_, __queued_
    now = time.time()

    if not preemptive and now <= __queued_ + 0.01:
        return  # never delay queues too fast (except preemptively)

    __queued_ = now
    _timeout = float(timeout) / 1000

    if __signaled_first_:
        if MAX_DELAY > 0 and now - __signaled_first_ + _timeout > MAX_DELAY:
            _timeout -= now - __signaled_first_
            if _timeout < 0:
                _timeout = 0
            timeout = int(round(_timeout * 1000, 0))

    new__signaled_ = now + _timeout - 0.01

    if __signaled_ >= now - 0.01 and (preemptive or new__signaled_ >= __signaled_ - 0.01):
        __signaled_ = new__signaled_
        #print 'delayed to', (preemptive, __signaled_ - now)

        def _signal():
            if time.time() < __signaled_:
                return
            __semaphore_.release()

        sublime.set_timeout(_signal, timeout)


def delay_queue(timeout):
    __lock_.acquire()
    try:
        _delay_queue(timeout, False)
    finally:
        __lock_.release()


# only start the thread once - otherwise the plugin will get laggy
# when saving it often.
__semaphore_ = threading.Semaphore(0)
__lock_ = threading.Lock()
__queued_ = 0
__signaled_ = 0
__signaled_first_ = 0

# First finalize old standing threads:
__loop_ = False
__pre_initialized_ = False


def queue_finalize(timeout=None):
    global __pre_initialized_

    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == queue_thread_name:
            __pre_initialized_ = True
            thread.__semaphore_.release()
            thread.join(timeout)
queue_finalize()

# Initialize background thread:
__loop_ = True
__active_color_highlighter_thread = threading.Thread(target=queue_loop, name=queue_thread_name)
__active_color_highlighter_thread.__semaphore_ = __semaphore_
__active_color_highlighter_thread.start()

################################################################################
