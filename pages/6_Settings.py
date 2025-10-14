# File: pages/6_Settings.py
import streamlit as st
import os
import sys
from dotenv import load_dotenv, dotenv_values, set_key
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.translator import initialize_state

load_dotenv()
initialize_state()

st.set_page_config(page_title="Settings", layout="wide")
st.title(f"⚙️ {'Application Settings'}")
st.markdown("Configure the AI models used by the application.")

current_settings = load_settings()
available_local_models = ai_services.get_available_lm_studio_models()

PROVIDER_OPTIONS = {
    "Local (LM Studio)": "local",
    "OpenAI": "openai"
}

# 儲存不同 provider 下最近一次填過的 model 名稱，以便切換方便
def get_model_val(serv, default_local='', default_openai=''):
    saved = current_settings.get(serv, {})
    local_val  = saved.get('local_model',  saved.get('model', default_local))
    openai_val = saved.get('openai_model', saved.get('model', default_openai))
    return local_val, openai_val

with st.form("settings_form"):
    
    # --- Vision Service Configuration ---
    st.header("Vision Service (for Spec Sheets & Tags)")
    
    current_vision_provider = current_settings.get("vision_service", {}).get("provider", "local")
    selected_vision_provider_name = st.radio(
        "Select Vision Provider",
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_settings.get("vision_service", {}).get("provider", "local")),
        key="vision_provider_selector"
    )
    selected_vision_provider = PROVIDER_OPTIONS[selected_vision_provider_name]

    vision_model_input = ""
    if selected_vision_provider == "local":
        if not available_local_models:
            st.error("Could not connect to LM Studio. Please ensure it is running.")
        else:
            try:
                vision_index = available_local_models.index(current_settings.get("vision_service", {}).get("model"))
            except (ValueError, TypeError):
                vision_index = 0
            vision_model_input = st.selectbox("Select Local Vision Model", options=available_local_models, index=vision_index)
    else: # For online providers
        vision_model_input = st.text_input("Enter Online Model Name", value=current_settings.get("vision_service", {}).get("model", "gemini-1.5-pro-latest"))
        # Check for API key
        api_key_name = f"{selected_vision_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.success(f"✅ API Key found for {selected_vision_provider_name}")
        else:
            st.error(f"⚠️ API Key not found. Please add {api_key_name} to your .env file.")

    st.divider()

    # --- Language Service Configuration ---
    st.header("Language Service (for Translations)")
    
    current_lang_provider = current_settings.get("language_service", {}).get("provider", "local")
    selected_lang_provider_name = st.radio(
        "Select Language Provider",
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_settings.get("language_service", {}).get("provider", "local")),
        key="lang_provider_selector"
    )
    selected_lang_provider = PROVIDER_OPTIONS[selected_lang_provider_name]

    lang_model_input = ""
    if selected_lang_provider == "local":
        if not available_local_models:
            st.error("Could not connect to LM Studio. Please ensure it is running.")
        else:
            try:
                lang_index = available_local_models.index(current_settings.get("language_service", {}).get("model"))
            except (ValueError, TypeError):
                lang_index = 0
            lang_model_input = st.selectbox("Select Local Language Model", options=available_local_models, index=lang_index)
    else: # For online providers
        lang_model_input = st.text_input("Enter Online Model Name", value=current_settings.get("language_service", {}).get("model", "claude-3-sonnet"))
        api_key_name = f"{selected_lang_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.success(f"✅ API Key found for {selected_lang_provider_name}")
        else:
            st.error(f"⚠️ API Key not found. Please add {api_key_name} to your .env file.")

    # --- Save Button ---
    submitted = st.form_submit_button("Save All Settings")
    if submitted:
        new_settings = {
            "vision_service": {
                "provider": vision_selected,
                "model": vision_local_model_name if vision_selected == "local" else vision_openai_model_name,
                "local_model": vision_local_model_name,
                "openai_model": vision_openai_model_name,
            },
            "language_service": {
                "provider": lang_selected,
                "model": lang_local_model_name if lang_selected == "local" else lang_openai_model_name,
                "local_model": lang_local_model_name,
                "openai_model": lang_openai_model_name,
            },
        }
        save_settings(new_settings)
        st.success("Settings saved successfully!")
