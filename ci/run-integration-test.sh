#!/usr/bin/env bash

echo "Running $0 $1..."

$1
exitcode=$?

rm -r \
    /root/.config/sublime-text-3/Packages/User/Preferences.sublime-settings \
    /root/.config/sublime-text-3/Packages/User/color_highlighter \
    /root/.config/sublime-text-2/Packages/User/Preferences.sublime-settings \
    /root/.config/sublime-text-2/Packages/User/color_highlighter

exit $exitcode
