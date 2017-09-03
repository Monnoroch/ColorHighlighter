#!/usr/bin/env bash

set -e

echo "Running $0..."

PARSED=$(getopt -o "" --longoptions image:,name:,timeout: --name "$0" -- "$@")

eval set -- "$PARSED"
while true; do
    case "$1" in
        --image ) IMAGE_NAME="$2"; shift 2 ;;
        --name ) CONTAINER_NAME="$2"; shift 2 ;;
        --timeout ) TIMEOUT="$2"; shift 2 ;;
        * ) break ;;
    esac
done

if [[ ! ${IMAGE_NAME} ]] || [[ ! ${CONTAINER_NAME} ]] || [[ ! ${TIMEOUT} ]]; then
    echo "Error: Missing one or more of script arguments: \"image\", \"name\", \"timeout\"."
    exit 1
fi

docker run -d --rm --name "${CONTAINER_NAME}" "${IMAGE_NAME}" sleep "${TIMEOUT}"
workdir=$(docker exec -i "${CONTAINER_NAME}" pwd)
docker cp ./ "${CONTAINER_NAME}:${workdir}/"

packages_dirs=(
    "/root/.config/sublime-text-3/Packages"
    "/root/.config/sublime-text-2/Packages"
)
for packages in "${packages_dirs[@]}"; do
    docker exec -i "${CONTAINER_NAME}" mkdir ${packages}/ColorHighlighter
    docker exec -i "${CONTAINER_NAME}" mkdir ${packages}/0_test_plugin

    test_files=(
        __init__.py
        flushing_file.py
        main.py
    )

    for file in "${test_files[@]}"; do
        docker cp "./test_plugin/${file}" "${CONTAINER_NAME}:${packages}/0_test_plugin/${file}"
    done

    for file in *.py; do
        docker cp "./${file}" "${CONTAINER_NAME}:${packages}/ColorHighlighter/${file}"
    done
    docker cp "./elementtree" "${CONTAINER_NAME}:${packages}/ColorHighlighter/elementtree"

    file="ColorHighlighter.sublime-settings"
    docker cp "./${file}" "${CONTAINER_NAME}:${packages}/ColorHighlighter/${file}"
    docker exec "${CONTAINER_NAME}" rm "${packages}/ColorHighlighter/sublime.py"
done
