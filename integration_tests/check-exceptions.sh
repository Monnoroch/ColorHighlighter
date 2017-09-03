#!/usr/bin/env bash

echo "Running $0 $1..."

EXCEPTIONS_NUMBER=$(grep -c "Traceback" < "$1")
if [[ ${EXCEPTIONS_NUMBER} != 0 ]]; then
    exit 1
fi
