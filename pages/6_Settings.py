# File: pages/6_Settings.py

import streamlit as st
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.constants import MODEL_CAPABILITIES, DEFAULT_MODELS, OPENAI_MODELS
# from app.translator import initialize_state, t, language_selector, display_model_status

# --- Load .env file for API keys ---
load_dotenv()

# --- Initialize State and Translator ---
# initialize_state()
# language_selector()
# display_model_status()

st.set_page_config(page_title="Settings", layout="wide")
st.title(f"⚙️ Application Settings")
st.markdown("Configure the AI models used by the application.")

# --- Load current settings ---
current_settings = load_settings()

# Check for OpenAI API key at the top
api_key_found = bool(os.getenv("OPENAI_API_KEY"))
if api_key_found:
    st.success("✅ OpenAI API Key found")
else:
    st.error("⚠️ OpenAI API Key not found. Please add OPENAI_API_KEY to your .env file.")

st.divider()

# --- Settings Form ---
with st.form("settings_form"):
    
    # --- Vision Model Configuration ---
    st.header("👁️ Vision Model")
    st.markdown("Model used for analyzing product images and generating spec sheets.")
    
    vision_models = MODEL_CAPABILITIES['image_input']  # Only vision-capable models
    current_vision_model = current_settings.get("vision_service", {}).get("model", DEFAULT_MODELS['vision'])
    try:
        vision_index = vision_models.index(current_vision_model)
    except ValueError:
        vision_index = vision_models.index(DEFAULT_MODELS['vision']) if DEFAULT_MODELS['vision'] in vision_models else 0
    
    selected_vision_model = st.selectbox(
        "Select Vision Model", 
        options=vision_models, 
        index=vision_index,
        help="Used for image analysis and spec sheet generation"
    )

    st.divider()

    # --- Text Model Configuration ---
    st.header("📝 Text Model")
    st.markdown("Model used for text processing and translations.")
    
    text_models = MODEL_CAPABILITIES['text_input'][:10]  # Limit to top 10 text models for simplicity
    current_text_model = current_settings.get("language_service", {}).get("model", DEFAULT_MODELS['text_only'])
    try:
        text_index = text_models.index(current_text_model)
    except ValueError:
        text_index = text_models.index(DEFAULT_MODELS['text_only']) if DEFAULT_MODELS['text_only'] in text_models else 0
    
    selected_text_model = st.selectbox(
        "Select Text Model",
        options=text_models,
        index=text_index,
        help="Used for text processing and translations"
    )

    st.divider()

    # --- Image Generation Model Configuration ---
    st.header("🎨 Image Generation Model")
    st.markdown("Model used for generating product photos.")
    
    image_gen_models = MODEL_CAPABILITIES['image_output']  # Only image generation models
    current_image_gen_model = current_settings.get("image_generation_service", {}).get("model", DEFAULT_MODELS.get('image_generation', 'dall-e-3'))
    try:
        image_gen_index = image_gen_models.index(current_image_gen_model)
    except ValueError:
        image_gen_index = 0  # Default to first available
    
    selected_image_gen_model = st.selectbox(
        "Select Image Generation Model",
        options=image_gen_models,
        index=image_gen_index,
        help="Used for creating product photos"
    )

    st.divider()

    # --- Model Replacement Suggestions ---
    model_suggestions = current_settings.get("model_suggestions", [])
    if model_suggestions:
        st.header("⚠️ Model Replacement Suggestions")
        st.markdown("The following models were found to be unavailable during startup:")
        
        for suggestion in model_suggestions:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.error(f"❌ {suggestion['unavailable_model']}")
                with col2:
                    st.markdown("➡️")
                with col3:
                    st.success(f"✅ {suggestion['suggested_replacement']}")
        
        if st.button("Clear Suggestions", help="Remove these suggestions after reviewing"):
            # Remove suggestions from settings
            updated_settings = current_settings.copy()
            updated_settings.pop("model_suggestions", None)
            save_settings(updated_settings)
            st.success("Suggestions cleared!")
            st.rerun()

    # --- Save Button ---
    submitted = st.form_submit_button("Save All Settings")
    if submitted:
        new_settings = {
            "vision_service": {
                "provider": "openai",
                "model": selected_vision_model
            },
            "language_service": {
                "provider": "openai", 
                "model": selected_text_model
            },
            "image_generation_service": {
                "provider": "openai",
                "model": selected_image_gen_model
            }
        }
        
        # Preserve model suggestions if they exist
        if "model_suggestions" in current_settings:
            new_settings["model_suggestions"] = current_settings["model_suggestions"]
            
        save_settings(new_settings)
        st.success("Settings saved successfully!")
