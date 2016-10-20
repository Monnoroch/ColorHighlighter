# ColorHighlighter
A plugin for the Sublime Text (2 and 3) for highlighting color values in an unobtrusive manner.

![underline highlighting preview][image-underline-preview]

## Features
 - [x] Customizable Highlighting of Colors
 - [x] Gutter Icons
 - [x] Color Picker
 - [x] Color Format Converter
 - [x] Less/SASS/SCSS/Stylus variable navigation

![gutter icons preview][image-gutter-dots-preview]

## Installation
With [Package Control][package-control] (Recommended):

1. Run “Package Control: Install Package” command
2. Find and install Color Highlighter plugin from the list
3. Just sit back every time an update is rolled out. Package Control will do the right thing.

Manually:

  1. Clone or Download the [git repo][project-url] into your Packages folder (Preferences > Browse Packages...)
  2. Rename the Plugin directory from "ColorHighlighter" to "Color Highlighter"
  3. Repeat this process each time an update is rolled out.

Dependencies:

  - For Gutter Icons, install [ImageMagick][imagemagick-url].
  - For Color Picker on Linux, install Qt5 framework.

## Usage
A color-value or variable is highlighted with it's color whenever the cursor enters it.

![underline highlighting preview][image-underline-preview]

### Supported Color Formats
  - All CSS color formats.
    - Hexadecimal colors: `0xRRGGBBAA`, `0xRRGGBB`, `0xRGBA`, `0xRGB`
    - RGB colors: `rgb(r, g, b)`
    - RGBA colors: `rgba(r, g, b, a)`
    - HSL colors: `hsl(h, s, l)`
    - HSLA colors: `hsla(h, s, l, a)`
    - Named colors: `black`, `white`, `green`
  - Less/SASS/SCSS/Stylus variables (supports @importing from another files recursively)
  - `[VAL, VAL, VAL]` and `[VAL, VAL, VAL, VAL]` when editing e files, where `VAL` can be one of the following:
    - An integer from `0` to `255`
    - A float from `0.0` to `1.0` (You may skip the leading zero as in `.25`)
    - A percentage from `0%` to `100%`

### Variables file
You may define a list or string `color_variables_files` in your `.sublime-project` to include all Less/SASS/SCSS/Stylus color variables from that file as context for every file you edit. (Currently, only absolute paths are supported).

> NOTE: The older `color_variables_file` is still supported but now deprecated. It can only contain a string for a single file, not a list.

```js
{
    "folders": [...],
    "color_variables_file": "/path/to/file",
    ...
}
```

### Color Picker usage
Place cursor(s) on a color-value(s). Press <kbd><kbd>Ctrl</kbd><kbd>Shift</kbd><kbd>C</kbd></kbd> or select "Choose color" in the context menu.

The Color Picker will pop up and the color you pick will replace the color(s) under the cursor(s). The replacement will preserve exact code format, so if `#FFF`, `rgb(255,255,255)` and `white` are selected and `#FF0000` is picked, the colours will be replaced as `#F00`, `rgb(255,0,0)` and `red`. As expected, this works with variables as well.

![color picker preview][image-color-picker]

### Color Format Converter usage
Place cursor(s) on a color-value(s). Press <kbd><kbd>Ctrl</kbd><kbd>Shift</kbd><kbd>A</kbd></kbd> or select "Convert color" in the context menu.

Select/Input a color format to use. The full list of all color formats is in the settings file. Format can be any format supported by this plugin, for example if you convert "rgb(255,255,255)" into format "hsv", you'll get "hsv(0, 0%, 100%)". As expected, this works with named colors and variables as well.

![color converter preview][image-color-converter]

Additionally, there are "Next Color" and "Previous Color" commands, triggered by <kbd><kbd>Ctrl</kbd><kbd>Shift</kbd><kbd>,</kbd></kbd> and <kbd><kbd>Ctrl</kbd><kbd>Shift</kbd><kbd>.</kbd></kbd> respectively to choose previous or next color format.

### Less/SASS/SCSS/Stylus variables navigation
Place cursor on a variable. Press <kbd><kbd>Ctrl</kbd><kbd>Alt</kbd><kbd>D</kbd></kbd> or select "Go to variable definition" in the context menu. The cursor will then be moved to the line of declaration of that variable. If the variable is declared in another, that file will be opened in a new view (tab).

![jump to variable definition preview][image-go-to-definition]

## Settings
ColorHighlighter is configurable via `ColorHighlighter.sublime-settings` like any other well-behaved package.

You can choose the highlighting style from:
`none` `text` `filled` `outlined` `underlined_solid` `underlined_strippled` `underlined_squiggly`

![colored text highlighting preview][image-colored-text-preview]

**NOTE**: Underlined styles are available in Sublime Text 3 only.

You can also turn on highlighting all colors at once. This mode has own highlighting style, so you can highlight all colors with underline and selected colors with filled rectangle.

![highlight all preview][image-highlight-all]

You can also enable icons, which will be shown in the gutter of a file (might not work in ST2).

You can always turn off default key-bindings via main menu or settings.

## Contributing
To contribute to the project, just head on over to the [Github Project][project-url].

Found something that doesn't work? Let us know by opening an issue.
Have an idea? Open up an issue and let's make it happen!
Found a typo? Send in a pull request.

Don't hesitate. :smile:

 [project-url]: https://github.com/Monnoroch/ColorHighlighter
 [package-control]: https://packagecontrol.io/installation
 [imagemagick-url]: http://www.imagemagick.org/

 [image-color-picker]: images/color-picker.gif
 [image-color-converter]: images/convert.gif
 [image-underline-preview]: images/underline-preview.gif
 [image-colored-text-preview]: images/colored-text-preview.gif
 [image-gutter-dots-preview]: images/dots.gif
 [image-go-to-definition]: images/go-to-definition.gif
 [image-highlight-all]: images/highlight-all.gif