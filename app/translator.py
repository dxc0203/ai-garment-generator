# File: app/translator.py

import streamlit as st
import requests
import json
import os
from app.database import crud
from app.config import LM_STUDIO_API_URL
from app.settings_manager import load_settings
from app.core.ai_services import get_available_lm_studio_models

def initialize_state():
    """Initializes the session state for the translator."""
    if 'lang' not in st.session_state:
        st.session_state.lang = "en"

def t(source_text: str):
    """The main translation function."""
    lang_code = st.session_state.get('lang', 'en')
    if lang_code == 'en': return source_text
    cached = crud.get_translation(lang_code, source_text)
    if cached: return cached
    ai_trans = ai_translate(source_text, lang_code)
    if ai_trans and not ai_trans.startswith("Error"):
        crud.add_translation(lang_code, source_text, ai_trans)
        return ai_trans
    return source_text

def language_selector():
    """Creates a language selector widget in the Streamlit sidebar."""
    st.sidebar.subheader(t("Language"))
    languages = {"English": "en", "简体中文": "zh_CN", "Español": "es", "Français": "fr"}
    current_lang_code = st.session_state.get('lang', 'en')
    current_lang_name_list = [name for name, code in languages.items() if code == current_lang_code]
    current_lang_name = current_lang_name_list[0] if current_lang_name_list else "English"
    def on_lang_change():
        st.session_state.lang = languages[st.session_state.lang_selector]
    st.sidebar.selectbox(
        t("Select Language"),
        options=languages.keys(),
        index=list(languages.keys()).index(current_lang_name),
        key="lang_selector",
        on_change=on_lang_change
    )

# --- Reusable Model Status Display Function ---
def display_model_status():
    """
    Checks and displays the status of selected AI models in the sidebar.
    """
    st.sidebar.divider()
    st.sidebar.subheader(t("Model Status"))
    settings = load_settings()
    available_models = get_available_lm_studio_models()

    if not available_models:
        st.sidebar.error(t("LM Studio server not found!"))
        return

    # --- THIS IS THE FIX ---
    # Helper function to safely get the display name
    def get_display_name(model_identifier):
        if model_identifier and '/' in model_identifier:
            return model_identifier.split('/')[1]
        return model_identifier # Return the full name if no '/' is present

    # Check Vision Model
    vision_config = settings.get("vision_service", {})
    vision_provider = vision_config.get("provider", "local")
    vision_model = vision_config.get("model")
    
    st.sidebar.markdown(f"**{t('Vision Model')}:**")
    if vision_provider == "local":
        if vision_model and vision_model in available_models:
            st.sidebar.success(f"{get_display_name(vision_model)}", icon="✅")
        else:
            st.sidebar.error(t("Model Missing!"), icon="⚠️")
    else: # For online models
        api_key_name = f"{vision_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.sidebar.success(f"{vision_provider.title()}: {vision_model}", icon="☁️")
        else:
            st.sidebar.error(f"{t('API Key Missing!')}", icon="⚠️")

    # Check Language Model
    lang_config = settings.get("language_service", {})
    lang_provider = lang_config.get("provider", "local")
    lang_model = lang_config.get("model")

    st.sidebar.markdown(f"**{t('Language Model')}:**")
    if lang_provider == "local":
        if lang_model and lang_model in available_models:
            st.sidebar.success(f"{get_display_name(lang_model)}", icon="✅")
        else:
            st.sidebar.error(t("Model Missing!"), icon="⚠️")
    else: # For online models
        api_key_name = f"{lang_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.sidebar.success(f"{lang_provider.title()}: {lang_model}", icon="☁️")
        else:
            st.sidebar.error(f"{t('API Key Missing!')}", icon="⚠️")

def ai_translate(text_to_translate: str, target_lang_code: str):
    settings = load_settings()
    service_config = settings.get("language_service", {})
    language_model = service_config.get("model")
    if not language_model:
        return f"Error: No Language Model selected in Settings."
    language_map = {"zh_CN": "Simplified Chinese", "es": "Spanish", "fr": "French"}
    target_language = language_map.get(target_lang_code, "English")
    prompt = f"Translate to {target_language}: \"{text_to_translate}\""
    headers = {"Content-Type": "application/json"}
    data = {"model": language_model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip().strip('"')
    except Exception as e:
        return f"AI translation failed: {e}"
