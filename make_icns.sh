#!/bin/bash
set -e

if [ ! -f "assets/app_icon.png" ]; then
    echo "Error: assets/app_icon.png not found."
    exit 1
fi

mkdir -p AppIcon.iconset
sips -z 16 16     assets/app_icon.png --out AppIcon.iconset/icon_16x16.png
sips -z 32 32     assets/app_icon.png --out AppIcon.iconset/icon_16x16@2x.png
sips -z 32 32     assets/app_icon.png --out AppIcon.iconset/icon_32x32.png
sips -z 64 64     assets/app_icon.png --out AppIcon.iconset/icon_32x32@2x.png
sips -z 128 128   assets/app_icon.png --out AppIcon.iconset/icon_128x128.png
sips -z 256 256   assets/app_icon.png --out AppIcon.iconset/icon_128x128@2x.png
sips -z 512 512   assets/app_icon.png --out AppIcon.iconset/icon_512x512.png
sips -z 1024 1024 assets/app_icon.png --out AppIcon.iconset/icon_512x512@2x.png

iconutil -c icns AppIcon.iconset
rm -rf AppIcon.iconset
echo "AppIcon.icns generated."