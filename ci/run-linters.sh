#!/usr/bin/env bash

set -e

echo "Running $0..."

PARSED=$(getopt -o "" --longoptions container: --name "$0" -- "$@")

eval set -- "$PARSED"
while true; do
    case "$1" in
        --container ) container_name="$2"; shift 2 ;;
        * ) break ;;
    esac
done

if [[ ! ${container_name} ]]; then
    echo "Error: Missing \"container\" script argument."
    exit 1
fi

ENDLINECHECK_EXCLUDE="ColorPicker/ColorPicker_linux_x32"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/ColorPicker_linux_x64"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/ColorPicker_osx_x64"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/ColorPicker_win.exe"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/winapi/Cyotek.Windows.Forms.ColorPicker/Resources/eyedropper.cur"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/winapi/Cyotek.Windows.Forms.ColorPicker/cyopublic.snk"
ENDLINECHECK_EXCLUDE="$ENDLINECHECK_EXCLUDE:ColorPicker/winapi/Sample-Palettes/background.lbm"

docker exec -e ENDLINECHECK_EXCLUDE="${ENDLINECHECK_EXCLUDE}" -i "${container_name}" \
    /opt/linters-system/generated/run-linux.sh
