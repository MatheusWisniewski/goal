@st.cache_resource
def load_gemma():
    model_path = os.path.join(APP_DIR, "models", "gemma-2-2b-it-Q4_K_M.gguf")
    if not os.path.exists(model_path):
        model_path = "./models/gemma-2-2b-it-Q4_K_M.gguf"
        
    # Metal Acceleration for Apple Silicon
    return Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1, verbose=False)