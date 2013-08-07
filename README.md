#ColorHighlighter

_ColorHighlighter is a simple plugin for the Sublime Text 2, which unobtrusively previews hexadecimal color values by underlaying the selected hex codes._
![Description](http://f.cl.ly/items/0b471K1T0X3b3e1m2j1r/Screen%20Shot%202013-08-07%20at%2012.52.01%20PM.jpg)

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
    - `ctrl+shft+p` then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder

**Usage :**

Just click or move the cursor on the color code e.g. #FFFFFF and it'll be highlighted with its real color.
Two color representations are currently supported:
- Hexademical e.g. #RGB or #RRGGBB or #RRGGBBAA (you can use both upper and lower case letters)
- RBG or RGBA value e.g. rgb(rrr,ggg,bbb) or rgba(rrr,ggg,bbb,a.aaa) with decimal channel values.

!!! NOT IMPLEMENTED !!!
And two more you can enable in options:
- Usual hexademical numbers like RRGGBBAA.
- Hexademical numbers with prefix 0x like 0xRRGGBBAA

Named colors like "green", "black" and many others are also supported.

Both you can enable or disable from the menu Tools -> Color Highlighter.

**Note :**
This version is beta and although it works fine, it corrupts color scheme with additional values. The color scheme will still work, but it'll became bigger and bigger. Anyway, you always can restore the original color scheme file from the menu.

**TODO :**
- ST3 support.
- Highlighting all the colors at once.
- Run IO operations in another thread.
