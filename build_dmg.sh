#!/bin/bash
set -e

# 1. Read version dynamically from version.json
if [ ! -f "version.json" ]; then
    echo "Error: version.json not found."
    exit 1
fi

VERSION=$(python3 -c "import json; print(json.load(open('version.json'))['version'])")
echo "Starting build for DataLabeler v${VERSION}..."

# 2. Generate ICNS Icon
echo "Generating ICNS Icon..."
chmod +x make_icns.sh
./make_icns.sh

# 3. Run PyInstaller (Builds dist/DataLabeler.app directly)
echo "Running PyInstaller..."
pyinstaller --noconfirm --clean --windowed \
  --name "DataLabeler" \
  --icon "AppIcon.icns" \
  --add-data "app.py:." \
  --hidden-import "llama_cpp" \
  --hidden-import "streamlit" \
  entrypoint.py

# 4. Embed Gemma Model & Scripts into .app Resources
echo "Embedding Model into App Bundle..."
APP_RESOURCES="dist/DataLabeler.app/Contents/Resources"
mkdir -p "$APP_RESOURCES/models"

if [ -f "models/gemma-2-2b-it-Q4_K_M.gguf" ]; then
    cp "models/gemma-2-2b-it-Q4_K_M.gguf" "$APP_RESOURCES/models/"
fi
cp "app.py" "$APP_RESOURCES/"

# 5. Package DMG
echo "Packaging DMG..."
create-dmg \
  --volname "DataLabeler v${VERSION} Installer" \
  --volicon "AppIcon.icns" \
  --window-size 660 400 \
  --icon-size 100 \
  --icon "DataLabeler.app" 180 170 \
  --app-drop-link 480 170 \
  --overwrite \
  "DataLabeler-v${VERSION}.dmg" \
  "dist/DataLabeler.app"

echo "Build Complete: DataLabeler-v${VERSION}.dmg"