import os
import sys
import json
import requests
import pandas as pd
import streamlit as st
from llama_cpp import Llama

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/matheuswisniewski/goal/main/version.json"

APP_DIR = os.path.expanduser("~/Library/Application Support/GoalDataLabeler")
LOCAL_APP_PATH = os.path.join(APP_DIR, "app.py")

st.set_page_config(
    page_title="Goal Data Labeler",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Update System ---
def fetch_remote_version():
    try:
        res = requests.get(VERSION_URL, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

def apply_update(script_url):
    try:
        res = requests.get(script_url, timeout=5)
        if res.status_code == 200:
            os.makedirs(APP_DIR, exist_ok=True)
            with open(LOCAL_APP_PATH, "w", encoding="utf-8") as f:
                f.write(res.text)
            return True
    except Exception as e:
        st.error(f"Update failed: {e}")
    return False

# Sidebar Updates
with st.sidebar:
    st.header("⚙️ Settings")
    st.caption(f"Installed Version: **v{CURRENT_VERSION}**")
    
    if st.button("🔄 Check for Updates", use_container_width=True):
        with st.spinner("Checking..."):
            remote_data = fetch_remote_version()
            if remote_data and remote_data.get("version", CURRENT_VERSION) > CURRENT_VERSION:
                st.session_state["update_available"] = remote_data
                st.session_state["update_status_msg"] = None
            else:
                st.session_state["update_available"] = None
                st.session_state["update_status_msg"] = "✅ Running latest version!"

    if st.session_state.get("update_status_msg"):
        st.info(st.session_state["update_status_msg"])

    if st.session_state.get("update_available"):
        info = st.session_state["update_available"]
        st.warning(f"🎉 **Update Available: v{info['version']}**")
        st.write(info.get("notes", ""))
        
        col1, col2 = st.columns(2)
        if col1.button("✅ Update", type="primary"):
            if apply_update(info["script_url"]):
                st.success("Updated! Refreshing...")
                st.session_state.clear()
                st.rerun()
        if col2.button("❌ Dismiss"):
            st.session_state["update_available"] = None
            st.rerun()

# --- Model Loading with Intel Fallback ---
@st.cache_resource
def load_gemma():
    model_path = os.path.join(APP_DIR, "models", "gemma-2-2b-it-Q4_K_M.gguf")
    if not os.path.exists(model_path):
        model_path = "./models/gemma-2-2b-it-Q4_K_M.gguf"
        
    try:
        # Try GPU / Metal Acceleration (Apple Silicon or Intel Macs with Metal)
        return Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1, verbose=False)
    except Exception:
        # Fallback to CPU execution for older Intel Macs
        return Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=0, verbose=False)

try:
    llm = load_gemma()
except Exception as e:
    st.error(f"Model file missing. Place `gemma-2-2b-it-Q4_K_M.gguf` in `./models/`: {e}")
    st.stop()

# --- Helper Functions ---
def build_prompt(text_val, rule_desc, output_type, enums):
    if output_type == "Categorical / Enum":
        enum_str = ", ".join([f'"{e}"' for e in enums if e.strip()])
        constraint = f"Output MUST be exactly one of: [{enum_str}]."
    elif output_type == "Boolean (Yes/No)":
        constraint = "Output MUST be 'True' or 'False'."
    elif output_type == "Number":
        constraint = "Output MUST be a single numeric value."
    else:
        constraint = "Output should be a concise summary."

    return f"""<start_of_turn>user
Task: {rule_desc}
Constraint: {constraint}
Text: "{text_val}"
Return ONLY valid JSON with key "label". Example: {{"label": "VALUE"}}<end_of_turn>
<start_of_turn>model
"""

def process_label(prompt):
    res = llm(prompt, max_tokens=60, temperature=0.0, stop=["<end_of_turn>"])
    raw = res["choices"][0]["text"].strip()
    try:
        return str(json.loads(raw).get("label", raw))
    except Exception:
        return raw.replace('{"label":', '').replace('}', '').replace('"', '').strip()

# --- UI Flow ---
st.title("🏷️ Goal Data Labeler")
st.caption("Powered by Gemma 2 • Offline Local Intelligence")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("1. Data Preview")
    st.dataframe(df.head(4), use_container_width=True)

    st.subheader("2. Configure Labeling Rules")
    
    if "column_configs" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
        st.session_state["current_file"] = uploaded_file.name
        st.session_state["column_configs"] = {
            col: {
                "active": False,
                "description": f"Classify content for {col}",
                "output_type": "Categorical / Enum",
                "enums": ["POSITIVE", "NEGATIVE", "NEUTRAL"]
            } for col in df.columns
        }

    active_rules = {}
    for col in df.columns:
        cfg = st.session_state["column_configs"][col]
        with st.expander(f"📌 Column: **{col}**", expanded=cfg["active"]):
            cfg["active"] = st.checkbox("Enable", value=cfg["active"], key=f"chk_{col}")
            if cfg["active"]:
                cfg["description"] = st.text_area("Instruction:", value=cfg["description"], key=f"desc_{col}")
                cfg["output_type"] = st.selectbox(
                    "Output Type:",
                    ["Categorical / Enum", "Free-Form Text", "Boolean (Yes/No)", "Number"],
                    index=["Categorical / Enum", "Free-Form Text", "Boolean (Yes/No)", "Number"].index(cfg["output_type"]),
                    key=f"type_{col}"
                )

                if cfg["output_type"] == "Categorical / Enum":
                    updated_enums = []
                    for i, enum_val in enumerate(cfg["enums"]):
                        c1, c2 = st.columns([0.85, 0.15])
                        val = c1.text_input(f"Option {i+1}", value=enum_val, key=f"enum_{col}_{i}", label_visibility="collapsed")
                        if c2.button("🗑️", key=f"del_{col}_{i}"):
                            cfg["enums"].pop(i)
                            st.rerun()
                        else:
                            updated_enums.append(val)
                    cfg["enums"] = updated_enums
                    if st.button("➕ Add Option", key=f"add_{col}"):
                        cfg["enums"].append("NEW_OPTION")
                        st.rerun()

                active_rules[col] = cfg

    st.subheader("3. Execute Job")
    if active_rules and st.button("🚀 Start Labeling", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status = st.empty()
        labeled_df = df.copy()
        
        for idx, row in df.iterrows():
            for col_name, rule_cfg in active_rules.items():
                val = str(row[col_name]) if pd.notna(row[col_name]) else ""
                if not val.strip():
                    labeled_df.loc[idx, f"{col_name}_label"] = ""
                    continue
                
                prompt = build_prompt(val, rule_cfg["description"], rule_cfg["output_type"], rule_cfg["enums"])
                labeled_df.loc[idx, f"{col_name}_label"] = process_label(prompt)
            
            progress_bar.progress((idx + 1) / len(df))
            status.text(f"Processing row {idx + 1} of {len(df)}...")

        status.success("✅ Complete!")
        st.dataframe(labeled_df.head(10), use_container_width=True)
        st.download_button("📥 Download Labeled CSV", labeled_df.to_csv(index=False).encode('utf-8'), f"labeled_{uploaded_file.name}", "text/csv")