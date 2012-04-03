# -*- coding: utf-8 -*- 

import sublime, sublime_plugin

# Constants
PACKAGES_PATH = sublime.packages_path()


class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFFFF
    # 0x000000
    # 0xFFFFFFFF

	old = ""
	colored = False
	color_scheme = ""
	letters = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F', 'a', 'b', 'c', 'd', 'e', 'f']
	current_col = ""


    # check if col is a hexademical color code
	def isHexColor(self, col):
		# short, normal and alpha-channel support
		if not (len(col) in [4, 7, 9] and col[0] == '#'):
			return False
		for c in col[1:]:
			if c not in self.letters:
				return False
		return True

	def formatHex(self, col):
		zeroxcol = len(col) in [8, 10] and (col[0] + col[1]) == '0x'
		if zeroxcol:
			col = '#' + col[2:]
		return col

	def SetColor(self, view, color):
		# getting the color file path (cs)
		cs = view.settings().get('color_scheme')
		# does not support null color scheme yet
		if cs == "": return
		cs = cs[cs.find('/'):]

		# if color scheme has been changed - update one
		if self.color_scheme != cs:
			self.color_scheme = cs
			self.old = ""

		f = open(PACKAGES_PATH + self.color_scheme, 'r+')
		cont = f.read()
		n = cont.find("<key>selection</key>")
		cont1 = cont[n:]
		n1 = cont1.find("<string>")
		n2 = cont1.find("</string>")
		# set defauld color if needed
		if self.old == "":
			self.old = cont1[n1+8:n2]
		# main job
		oldcol = cont1[n1+8:n2]
		length = n2 - (n1+8)
		newlength = len(color)
		# wrighting back in file
		f.seek(n+n1+8)
		if length == newlength:
			f.write(color)
		elif length == 9 and newlength == 7:
			# clever hack (IDK really can i do it w\o any side effects)
			# TODO: figue out
			f.write(color)
			f.write("FF")
		else:
			# грустно, но надо переписывать весь файл
			f.write(color)
			f.write(cont[n+n2:])
		f.close()

	def on_selection_modified(self, view):
		selection = view.sel()
		# we dont do it with multiple selection
		if len(selection) != 1: return
		str = view.substr(selection[0])
		str = self.formatHex(str)
		if self.colored:
			if not self.isHexColor(str):
				self.colored = False
				self.SetColor(view, self.old)
				self.current_col = ""
			elif str != self.current_col:
				self.SetColor(view, str)
				self.current_col = str
		else:
			if self.isHexColor(str):
				self.colored = True
				self.SetColor(view, str)
				self.current_col = str
