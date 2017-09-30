#!/usr/bin/env bash

echo "Running $0..."

export DISPLAY=:1.0

Xvfb :1 -screen 0 1024x768x16 &
XVFB_PID=$!

sleep 5

ci/run-integration-tests.sh
exitcode=$?

kill -9 "${XVFB_PID}"

exit $exitcode
