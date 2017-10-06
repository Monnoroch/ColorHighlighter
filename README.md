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
    - <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select `Package Control: Install Package`
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

### Blocks

Highlighting colors with blocks will display colored blocks right near highlighted colors.
These blocks cause text reflow.
To enable highlighting colors with underline blocks go to
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Highlight colors with blocks`
and choose one of `To the right of the color`, `To the left of the color`, `Below the color`.
These are options are self-explanatory.

For `Below the color` the block will be the same size that the color code is. For `To the right of the color` and
`To the left of the color` the block size can be configured with the `length` parameter which defines the size of
the block in characters.

Going to `Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Highlight colors with blocks`
and selecting `None` will disable it.

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
highlight selected colors with blocks to the right of the color and highlight colors one hovers over with inline blocks.

## Color picker

Just put the cursor (or multiple cursors) where you want the color and and select "Insert color with color picker"
in context menu (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>C</kbd>).
Select the color in a popup color picker and it will be inserted in place of all your cursors.
If some of your cursors are in existing colors, these colors will be replaces with a newly selected one.

## Color converter

Just put the cursor (or multiple cursors) on the color code and select "Convert color to the next format" in context menu (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>,</kbd>) or "Convert color to the previous format" in context menu (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>.</kbd>).
This will convert colors under cursors between different supported color formats.

## Variables highlighting

THIS FEATURE CURRENTLY DOESN'T WORK.

It was removed because it didn't work very well, was slow and buggy.
Right now I'm in the process of searching for ways to implement it nicely, but it's not ready yet.
I also plan to include color functions and native CSS variables into the release of this feature.
Please be patient.

## FAQ

#### My plugin settings are gone!

The settings file in the 8.0 has a completely different structure and way more features to configure.
Because of it it's incompatible with the old one.
To eliminate weird migration bugs I've decided to delete user settings file upon migration to the new version.
The settings are only deleted this once, so you can reconfigure the plugin again after update and the settings won't
disappear again.

#### The plugin doesn't work in HTML/JS/VUE/OTHER files

Yes, it does.
Highlighting colors is just disabled by default in all files but stylesheets.
To enable highlighting colors in files with any extension you need to modify `file_extensions` setting
and add the required extension there.
You can also put `"all"` there and the plugin will be enabled for all files.
If you have enabled some extensions before, they need to be reenabled due to the previous section.

#### Inline color highlighting works incorrectly

Inline color highlighting is not guaranteed to be compatible with any plugin that generates or changes color schemes,
such as `SublimeLinter`. If you use one of those plugins you have to either disable them completely, or configure them
to not modify the color scheme or configure Color Highlighter to not modify the color scheme, which basically means
disabling inline color highlighting.

##### I don't have any other plugin that modifies the color scheme and inline highlighting still works incorrectly

Due to a Sublime Text not ordering added regions deterministically enabling both text and non-text inline highlihgting
at the same time might work properly. For example, if you select `Text` in
`Tools > Color Highlighter > Color Highlighters > Highlight colors in all text > Inline highlighting style`
and `Filled` in
`Tools > Color Highlighter > Color Highlighters > Highlight colors in selected text > Inline highlighting style`
it might not work all the time. If you close/open the file a few times and sometimes it's working fine and sometimes it
isn't, this is exactly this issue.

**Donate**

Thank you guys for all your support, I couldn't have done it wihout your contributions. Every little bit helps!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=C2L27SE4YDFAC)

[pc-image]: https://img.shields.io/packagecontrol/dt/Color%20Highlighter.svg
[pc-link]: https://packagecontrol.io/packages/Color%20Highlighter
