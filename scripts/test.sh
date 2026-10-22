#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node tests/helper-control.cjs
node tests/resume.cjs
node tests/controller-resume.cjs
for test in native/prototype/test-*.cjs; do node "$test"; done
mkdir -p build/tests
cc -std=c99 -Wall -Wextra -Werror native/prototype/filter.c native/prototype/test_filter.c -o build/tests/test-filter
build/tests/test-filter
for file in launcher/*.js native/app/*.js native/service/*.js; do node --check "$file"; done
