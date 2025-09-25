# File: app/translator.py
import streamlit as st
import os
from app.settings_manager import load_settings
from app.core.ai_services import get_available_lm_studio_models

def initialize_state():
    """Initialize basic session state (translation functionality removed)."""
    pass

def t(source_text: str):
    """Simple pass-through function (translation functionality removed)."""
    return source_text

def language_selector():
    """Language selector removed - no longer needed."""
    pass

def display_model_status():
    """
    Checks and displays the status of selected AI models in the sidebar.
    """
    st.sidebar.divider()
    st.sidebar.subheader("Model Status")
    settings = load_settings()
    available_models = get_available_lm_studio_models()
    
    if not available_models:
        st.sidebar.error("LM Studio server not found!")
        return
    
    # Helper function to safely get the display name
    def get_display_name(model_identifier):
        if model_identifier and '/' in model_identifier:
            return model_identifier.split('/')[1]
        return model_identifier
    
    # Check Vision Model
    vision_config = settings.get("vision_service", {})
    vision_provider = vision_config.get("provider", "local")
    vision_model = vision_config.get("model")
    
    st.sidebar.markdown(f"**Vision Model:**")
    if vision_provider == "local":
        if vision_model and vision_model in available_models:
            st.sidebar.success(f"{get_display_name(vision_model)}", icon="✅")
        else:
            st.sidebar.error("Model Missing!", icon="⚠️")
    else:
        api_key_name = f"{vision_provider.upper()}_API_KEY"
        if os.getenv(api_key_name):
            st.sidebar.success(f"{vision_provider.title()}: {vision_model}", icon="☁️")
        else:
            st.sidebar.error("API Key Missing!", icon="⚠️")
    
    # Note: Language model for translation functionality removed
    # Only keeping vision model status for image generation
