import sublime, sublime_plugin
import os

# Constants
PACKAGES_PATH = sublime.packages_path()

dec_digits = "0123456789" #['0','1','2','3','4','5','6','7','8','9']

hex_digits = dec_digits + "ABCDEFabcdef" #[ 'A','B','C','D','E','F','a','b','c','d','e','f']

MAX_COL_LEN = 16
loglist = []
PREFIX = "mcol_"


class ColorContainer:

	colors = []
	newcolors = []
	string = u""
	gen_string = u"<dict><key>name</key><string>mon_color</string><key>scope</key><string>%s\
</string><key>settings</key><dict><key>background</key><string>%s\
</string><key>caret</key><string>%s\
</string><key>foreground</key><string>%s\
</string></dict></dict>\n"

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
		return res

	def need_update(self):
		return self.newcolors != []

	def deinit(self):
		self.colors = []
		self.newcolors = []
		self.string = u""

all_colors = ColorContainer()

# command to print log
class chlogCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		res = u""
		for l in loglist:
			res += l + "\n"
			print "! CH ! " + l
		if res == u"":
			return
		#self.view.insert(edit, 0, res + "\n\n\n")

# command to print log
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		cs = self.view.settings().get('color_scheme')
		# do not support empty color scheme
		if cs == "":
			log("Empty scheme")
			return
		# extract name
		cs = cs[cs.find('/'):]
		if os.path.exists(PACKAGES_PATH + cs + ".chback"):
			print "Nya!"
			b = open(PACKAGES_PATH + cs + ".chback", "r")
			f = open(PACKAGES_PATH + cs, "w")
			f.write(b.read())
			f.close()
			b.close()
			print "Done!"
		else:
			log("No backup :(")
		all_colors.deinit()

# turn on when debugging
def log(s):
	global loglist
	loglist.append(s)
	#print s

def region_name(s):
	return PREFIX + s[1:]

def tohex(r,g,b):
	return "#%X%X%XFF" % (r,g,b)

def tolong(col):
	ln = len(col)
	if ln == 9:
		return col
	if ln == 7:
		return col + "FF"
	return "#%s%s%sFF" % (col[1]*2, col[2]*2, col[3]*2)

def isColor(col):
	ln = len(col)
	if ln < 4 or ln > MAX_COL_LEN:
		return False
	if col[0] == '#':
		if ln not in [4,7,9]:
			return False
		for l in col[1:]:
			if l not in hex_digits:
				return False
		return tolong(col)
	if col[-1] != ')' or col[0:4] != "rgb(":
		return False
	col = col[4:-1].split(',')
	if len(col) != 3:
		return False
	for n in col:
		ll = len(n)
		if ll > 3:
			return False
		for c in n:
			if c not in dec_digits:
				return False
	return tohex(int(col[0]),int(col[1]),int(col[2]))

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

	letters = hex_digits + "#(),rgb" # ['#','(', ')',',','r','g','b']


	def get_current_word(self, view, sel):
		b = sel.begin()
		e = sel.end()
		n = b - 1
		k = e
		while k - n <= MAX_COL_LEN and view.substr(n) in self.letters:
			n -= 1
		while k - n <= MAX_COL_LEN and view.substr(k) in self.letters:
			k += 1
		return sublime.Region(n + 1,k)

	def _stop_process(self):
		#log("! Stopped!")
		self.process = False

	def stop_process(self):
		self._stop_process()
		#sublime.set_timeout(lambda self = self : self._stop_process(), 200)

	def start_process(self):
		#log("! Started!")
		self.process = True

	def modify_color_scheme(self):
		if self.color_scheme == None:
			log("color_scheme is none")
			return False
		if self.process:
			# try later
			log("Alreaty doing something")
			# TODO: decide if needed
			sublime.set_timeout(lambda self = self : self.modify_color_scheme(), 100)
			return False
		self.start_process()
		f = open(PACKAGES_PATH + self.color_scheme, u'w')
		f.write(self.color_scheme_cont[0] + self.colors.string + self.color_scheme_cont[1])
		f.close()
		self.stop_process()

	def read_colors(self, s):
		n = s.find(PREFIX)
		while n != -1:
			s = s[n+5:]
			self.colors.add('#' + s[:8])
			n = s.find(PREFIX)
		self.colors.update()
		log("Colors loaded: " + str(self.colors.colors))

	def _color_scheme_change(self, view, cs):
		self.color_scheme = cs
		self.start_process()
		f = open(PACKAGES_PATH + cs, u'r')
		cont = f.read()

		# backup the theme
		if not os.path.exists(PACKAGES_PATH + cs + ".chback"):
			b = open(PACKAGES_PATH + cs + ".chback", "w")
			b.write(cont)
			b.close()
		
		n = cont.find("<array>") + 7
		self.color_scheme_cont = [cont[:n], cont[n:]]
		self.read_colors(cont[n:cont.rfind(PREFIX)+8+5])
		f.close()
		self.stop_process()
		self.modify_color_scheme()

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

	def on_selection_modified(self, view):
		selection = view.sel()
		words = []
		for s in selection:
			wd = self.get_current_word(view,s)
			col = isColor(view.substr(wd))
			if col:
				self.colors.add(col)
				words.append((wd,col))
		if self.colors.update():
			#sublime.set_timeout(lambda self = self : self.modify_color_scheme(), 0)
			self.modify_color_scheme()
		if words == []:
			view.erase_regions("mon_CH")
			return
		for wd in words:
			w,c = wd
			view.add_regions("mon_CH",[w], region_name(c))
