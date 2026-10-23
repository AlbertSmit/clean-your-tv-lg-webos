#!/bin/sh
# Recover first; only an explicitly confirmed durable intent may resume Home.
exec /usr/bin/python3 /var/lib/clean-your-tv-root/runtime/cli.py boot
