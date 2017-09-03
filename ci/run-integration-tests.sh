#!/usr/bin/env bash

set -e

echo "Running $0..."

ci/run-integration-test.sh integration_tests/st3/test-empty.sh
ci/run-integration-test.sh integration_tests/st3/test-white.sh
ci/run-integration-test.sh integration_tests/st2/test-empty.sh
