import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    app_dir = os.path.expanduser("~/Library/Application Support/DataLabeler")
    local_script = os.path.join(app_dir, "app.py")
    
    # Use locally updated app.py if available, otherwise fallback to bundled app.py
    if not os.path.exists(local_script):
        local_script = os.path.join(os.path.dirname(__file__), "app.py")

    sys.argv = ["streamlit", "run", local_script, "--server.headless=true"]
    sys.exit(stcli.main())