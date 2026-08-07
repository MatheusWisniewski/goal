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

# 3. Run PyInstaller
echo "Running PyInstaller..."
pyinstaller --noconfirm --onedir --windowed \
  --add-data "app.py:." \
  --hidden-import "llama_cpp" \
  --hidden-import "streamlit" \
  entrypoint.py

# 4. Create Platypus App Bundle (with dynamic version)
echo "Creating Platypus App..."
platypus \
  --name "DataLabeler" \
  --app-version "$VERSION" \
  --interface-type "Progress Bar" \
  --interpreter "/bin/bash" \
  --app-icon "AppIcon.icns" \
  --bundle-identifier "com.datalabeler.mac" \
  --files "app.py|models/gemma-2-2b-it-Q4_K_M.gguf|dist/entrypoint" \
  launcher.sh \
  DataLabeler.app

# 5. Package DMG (with dynamic filename & volume name)
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
  "DataLabeler.app"

echo "Build Complete: DataLabeler-v${VERSION}.dmg"