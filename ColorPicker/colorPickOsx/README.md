
# color-pick

Command line wrapper around OS X built in color picker.

## usages

`colorpick`

`colorpick -startColor ffff00ff -mode 3`

`colorpick ffff00ff`

`colorpick #ffff00ff`


Writes color in hex format to stdout:

`#ffff00ff`

On cancel / exit, nothing is written to stdout


Avalible modes:

    NSGrayModeColorPanel            = 0
    NSRGBModeColorPanel             = 1
    NSCMYKModeColorPanel            = 2
    NSHSBModeColorPanel             = 3
    NSCustomPaletteModeColorPanel   = 4
    NSColorListModeColorPanel       = 5
    NSWheelModeColorPanel           = 6
    NSCrayonModeColorPanel          = 7

## wishlist

 * Different formats (rgb, rgba, hsl)
