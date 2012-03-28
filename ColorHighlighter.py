# -*- coding: utf-8 -*- 

import sublime, sublime_plugin

# Constants
PACKAGES_PATH = sublime.packages_path()


class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFF

	old = ""
	colored = False
	color_scheme = ""
	letters = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F', 'a', 'b', 'c', 'd', 'e', 'f']

    # check if col is a hexademical color code
	def isHexColor(self, col):
		if not (len(col) > 1 and col[0] == '#'):
			return False
		for c in col[1:]:
			if c not in self.letters:
				return False
		return True

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
		if length == newlength:
			f.seek(n+n1+8)
			f.write(color)
		else:
			# грустно, но надо переписывать весь файл
			f.seek(n+n1+8)
			f.write(color)
			f.write(cont[n+n2:])
		f.close()

	def on_selection_modified(self, view):
		selection = view.sel()
		# we dont do it with multiple selection
		if len(selection) != 1: return
		str = view.substr(selection[0])
		if self.colored:
			if not self.isHexColor(str):
				self.colored = False
				self.SetColor(view, self.old)
		else:
			if self.isHexColor(str):
				self.colored = True
				self.SetColor(view, str)
				
