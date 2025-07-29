# File: pages/6_Settings.py

import streamlit as st
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.translator import initialize_state, t, language_selector, display_model_status

# --- Load .env file for API keys ---
load_dotenv()

# --- Initialize State and Translator ---
initialize_state()
language_selector()
display_model_status()

st.set_page_config(page_title=t("Settings"), layout="wide")
st.title(f"⚙️ {t('Application Settings')}")
st.markdown(t("Configure the AI models used by the application."))

# --- Load current settings and available models ---
current_settings = load_settings()
available_local_models = ai_services.get_available_lm_studio_models()

# --- Provider Options ---
# To add a new provider, just add it to this dictionary.
PROVIDER_OPTIONS = {
    "Local (LM Studio)": "local",
    "Google": "google",
    "OpenAI": "openai",
    "Anthropic": "anthropic"
}
# Create a reverse map for easy lookup
PROVIDER_NAMES = {v: k for k, v in PROVIDER_OPTIONS.items()}

# --- Settings Form ---
with st.form("settings_form"):
    
    # --- Vision Service Configuration ---
    st.header(t("Vision Service (for Spec Sheets & Tags)"))
    
    current_vision_provider = current_settings.get("vision_service", {}).get("provider", "local")
    selected_vision_provider_name = st.radio(
        t("Select Vision Provider"),
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_vision_provider),
        key="vision_provider_selector"
    )
    selected_vision_provider = PROVIDER_OPTIONS[selected_vision_provider_name]

    vision_model_input = ""
    if selected_vision_provider == "local":
        if not available_local_models:
            st.error(t("Could not connect to LM Studio. Please ensure it is running."))
        else:
            try:
                vision_index = available_local_models.index(current_settings.get("vision_service", {}).get("model"))
            except (ValueError, TypeError):
                vision_index = 0
            vision_model_input = st.selectbox(t("Select Local Vision Model"), options=available_local_models, index=vision_index)
    else: # For online providers
        vision_model_input = st.text_input(t("Enter Online Model Name"), value=current_settings.get("vision_service", {}).get("model", "gemini-1.5-pro-latest"))
        # Check for API key
        api_key_name = f"{selected_vision_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.success(f"✅ {t('API Key found for {}').format(selected_vision_provider_name)}")
        else:
            st.error(f"⚠️ {t('API Key not found. Please add {} to your .env file.').format(api_key_name)}")

    st.divider()

    # --- Language Service Configuration ---
    st.header(t("Language Service (for Translations)"))
    
    current_lang_provider = current_settings.get("language_service", {}).get("provider", "local")
    selected_lang_provider_name = st.radio(
        t("Select Language Provider"),
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_lang_provider),
        key="lang_provider_selector"
    )
    selected_lang_provider = PROVIDER_OPTIONS[selected_lang_provider_name]

    lang_model_input = ""
    if selected_lang_provider == "local":
        if not available_local_models:
            st.error(t("Could not connect to LM Studio. Please ensure it is running."))
        else:
            try:
                lang_index = available_local_models.index(current_settings.get("language_service", {}).get("model"))
            except (ValueError, TypeError):
                lang_index = 0
            lang_model_input = st.selectbox(t("Select Local Language Model"), options=available_local_models, index=lang_index)
    else: # For online providers
        lang_model_input = st.text_input(t("Enter Online Model Name"), value=current_settings.get("language_service", {}).get("model", "claude-3-sonnet"))
        api_key_name = f"{selected_lang_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.success(f"✅ {t('API Key found for {}').format(selected_lang_provider_name)}")
        else:
            st.error(f"⚠️ {t('API Key not found. Please add {} to your .env file.').format(api_key_name)}")

    # --- Save Button ---
    submitted = st.form_submit_button(t("Save All Settings"))
    if submitted:
        new_settings = {
            "vision_service": {
                "provider": selected_vision_provider,
                "model": vision_model_input
            },
            "language_service": {
                "provider": selected_lang_provider,
                "model": lang_model_input
            }
        }
        save_settings(new_settings)
        st.success(t("Settings saved successfully!"))
