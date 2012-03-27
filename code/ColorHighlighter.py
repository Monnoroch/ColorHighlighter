# -*- coding: utf-8 -*- 

import sublime, sublime_plugin

# Constants
PACKAGES_PATH = sublime.packages_path()

class ColorSelection(sublime_plugin.EventListener):
    #000000
    #FFFFFF

	old = ""
	colored = False

    # определить, является ли строка корректным шестнадцетеричным цветом
	def isHexColor(self, col):
		if not (len(col) >= 7 and col[0] == '#'):
			return False
		for c in col[1:]:
			if not (c in ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']):
				return False
		return True

	def SetColor(self, view, color):
		if self.old == "":
			self.colored = False
			self.old = self.GetColor(view)
		cs = view.settings().get('color_scheme')
		fol = cs.find('/')
		cs = cs[fol:]
		f = open(PACKAGES_PATH + cs, 'r+')
		cont = f.read()
		n = cont.find("<key>selection</key>")
		cont1 = cont[n:]
		n1 = cont1.find("<string>")
		n2 = cont1.find("</string>")
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
		return oldcol

	def GetColor(self, view):
		cs = view.settings().get('color_scheme')
		fol = cs.find('/')
		cs = cs[fol:]
		f = open(PACKAGES_PATH + cs, 'r')
		cont = f.read()
		f.close()
		n = cont.find("<key>selection</key>")
		cont1 = cont[n:]
		n1 = cont1.find("<string>")
		n2 = cont1.find("</string>")
		return cont1[n1+8:n2]

	def on_selection_modified(self, view):
		selection = view.sel()
		if len(selection) != 1: return
		str = view.substr(selection[0])
		if self.colored:
			if not self.isHexColor(str):
				self.SetColor(view, self.old)
				self.colored = False
		else:
			if self.isHexColor(str):
				self.SetColor(view, str)
				self.colored = True


