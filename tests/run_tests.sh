#!/usr/bin/env bash

echo "Running $0..."

test_files=(
    __init__.py
    sublime.py
    sublime_plugin.py
)

for file in "${test_files[@]}"; do
    mv "./tests/${file}" ./
done

py.test
exitcode=$?

for file in "${test_files[@]}"; do
    mv "${file}" ./tests/
done

exit $exitcode
