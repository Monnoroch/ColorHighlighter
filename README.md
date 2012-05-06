#ColorHighlighter

_ColorHighlighter is a simple plugin for the Sublime Text 2, which unobtrusively previews hexadecimal color values by underlaying the selected hex codes. Only **selected** hex codes show colored underlay._

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
    - `ctrl+shft+p` then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder

**Usage :**

Just click or move the cursor on the color code value e.g. #FFFFFF and it'll be highlighted with it's real color.
Two color representations are currently supported:
- Hexademical e.g. #RGB or #RRGGBB or #RRGGBBAA (you can use both capital and literal characters)
- RBG value e.g. rgb(rrr,ggg,bbb) with decimal channel values. 

**Note :**
This version is beta and although it works fine, it corrupts color scheme with additional values. THe color scheme still will work, but it will became bigger and bigger.