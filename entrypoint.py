import os
import sys
import shutil
import threading
import time
import webbrowser
import streamlit.web.cli as stcli

def setup_first_run():
    """Copies initial app.py and model files to Application Support if missing."""
    app_dir = os.path.expanduser("~/Library/Application Support/DataLabeler")
    models_dir = os.path.join(app_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Locate bundle root directory inside the compiled macOS .app
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    
    # Copy app.py on first launch
    local_app = os.path.join(app_dir, "app.py")
    bundle_app = os.path.join(bundle_dir, "app.py")
    if not os.path.exists(local_app) and os.path.exists(bundle_app):
        shutil.copy(bundle_app, local_app)

    # Copy Gemma model weights on first launch
    local_model = os.path.join(models_dir, "gemma-2-2b-it-Q4_K_M.gguf")
    bundle_model = os.path.join(bundle_dir, "models", "gemma-2-2b-it-Q4_K_M.gguf")
    if not os.path.exists(local_model) and os.path.exists(bundle_model):
        shutil.copy(bundle_model, local_model)

def open_browser():
    """Opens the user's default browser once Streamlit starts."""
    time.sleep(1.5)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    setup_first_run()
    
    app_dir = os.path.expanduser("~/Library/Application Support/DataLabeler")
    local_script = os.path.join(app_dir, "app.py")
    
    if not os.path.exists(local_script):
        local_script = os.path.join(os.path.dirname(__file__), "app.py")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Streamlit engine
    sys.argv = ["streamlit", "run", local_script, "--server.headless=true"]
    sys.exit(stcli.main())