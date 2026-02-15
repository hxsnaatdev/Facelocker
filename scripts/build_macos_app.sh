#!/usr/bin/env bash
set -euo pipefail

APP_NAME="FaceRecGuard"
VERSION="${1:-0.1.0}"
DIST_DIR="dist"
BUILD_DIR="build"

python -m pip install --upgrade pyinstaller

pyinstaller \
  --noconfirm \
  --windowed \
  --name "${APP_NAME}" \
  app/gui.py

mkdir -p "${DIST_DIR}/dmg"
DMG_PATH="${DIST_DIR}/${APP_NAME}-${VERSION}.dmg"

hdiutil create \
  -volname "${APP_NAME}" \
  -srcfolder "${DIST_DIR}/${APP_NAME}.app" \
  -ov \
  -format UDZO \
  "${DMG_PATH}"

shasum -a 256 "${DMG_PATH}"
echo "Built: ${DMG_PATH}"
