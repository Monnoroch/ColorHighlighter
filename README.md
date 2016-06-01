#ColorHighlighter

_ColorHighlighter is a plugin for the Sublime Text 2 and 3, which unobtrusively previews color values by underlaying the selected hex codes in different styles, coloring text or gutter icons. Also, plugin adds color picker, color format converter and less/sass/styl variables navigation to easily modify colors._

![Description](http://i.imgur.com/UPmEk09.png)

![Description](http://i.imgur.com/kl4joGA.png)

![Description](http://sametmax.com/wp-content/uploads/2013/04/hilight-color.gif)

![Description](http://sametmax.com/wp-content/uploads/2013/04/color-picker.gif)

**Installation :**

- **_Recommended_** - Using [Sublime Package Control](https://packagecontrol.io "Sublime Package Control")
    - <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder and then rename plugins directory from "ColorHighlighter" to "Color Highlighter"
- For gutter icons install [ImageMagick](http://www.imagemagick.org/)
- For color picker on linux install Qt5 framework.

**Usage :**

Just click or move the cursor (or multiple cursors) on the color code e.g. "#FFFFFF" or "rgba(255, 0, 0, 0.7)" or variable with color code value and it'll be highlighted with its real color.
These color formats are currently supported:
- All CSS color formats.
- Hexadecimal RGBA ("0xFFFFFFFF") or ("0xFFFF") and RGB ("0xFFFFFF") or ("0xFFF").
- Named colors like "green", "black" and many others.
- Less/sass/scss/stylus variables (supports @importing from another files recursively).
- [VAL, VAL, VAL] and [VAL, VAL, VAL, VAL] when editing e files. Where VAL can be one of the following:
  - An integer: from 0 to 255.
  - A float value from 0.0 to 1.0, you can also skip leading zero (like that: .25)
  - A percentage from 0% to 100%.

**Variables file :**
You can define a list or string field `color_variables_files` in your .sublime-project file to automatically include all less/sass/scss/stylus color variables from these files for every file you edit (for now, only absolute path is supported).
There is a deprecated but left for compatibility setting `color_variables_file`, which can only contain a string for a single file, not a list.

**Settings :**

You can choose the highliting style from:
- "Filled", "outlined", "none", "colored text" in ST2.
- "Filled", "outlined", "none", "underlined" (solid, strippled, squiggly), "colored text" in ST3.

You can also turn on highlighting all colors at once. This mode has own highlighting style, so you can highlight all colors with underline and selected colors with filled rect.

You can also enable icons, which will be shown in the gutter of a file (might not work in ST2).

You can always turn off default keybindings via main menu or settings.

**Color picker usage:**

Just put the cursor (or multiple cursors) on the color code and select "Choose color" in context menu (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>C</kbd>). Select the color in a popup color picker and all color codes under your cursors will change. The change will preserve exact code format, so if you select codes "#FFF" and "rgb(255,255,255)" and "white" and choose color "#FF0000", you get codes: "#F00" and "rgb(255,0,0)" and "red". Also, works with variables.

**Color converter usage:**

Just put the cursor (or multiple cursors) on the color code and select "Convert color" in context menu (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd>). Input a color format to use and press enter. The full list of all color formats is in the plugins settings file.
Format can be any format supported by this plugin, for example if you convert "rgb(255,255,255)" into format "hsv", you'll get "hsv(0, 0%, 100%)". Also works with named colors and variables.

Also, there is a Prev/Next color commands, triggered by <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>,</kbd> and <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>.</kbd> respectively to choose previous or next color format.

**Less/sass/scss/stylus variables navigation:**

Just put cursor on a variable, right click on it and press "Go to variable definition" and the plugin will open it. There is also a shortcut <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>D</kbd>.
