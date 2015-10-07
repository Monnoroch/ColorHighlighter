
# color-pick

Command line wrapper around OS X built in color picker.

## usage

`colorpick`

`colorpick -startColor ffff00 -mode 3`

Writes color in hex format to stdout

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
