import sublime, sublime_plugin

# Constants
PACKAGES_PATH = sublime.packages_path()

dec_digits = ['0','1','2','3','4','5','6','7','8','9']

hex_digits = dec_digits + [ 'A','B','C','D','E','F','a','b','c','d','e','f']

def log(s):
	pass #print s

def tohex(r,g,b):
	return "#" + hex_digits[r / 16] + hex_digits[r % 16] + hex_digits[g / 16] + hex_digits[g % 16] + hex_digits[b / 16] + hex_digits[b % 16]

def tolong(col):
	ln = len(col)
	if ln == 9:
		return col
	if ln == 7:
		return col + "FF"
	return "#" + col[1]*2 + col[2]*2 + col[3]*2 + "FF"

def isColor(col):
	ln = len(col)
	if ln < 4 or ln > 16:
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
	return tolong(tohex(int(col[0]),int(col[1]),int(col[2])))

class ColorContainer:

	colors = []
	newcolors = []
	string = u""

	def __init__(self):
		pass

	def add(self,col):
		self.newcolors.append(col)

	def generate_string(self, col):
		self.string += u"<dict><key>name</key><string>mon_color</string><key>scope</key><string>mcol_" + col + "</string><key>settings</key><dict><key>background</key><string>" + col + "</string></dict></dict>\n"

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




class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFFFF
    # 0x000000
    # rgb(255,255,255)

	colors = ColorContainer()
	color_scheme = None
	color_scheme_cont = None
	process = False

	letters = hex_digits + ['#','(', ')',',','r','g','b']


	def get_current_word(self, view, sel):
		b = sel.begin()
		e = sel.end()
		n = b - 1
		k = e
		while view.substr(n) in self.letters:
			n -= 1
		while view.substr(k) in self.letters:
			k += 1
		return sublime.Region(n + 1,k)

	def _stop_process(self):
		log("Stopped!")
		self.process = False

	def stop_process(self):
		sublime.set_timeout(lambda self = self : self._stop_process(), 500)

	def start_process(self):
		log("Started!")
		self.process = True

	def modify_color_scheme(self):
		if self.process:
			# try later
			sublime.set_timeout(lambda self = self : self.modify_color_scheme(), 250)
			return False
		if self.color_scheme == None:
			return False
		self.start_process()
		f = open(PACKAGES_PATH + self.color_scheme, u'w+')
		f.write(self.color_scheme_cont[0] + self.colors.string + self.color_scheme_cont[1])
		f.close()
		print "Updated!"
		self.stop_process()

	def color_scheme_change(self, view):
		if self.process:
			return
		# getting the color file path (cs)
		cs = view.settings().get('color_scheme')
		if cs == "": return
		cs = cs[cs.find('/'):]
		self.start_process()
		f = open(PACKAGES_PATH + cs, u'r')
		cont = f.read()
		n = cont.find("<array>") + len("<array>")
		self.color_scheme_cont = [cont[:n], cont[n:]]
		f.close()
		self.color_scheme = cs
		self.stop_process()
		self.modify_color_scheme()

	def on_new(self, view):
		sets = view.settings()
		sets.add_on_change("color_scheme", lambda self = self, view = view : self.color_scheme_change(view))
		self.color_scheme_change(view)

	def on_clone(self, view):
		self.on_new(view)

	def on_selection_modified(self, view):
		if self.color_scheme_cont == None:
			self.color_scheme_change(view)
		selection = view.sel()
		words = []
		for s in selection:
			wd = self.get_current_word(view,s)
			col = isColor(view.substr(wd))
			if col:
				self.colors.add(col)
				words.append((wd,col))
		if self.colors.update():
			self.modify_color_scheme()
		if words == []:
			view.erase_regions("mon_col")
			return
		for wd in words:
			w,c = wd
			view.add_regions("mon_col",[w],"mcol_"+c)
