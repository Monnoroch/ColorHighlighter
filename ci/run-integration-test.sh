#!/usr/bin/env bash

echo "Running $0 $1..."

$1
exitcode=$?

rm -r \
    /root/.config/sublime-text-3/Packages/User/Preferences.sublime-settings \
    /root/.config/sublime-text-3/Packages/User/ColorHighlighter \
    /root/.config/sublime-text-2/Packages/User/Preferences.sublime-settings \
    /root/.config/sublime-text-2/Packages/User/ColorHighlighter

exit $exitcode
