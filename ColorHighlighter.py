# -*- coding: utf-8 -*- 

import sublime, sublime_plugin

# Constants
PACKAGES_PATH = sublime.packages_path()



settings = sublime.load_settings(u'ColorHighlighter.sublime-settings')

class ColorChangeEvent:
	def __init__(self, view, ev, color):
		self.color = color
		self.view = view
		self.ev = ev

	def run(self):
		self.ev(self.view, self.color)

events = []
fast_events = []
hold = False
def add_event(ev, prior):
	if prior:
		fast_events.append(ev)
	else:
		events.append(ev)

def run_events():
	global events, fast_events, hold
	ev = None
	if hold:
		sublime.set_timeout(run_events, 10)
	# need to process ALL fast events
	if fast_events != []:
		ev = fast_events[0]
		fast_events = fast_events[1:]
	# need to process only the last event
	elif events != []:
		ev = events[0]
		events = []
	if ev:
		ev.run()
	
	

# just for testing
class MyEx(BaseException):

	def __init__(self, s):
		self.s = s

	def __str__(self):
		return "MyEx("+self.s+")"

	def __rep__(self):
		return "MyEx("+self.s+")"

def RepairOldScheme(self, view):
	if self.old != "":
		# need to be fast
		self.SetColor(view, self.old, True)
		self.colored = False
		self.current_col = ""

def color_scheme_change(self, view):
	global hold
	hold = True
	# getting the color file path (cs)
	cs = view.settings().get('color_scheme')
	# does not support null color scheme yet
	if cs == "": return
	cs = cs[cs.find('/'):]
	# if color scheme has been changed - update one
	if self.color_scheme != cs:
		# because it could break =(
		RepairOldScheme(self, view)

		self.color_scheme = cs
		self.old = ""

		f = open(PACKAGES_PATH + self.color_scheme, u'r+')
		cont = f.read()
		
		n = cont.find("<key>selection</key>")
		cont1 = cont[n:]
		n1 = cont1.find("<string>") + 8
		n2 = cont1.find("</string>")
		if self.old == "":
			self.old = cont1[n1:n2]
		self.n1 = n + n1
		self.n2 = n + n2
		
		f.close()
	hold = False


		

def colorcode_formats_change(self, view):
	self.colorcode_formats = settings.get("colorcode_formats")

def colorcode_transform_change(self, view):
	self.colorcode_transform = settings.get("colorcode_transform")

# matches col against fmt
def Match(col, fmt):
	if len(col) != len(fmt):
		return False
	for (c,i) in zip(fmt, xrange(0, len(fmt) - 1)):
		if c != '%' and c != col[i]:
			return False
	return True

# get number from color code col, matched to format fmt
def GetNum(col, fmt):
	num = ""
	for (c,s) in zip(col, fmt):
		if s == '%':
			num += c
	return num

# get number from color code col, matched to format fmt
def PutNum(num, fmt):
	k = 0
	res = ""
	for c in fmt:
		if c != '%':
			res += c
		else:
			res += num[k]
			k+=1
	return res

# convert color code from format fmt1 to format fmt2
def Convert(col, fmt1, fmt2):
	return PutNum(GetNum(col, fmt1), fmt2)

class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFFFF
    # 0x000000
    # rgb(AA,FF,22)

	letters = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F', 'a', 'b', 'c', 'd', 'e', 'f']

	old = ""
	colored = False
	color_scheme = ""
	current_col = ""
	colorcode_formats = []
	colorcode_transform = []
	n1 = 0
	n2 = 0
		

	def on_new(self, view):
		sets = view.settings()
		sets.add_on_change("color_scheme", lambda s = self, v = view : color_scheme_change(s,v))
		color_scheme_change(self, view)
		#
		settings.add_on_change("colorcode_formats", lambda s = self, v = view : colorcode_formats_change(s,v))
		settings.add_on_change("colorcode_transform", lambda s = self, v = view : colorcode_transform_change(s,v))
		colorcode_formats_change(self, view)
		colorcode_transform_change(self, view)

	def on_clone(self, view):
		self.on_new(view)

	# returns color code converted to native form or False
	def isHexColor(self, view, col):
		for fmt in self.colorcode_formats:
			if Match(col, fmt):
				if fmt in self.colorcode_transform:
					return Convert(col, fmt, self.colorcode_transform[fmt])
				return col
		return False


    # check if col is a hexademical color code
#	def isHexColor(self, view, col):
#		# short, normal and alpha-channel support
#		if not (len(col) in [4, 7, 9] and col[0] == '#'):
#			return False
#		for c in col[1:]:
#			if c not in self.letters:
#				return False
#		return True

	# in case of any multithread optimization made it that way
	def SetColor(self, view, color, prior = False):
		add_event(ColorChangeEvent(view, self._SetColor, color), prior)
		sublime.set_timeout(run_events, 0)

	def _SetColor(self, view, color):
		global hold
		hold = True
		f = open(PACKAGES_PATH + self.color_scheme, u'r+')
		cont = f.read()
		# main job
		length = self.n2 - self.n1
		newlength = len(color)
		# wrighting back in file
		f.seek(self.n1)
		if length == newlength:
			f.write(color)
		elif length == 9 and newlength == 7:
			# clever hack (IDK really can i do it w\o any side effects)
			# TODO: figue out
			f.write(color+"FF")
		else:
			# sad, but nesessary =\
			f.write(color)
			f.write(cont[self.n2:])
			self.n2 = self.n2 - length + newlength
		f.close()
		hold = False

	def on_selection_modified(self, view):
		selection = view.sel()
		# we dont do it with multiple selection
		if len(selection) != 1: return
		s = view.substr(selection[0])
		s = self.isHexColor(view, s)
		if self.colored:
			if not s:
				RepairOldScheme(self, view)
			elif s != self.current_col:
				self.SetColor(view, s)
				self.current_col = s
		else:
			if s:
				self.colored = True
				self.SetColor(view, s)
				self.current_col = s

	def on_activate(self, view):
		self.on_selection_modified(view)
		