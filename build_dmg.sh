#!/bin/bash
set -e

if [ ! -f "version.json" ]; then
    echo "Error: version.json not found."
    exit 1
fi

VERSION=$(python3 -c "import json; print(json.load(open('version.json'))['version'])")
echo "Starting build for Goal Data Labeler v${VERSION}..."

echo "Generating ICNS Icon..."
chmod +x make_icns.sh
./make_icns.sh

echo "Running PyInstaller (Universal Binary: Apple Silicon + Intel)..."
pyinstaller --noconfirm --clean --windowed \
  --target-arch universal2 \
  --name "Goal Data Labeler" \
  --icon "AppIcon.icns" \
  --add-data "app.py:." \
  --hidden-import "llama_cpp" \
  --hidden-import "streamlit" \
  entrypoint.py

echo "Embedding Model into App Bundle..."
APP_RESOURCES="dist/Goal Data Labeler.app/Contents/Resources"
mkdir -p "$APP_RESOURCES/models"

if [ -f "models/gemma-2-2b-it-Q4_K_M.gguf" ]; then
    cp "models/gemma-2-2b-it-Q4_K_M.gguf" "$APP_RESOURCES/models/"
fi
cp "app.py" "$APP_RESOURCES/"

echo "Packaging DMG..."
create-dmg \
  --volname "Goal Data Labeler v${VERSION} Installer" \
  --volicon "AppIcon.icns" \
  --window-size 660 400 \
  --icon-size 100 \
  --icon "Goal Data Labeler.app" 180 170 \
  --app-drop-link 480 170 \
  --overwrite \
  "GoalDataLabeler-v${VERSION}.dmg" \
  "dist/Goal Data Labeler.app"

echo "Build Complete: GoalDataLabeler-v${VERSION}.dmg"