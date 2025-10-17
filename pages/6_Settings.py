# File: pages/6_Settings.py
import streamlit as st
import os
import sys
import logging
from dotenv import load_dotenv
from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.validation import validate_model_name

logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.validation import validate_model_name

load_dotenv()

st.set_page_config(page_title="Settings", layout="wide")
st.title(f"⚙️ {'Application Settings'}")
st.markdown("Configure the AI models used by the application.")

current_settings = load_settings()

# --- Vision Service Configuration ---
st.header("Vision Service (for Spec Sheets & Tags)")

vision_model_input = st.text_input("Enter OpenAI Vision Model Name", value="gpt-3.5-turbo")
api_key_name = "OPENAI_API_KEY"
if os.getenv(api_key_name):
    st.success(f"✅ API Key found for OpenAI")
else:
    st.error(f"⚠️ API Key not found. Please add {api_key_name} to your .env file.")

st.divider()

# --- Language Service Configuration ---
st.header("Language Service (for Translations)")

lang_model_input = st.text_input("Enter OpenAI Language Model Name", value="gpt-3.5-turbo")
if os.getenv(api_key_name):
    st.success(f"✅ API Key found for OpenAI")
else:
    st.error(f"⚠️ API Key not found. Please add {api_key_name} to your .env file.")

# --- Save Button ---
with st.form("settings_form"):
    submitted = st.form_submit_button("Save All Settings")
    if submitted:
        # Validate model names
        vision_valid, vision_error = validate_model_name(vision_model_input)
        lang_valid, lang_error = validate_model_name(lang_model_input)

        if not vision_valid:
            st.error(f"Vision Model Error: {vision_error}")
        elif not lang_valid:
            st.error(f"Language Model Error: {lang_error}")
        else:
            new_settings = {
                "vision_service": {
                    "provider": "openai",
                    "model": vision_model_input
                },
                "language_service": {
                    "provider": "openai",
                    "model": lang_model_input
                }
            }
            save_settings(new_settings)
            st.success("Settings saved successfully!")
            logger.info(f"Settings updated: vision_model={vision_model_input}, language_model={lang_model_input}")
