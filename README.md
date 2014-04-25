#ColorHighlighter

_ColorHighlighter is a plugin for the Sublime Text 2 and 3, which unobtrusively previews hexadecimal color values by underlaying the selected hex codes in different styles and icons. Also, plugin adds color picker, color format converter and less/sass variables navigation to easily modify colors._

![Description](http://i.imgur.com/UPmEk09.png)

![Description](http://sametmax.com/wp-content/uploads/2013/04/hilight-color.gif)

![Description](http://sametmax.com/wp-content/uploads/2013/04/color-picker.gif)

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
    - `ctrl+shft+p` then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder
- For icons install [ImageMagick](http://www.imagemagick.org/)
- For color picker on linux install Qt5 framework.

**Usage :**

Just click or move the cursor (or multiple cursors) on the color code e.g. #FFFFFF and it'll be highlighted with its real color.
These color formats are currently supported:
- Hexademical e.g. #RGB or #RGBA or #RRGGBB or #RRGGBBAA (you can use both upper and lower case letters)
- RBG or RGBA value e.g. rgb(VAL, VAL, VAL) or rgba(VAL, VAL, VAL, VAL) with decimal channel values.
- HSV or HSVA value e.g. hsv(HVAL, VAL, VAL) or hsva(HVAL, VAL, VAL, VAL) with decimal channel values.
- HSL or HSLA value e.g. hsl(HVAL, VAL, VAL) or hsla(HVAL, VAL, VAL, VAL) with decimal channel values.
- [VAL, VAL, VAL] and [VAL, VAL, VAL, VAL] when editing *.sublime-theme files.
- Named colors like "green", "black" and many others.
- Less/sass/scss variables (supports importing from another files).
- VAL can be the following text:
  - An integer: from 0 to 255.
  - A float value from 0.0 to 1.0, you can also skip leading zero (like that: .25)
  - A percentage from 0% to 100%.
- HVAL can be the following text:
  - An integer: from 0 to 360 for hue.
  - A float value from 0.0 to 1.0, you can also skip leading zero (like that: .25)
  - A percentage from 0% to 100%.

**Settings :**

You can choose the highliting style from:
- Filled, outlined in ST2.
- Filled, outlined, underlined (solid, strippled, squiggly) in ST3.

You can also turn on highlighting all colors at once. This mode has own highlighting style, so you can highlight all colors with underline and selected colors with filled rect.

You can also enable icons, which will be shown in the gutter of a file.

**Color picker usage:**

Just put the cursor (or multiple cursors) on the color code and select "Choose color" in context menu (or press `ctrl+shift+c`). Select the color in a popup color picker and all color codes under your cursors will change. The change will preserve exact code format, so if you select two codes "#FFF" and "rgb(255,255,255)" and choose color #FF0000, in the end you get two codes like that: "#FF00FF" and "rgb(255,0,0)".

**Color converter usage:**

Just put the cursor (or multiple cursors) on the color code and select "Convert color" in context menu (or press `ctrl+shift+v`). Input a color format to use and press enter.
Format can be any format supported by this plugin, for example if you convert rgb(255,255,255) into format hsv(1,1%,1%), you'll get hsv(360, 100%, 100%). Also works with named colors (both ways).

Also, there is a Next color command, triggered by `ctrl+shift+n` to choose next color format.

**Less/sass variables navigation:**

Just put cursor on a variable, right click on it and press "Go to variable definition" and the plugin will open it.


**ACHTUNG!!! :**

Color picker has a bug on OSX, i fixed it, but can't rebuild the binary to apply this fix.

