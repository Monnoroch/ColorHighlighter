import sublime, sublime_plugin
import os

import colors

version = "2.1.0"

# Constants
PACKAGES_PATH = sublime.packages_path()

dec_digits = "0123456789" #['0','1','2','3','4','5','6','7','8','9']

hex_digits = dec_digits + "ABCDEFabcdef" #[ 'A','B','C','D','E','F','a','b','c','d','e','f']

MAX_COL_LEN = 16
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

# Commands

# treat hex vals as colors
class HexValsAsColorsCommand(sublime_plugin.WindowCommand):
	def run(self):
		ch_settings.set("hex_values", not ch_settings.get("hex_values"))
		sublime.save_settings(sets_name)

	def is_checked(self):
		return ch_settings.get("hex_values")

# treat hex vals as colors
class XHexValsAsColorsCommand(sublime_plugin.WindowCommand):
	def run(self):
		ch_settings.set("0x_hex_values", not ch_settings.get("0x_hex_values"))
		sublime.save_settings(sets_name)

	def is_checked(self):
		return ch_settings.get("0x_hex_values")

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
		cs = self.view.settings().get('color_scheme')
		# do not support empty color scheme
		if cs == "":
			log("Empty scheme, can't restore")
			return
		# extract name
		cs = cs[cs.find('/'):]
		if os.path.exists(PACKAGES_PATH + cs + ".chback"):
			log("Starting restore scheme: " + cs)
			write_file(PACKAGES_PATH + cs, read_file(PACKAGES_PATH + cs + ".chback"))
			log("Restore done.")
			all_colors.deinit()
		else:
			log("No backup :(")

class ColorContainer:

	colors = []
	newcolors = []
	string = ""
	gen_string = "<dict><key>name</key><string>mon_color</string><key>scope</key><string>%s\
</string><key>settings</key><dict><key>background</key><string>%s\
</string><key>caret</key><string>%s\
</string><key>foreground</key><string>%s\
</string></dict></dict>\n"

# rgb(255,1,10)

	def __init__(self):
		pass

	def add(self,col):
		self.newcolors.append(col)

	def generate_string(self, col):
		cont = get_cont_col(col)
		self.string += self.gen_string % (region_name(col), col, cont, cont)

	def update(self):
		res = False
		for c in self.newcolors:
			if c not in self.colors:
				self.colors.append(c)
				self.generate_string(c)
				res = True
		self.newcolors = []
		self.string = self.string.decode("utf-8").encode("utf-8")
		return res

	def need_update(self):
		return self.newcolors != []

	def deinit(self):
		self.colors = []
		self.newcolors = []
		self.string = "".decode("utf-8").encode("utf-8")

all_colors = ColorContainer()

def region_name(s):
	return PREFIX + s[1:]

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

def tolong(col):
	ln = len(col)
	if ln == 9:
		return col.upper()
	if ln == 7:
		return col.upper() + "FF"
	return ("#%s%s%sFF" % (col[1]*2, col[2]*2, col[3]*2)).upper()


def isColor(col):
	ln = len(col)
	if ln < 3 or ln > MAX_COL_LEN:
		return False
	if col[0] == '#':
		if ln not in [4,7,9]:
			return False
		for l in col[1:]:
			if l not in hex_digits:
				return False
		return tolong(col)
	if ch_settings.get("0x_hex_values") and col[:2] == "0x":
		if ln in [5,8,10]:
			for l in col[2:]:
				if l not in hex_digits:
					return False
			return tolong('#' + col[2:])
		return False
	if ch_settings.get("hex_values") and ln in [3,6,8]:
		for l in col:
			if l not in hex_digits:
				return False
		return tolong('#' + col)
	if col[-1] != ')' or col[0:4] != "rgb(":
		return False
	cols = col[4:-1].split(',')
	if len(cols) != 3:
		return False
	for n in cols:
		ll = len(n)
		if ll > 3 or ll == 0:
			return False
		for c in n:
			if c not in dec_digits:
				return False
	return tohex(int(cols[0]),int(cols[1]),int(cols[2]))

def get_y(col):
	return (0.3 * int(col[1:3],16) + 0.59 * int(col[3:5],16) + 0.11 * int(col[5:7],16)) * (int(col[7:9],16) / 255.0)

def get_cont_col(col):
	if get_y(col) > 255.0/2:
		return "#000000FF"
	return "#FFFFFFFF"

class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFFFF
    # rgb(255,255,255)

	colors = all_colors
	color_scheme = None
	color_scheme_cont = None
	process = False

	letters = hex_digits + "#(),rgbx" # ['#','(', ')',',','r','g','b']


	def get_current_word(self, view, sel):
		n = sel.begin() - 1
		k = sel.end()
		while k - n <= MAX_COL_LEN and view.substr(n) in self.letters:
			n -= 1
		while k - n <= MAX_COL_LEN and view.substr(k) in self.letters:
			k += 1
		return sublime.Region(n + 1,k)

	def _stop_process(self):
		log("Stopped!")
		self.process = False

	def stop_process(self):
		self._stop_process()
		#sublime.set_timeout(lambda self = self : self._stop_process(), 200)

	def start_process(self):
		log("Started!")
		self.process = True

	def modify_color_scheme(self, view):
		if self.color_scheme == None:
			self.color_scheme_change(view)
			log("color_scheme is none")
			return False
		if self.process:
			# try later
			log("Alreaty doing something")
			# TODO: decide if needed
			sublime.set_timeout(lambda self = self, view = view : self.modify_color_scheme(view), 100)
			return False
		log("Modifying scheme: " + self.color_scheme)
		self.start_process()
		ss = self.color_scheme_cont[0] + self.colors.string + self.color_scheme_cont[1]
		write_file(PACKAGES_PATH + self.color_scheme, ss)
		self.stop_process()
		log("Modifying done.")
		
	def read_colors(self, s):
		self.colors.deinit()
		n = s.find(PREFIX)
		while n != -1:
			s = s[n+5:]
			self.colors.add('#' + s[:8])
			n = s.find(PREFIX)
		log("Colors loaded: " + str(self.colors.newcolors))
		self.colors.update()

	def _color_scheme_change(self, view, cs):
		log("Changing to scheme: " + cs)
		self.color_scheme = cs
		self.start_process()
		cont = read_file(PACKAGES_PATH + cs)

		# backup the theme
		if not os.path.exists(PACKAGES_PATH + cs + ".chback"):
			log("Backup scheme: " + cs)
			write_file(PACKAGES_PATH + cs + ".chback", cont)
			log("Backup done!")
		
		n = cont.find("<array>") + 7
		self.color_scheme_cont = [cont[:n], cont[n:]]
		self.read_colors(cont[n:cont.rfind(PREFIX)+8+5])
		self.stop_process()
		log("Changing done.")
		self.modify_color_scheme(view)

	def color_scheme_change(self, view):
		# getting the color file path (cs)
		cs = view.settings().get('color_scheme')
		# do not support empty color scheme
		if cs == "":
			log("Empty scheme")
			return
		# extract name
		cs = cs[cs.find('/'):]
		# nothing's changed
		if self.color_scheme == cs:
			return
		log("Loaded scheme: " + cs)
		if self.process:
			log("Something's really wrong!")
			return
		self._color_scheme_change(view, cs)

	def on_new(self, view):
		sets = view.settings()
		sets.add_on_change("color_scheme", lambda self = self, view = view : self.color_scheme_change(view))
		self.color_scheme_change(view)

	def on_clone(self, view):
		self.on_new(view)

		black

	def on_selection_modified(self, view):
		selection = view.sel()
		words = []
		for s in selection:
			wd = self.get_current_word(view,s)
			col = isColor(view.substr(wd))
			if not col:
				wd = view.word(s)
				try:
					col = colors.names_to_hex[view.substr(wd)]
				except KeyError:
					pass
			if col:
				self.colors.add(col)
				words.append((wd,col))
		if self.colors.update():
			#sublime.set_timeout(lambda self = self, view = view : self.modify_color_scheme(view), 0)
			self.modify_color_scheme(view)
		if words == []:
			view.erase_regions("mon_CH")
			return
		for wd in words:
			w,c = wd
			#log(region_name(c))
			view.add_regions("mon_CH",[w], region_name(c))
			