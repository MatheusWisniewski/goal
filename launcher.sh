#!/bin/bash
RESOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Library/Application Support/DataLabeler"

mkdir -p "$APP_DIR/models"

# Copy initial model and app file on first launch
if [ ! -f "$APP_DIR/app.py" ]; then
    cp "$RESOURCE_DIR/app.py" "$APP_DIR/app.py"
fi

if [ ! -f "$APP_DIR/models/gemma-2-2b-it-Q4_K_M.gguf" ] && [ -f "$RESOURCE_DIR/models/gemma-2-2b-it-Q4_K_M.gguf" ]; then
    cp "$RESOURCE_DIR/models/gemma-2-2b-it-Q4_K_M.gguf" "$APP_DIR/models/"
fi

# Launch backend
"$RESOURCE_DIR/entrypoint" &
SERVER_PID=$!

until curl -s http://localhost:8501 > /dev/null; do
    sleep 0.5
done

open "http://localhost:8501"
wait $SERVER_PID