#!/bin/sh
set -eu
if [ -e /var/lib/clean-your-tv-root/python-launcher ] || [ -L /var/lib/clean-your-tv-root/python-launcher ] || [ -e /var/lib/clean-your-tv-root/python-runtime.json ]; then
  exec /var/lib/clean-your-tv-root/python-launcher /var/lib/clean-your-tv-root/runtime/cli.py boot
fi
exec /usr/bin/python3 /var/lib/clean-your-tv-root/runtime/cli.py boot
