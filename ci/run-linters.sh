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

docker exec -i "${container_name}" /opt/linters-system/generated/run-linux.sh
