# ColorHighlighter

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=C2L27SE4YDFAC)
[![Package Control Downloads][pc-image]][pc-link]

_ColorHighlighter is a plugin for the Sublime Text 2 and 3, which unobtrusively previews color values by underlaying the selected hex codes in different styles, coloring text or gutter icons. Also, plugin adds color picker, color format converter to easily modify colors._

![Description](http://i.imgur.com/UPmEk09.png)

![Description](http://i.imgur.com/kl4joGA.png)

![Description](http://sametmax.com/wp-content/uploads/2013/04/hilight-color.gif)

![Description](http://sametmax.com/wp-content/uploads/2013/04/color-picker.gif)

## Installation

- **_Recommended_** - Using [Sublime Package Control](https://packagecontrol.io "Sublime Package Control")
    - ++ctrl+shift+p++ then select `Package Control: Install Package`
    - install `Color Highlighter`
- Alternatively, download the package from [GitHub](https://github.com/Monnoroch/ColorHighlighter "ColorHighlighter") into your `Packages` folder.
- For gutter icons install [ImageMagick](http://www.imagemagick.org/). To configure ImageMagick, update `icon_factory.convert_command` plugin setting.

## Color Highlighting styles

There are three color highlighting styles: inline highlighting, underline blocks, and gutter icons.

### Gutter icons

To enable highlighting colors with gutter icons go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Gutter icon style` and select `Circle` or `Square`.
Highlighting colors with gutter icons requires ImageMagick to be installed (see the installation section).
Going to `Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Gutter icon style` and selecting `None` will disable it.

This mode can cause pauses when opening big files for the first time with "highlihgt everything" mode because
the plugin needs to create icons for all newly encountered colors.

### Underline blocks

Highlighting colors with underline blocks will display colored blocks right under highlighted colors.
These blocks cause text reflow.
To enable highlighting colors with underline blocks go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text` and click `Highlight colors with blocks`.
Clicking on this setting again will disable it.

### Inline highlighting

Inline color highlighting itself has several styles.
All of them require Color Scheme modification, so when this mode is enabled the view's color scheme is changed to a fake one,
which is a copy of the real color scheme, but augmented with the plugin-specific definitions.
To disable inline highlighting  go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Inline highlighting style` and select `None`.

##### Inline blocks

Highlighting colors with inline blocks will display colored blocks right on top of highlighted colors.
To enable highlighting colors with inline blocks go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Inline highlighting style` and select `Filled`.

##### Colored text

Highlighting colors with colored text will make colors text be rendered with that color.
To enable highlighting colors with colored text go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Inline highlighting style` and select `Text`.

##### Outline and underline styles

If one wants color highlighting to be more subtle that one with inline blocks he can select one of
`Outlined`, `Underlined solid`, `Underlined strippled`, `Underlined squiggly` styles in
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Inline highlighting style` menu.

## Color Highlighting modes

#### Highlight everything

In this mode the plugin parses the whole file and highlights all colors it can find.
Highlighting style settings for that mode are in `Tools > Color Highlighter > Color Highlighters > Highlight colors in all text`.

This mode can cause pauses when opening big files because the plugin needs to parse the whole file.

#### Highlight selection

In this mode the plugin highlights colors under the cursor. It supports multiple selections as well.
Highlighting style settings for that mode are in `Tools > Color Highlighter > Color Highlighters > Highlight colors in selected text`.

#### Highlight when hovering

In this mode the plugin highlights colors when one hovers over them with the mouse cursor.
Highlighting style settings for that mode are in `Tools > Color Highlighter > Color Highlighters > Highlight colors when hovering the cursor above them`.

#### Combined

These three modes can be combined in any possible way.
The settings for all three modes are completely independent and can be configured all at once.
For example, the default settings are to highlight all colors with gutter icons and with colored text,
highlight selected colors with underline blocks and highlight colors one hovers over with inline blocks.

## Color picker

Just put the cursor (or multiple cursors) where you want the color and and select "Insert color with color picker"
in context menu (or press ++ctrl+shift+c++).
Select the color in a popup color picker and it will be inserted in place of all your cursors.
If some of your cursors are in existing colors, these colors will be replaces with a newly selected one.

## Color converter

Just put the cursor (or multiple cursors) on the color code and select "Convert color to the next format" in context menu (or press ++ctrl+shift+comma++) or "Convert color to the previous format" in context menu (or press ++ctrl+shift+period++).
This will convert colors under cursors between different supported color formats.

## Variables highlighting

THIS FEATURE CURRENTLY DOESN'T WORK.

It was removed because it didn't work very well, was slow and buggy.
Right now I'm in the process of searching for ways to implement it nicely, but it's not ready yet.
I also plan to include color functions and native CSS variables into the release of this feature.
Please be patient.

**Donate**

Thank you guys for all your support, I couldn't have done it wihout your contributions. Every little bit helps!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=C2L27SE4YDFAC)

[pc-image]: https://img.shields.io/packagecontrol/dt/Color%20Highlighter.svg
[pc-link]: https://packagecontrol.io/packages/Color%20Highlighter
