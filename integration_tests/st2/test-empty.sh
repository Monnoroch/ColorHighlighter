#!/usr/bin/env bash

echo "Running $0..."

/opt/sublime_text_2/sublime_text integration_tests/empty.css &

sleep 7

killall -9 sublime_text

set -e

test_dir=integration_tests/tmp
rm -rf "${test_dir}"
mkdir -p "${test_dir}"
log_file="${test_dir}"/sublime_text.log

mv /opt/sublime_text.log "${log_file}"

echo "Log:"
cat "${log_file}"

integration_tests/check-exceptions.sh "${log_file}"

filtered_log_file="${test_dir}"/sublime_text_filtered.log
set +e
grep "ColorHighlighter:" < "${log_file}" > "${filtered_log_file}"
set -e

expected_log_file=integration_tests/st2/empty.expected.log
cmp -s "${filtered_log_file}" "${expected_log_file}"
