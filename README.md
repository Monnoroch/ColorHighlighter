#ColorHighlighter

_ColorHighlighter is a plugin for the Sublime Text 2 and 3, which unobtrusively previews hexadecimal color values by underlaying the selected hex codes. Also, plugin adds color picker to easily modify colors._

![Description](http://i.imgur.com/aRtd2jf.png)

![Description](http://sametmax.com/wp-content/uploads/2013/04/hilight-color.gif)

![Description](http://sametmax.com/wp-content/uploads/2013/04/color-picker.gif)

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
    - `ctrl+shft+p` then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder

**Usage :**

Just click or move the cursor (or multiple cursors) on the color code e.g. #FFFFFF and it'll be highlighted with its real color.
These color formats are currently supported:
- Hexademical e.g. #RGB or #RGBA or #RRGGBB or #RRGGBBAA (you can use both upper and lower case letters)
- RBG or RGBA value e.g. rgb(VAL, VAL, VAL) or rgba(VAL, VAL, VAL, VAL) with decimal channel values.
- HSV or HSVA value e.g. hsv(VAL, VAL, VAL) or hsva(VAL, VAL, VAL, VAL) with decimal channel values.
- HSL or HSLA value e.g. hsl(VAL, VAL, VAL) or hsla(VAL, VAL, VAL, VAL) with decimal channel values.
- [VAL, VAL, VAL] and [VAL, VAL, VAL, VAL] when editing *.sublime-theme files.
- Named colors like "green", "black" and many others.
- Less/sass/scss variables (supports importing from another files).
- VAL can be the following text:
  - An integer: from 0 to 255 or from 0 to 360 for hue.
  - A float value from 0.0 to 1.0, you can also skip leading zero (like that: .25)
  - A percentage from 0% to 100%.

**Settings :**

You can choose the highliting style from:
- Filled, outlined in ST2.
- Filled, outlined, underlined (solid, strippled, squiggly) in ST3.

You can also turn on highlighting all colors at once, but it would highlight only constant colors, no variables. This mode has own highlighting style, so you can highlight all colors with underline and selected colors with filled rect.

**Color picker usage:**

Just put the cursor (or multiple cursors) on the color code and select "Choose color" in context menu. Select the color in a popup color picker and all color codes under your cursors will change. The change will preserve exact code format, so if you select two codes "#FFF" and "rgb(255,255,255)" and choose color #FF0000, in the end you get two codes like that: "#FF00FF" and "rgb(255,0,0)".


**ACHTUNG!!! :**

Color picker works only on linux x64 and win64 with installed Qt (just for a couple of days, untill we build it on other systems).

