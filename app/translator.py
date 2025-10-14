# File: app/translator.py

import streamlit as st
import requests
import json
import os
import openai
from app.database import crud
from app.config import LM_STUDIO_API_URL
from app.settings_manager import load_settings
from app.core.ai_services import get_available_lm_studio_models

def initialize_state():
    """Initializes the session state for the translator."""
    if 'lang' not in st.session_state:
        st.session_state.lang = "en"

# --- Update Settings to Use OpenAI ---
def get_available_openai_models():
    """Fetch available OpenAI models."""
    try:
        response = openai.Model.list()
        return [model['id'] for model in response['data']]
    except Exception as e:
        return []
