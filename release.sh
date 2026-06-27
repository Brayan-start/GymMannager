#!/usr/bin/env bash
# Render Release Command: runs db.create_all() + seed on first deploy.
# This runs AFTER the build (pip install) but BEFORE the web process starts.

set -e  # exit on error

echo "[release.sh] Setting FLASK_ENV=production and running seed..."
export FLASK_ENV=production
python seed.py
echo "[release.sh] Done."
