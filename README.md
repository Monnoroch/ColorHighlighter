#ColorHighlighter

_ColorHighlighter is a plugin for the Sublime Text 2, which unobtrusively previews hexadecimal color values by underlaying the selected hex codes._
![Description](http://f.cl.ly/items/0b471K1T0X3b3e1m2j1r/Screen%20Shot%202013-08-07%20at%2012.52.01%20PM.jpg)

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
    - `ctrl+shft+p` then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder

**Usage :**

Just click or move the cursor on the color code e.g. #FFFFFF and it'll be highlighted with its real color.
Two color representations are currently supported:
- Hexademical e.g. #RGB or #RGBA or #RRGGBB or #RRGGBBAA (you can use both upper and lower case letters)
- RBG or RGBA value e.g. rgb(rrr, ggg, bbb) or rgba(rrr, ggg, bbb, aaa) or rgba(rrr, ggg, bbb, 0.aaa) with decimal channel values.
- [rrr, ggg, bbb, aaa] and [rrr, ggg, bbb, 0.aaa] when editing *.sublime-theme files.
- Named colors like "green", "black" and many others.
- Less/sass/scss variables (supports importing from another files).

**TODO :**
- Highlighting all the colors at once.
