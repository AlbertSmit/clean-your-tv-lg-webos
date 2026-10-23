#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for test in tests/apps/*.cjs; do
  if [[ "$test" != *"/ui.cjs" ]]; then node "$test"; fi
done
node tests/renewal-core.cjs
node tests/renewal-transport.cjs
node tests/renewal-manager.cjs
node tests/renewal-storage.cjs
node tests/preview-bridge.cjs
node tests/helper-control.cjs
node tests/resume.cjs
node tests/controller-resume.cjs
for test in native/prototype/test-*.cjs; do node "$test"; done
mkdir -p build/tests
cc -std=c99 -Wall -Wextra -Werror native/prototype/filter.c native/prototype/test_filter.c -o build/tests/test-filter
build/tests/test-filter
for file in launcher/*.js native/app/*.js native/service/*.js renewal-service/*.js; do node --check "$file"; done

node root-edition/service/test-handlers.js
node root-edition/service/test-persistent.js
node root-edition/ui/test-exit.cjs
node root-edition/ui/test-settings.cjs
node root-edition/ui/test-persistent.cjs
node root-edition/ui/test-profile.cjs
node root-edition/ui/test-updates.cjs
for test in root-edition/tests/test_update_*.cjs; do node "$test"; done
for file in root-edition/ui/*.js; do node --check "$file"; done
for file in root-edition/updater/*.js; do node --check "$file"; done
python3 -m unittest discover -s root-edition/tests

python3 -m unittest discover -s tests/setup
python3 -m unittest discover -s tests/cytv
python3 -m unittest discover -s tests -p test_preview.py
for test in tests/updates/*.cjs; do node "$test"; done
for file in updater-service/*.js updater-app/*.js; do node --check "$file"; done
cmp launcher/user-data.js updater-service/user-data.js
