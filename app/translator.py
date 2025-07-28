# File: app/translator.py

import streamlit as st
import requests
import json
from app.database import crud
from app.config import LM_STUDIO_API_URL # Use the single, main URL

def initialize_state():
    """Initializes the session state for the translator."""
    if 'lang' not in st.session_state:
        st.session_state.lang = "en"

def ai_translate(text_to_translate: str, target_lang_code: str):
    """Sends text to the local LLM and returns the translation."""
    language_map = {
        "zh_CN": "Simplified Chinese",
        "es": "Spanish",
        "fr": "French"
    }
    target_language = language_map.get(target_lang_code, "English")
    prompt = f"Please translate the following English text to {target_language}. Provide only the translated text, without any explanations or quotation marks. The text to translate is: \"{text_to_translate}\""
    
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        # The request now uses the single, correct URL from the config file.
        response = requests.post(LM_STUDIO_API_URL, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        translated_text = response.json()['choices'][0]['message']['content'].strip().strip('"')
        return translated_text
    except Exception as e:
        print(f"AI translation failed for '{text_to_translate}': {e}")
        return None

def t(source_text: str):
    """The main translation function."""
    lang_code = st.session_state.get('lang', 'en')
    if lang_code == 'en':
        return source_text

    cached_translation = crud.get_translation(lang_code, source_text)
    if cached_translation:
        return cached_translation
    
    ai_translation = ai_translate(source_text, lang_code)
    
    if ai_translation:
        crud.add_translation(lang_code, source_text, ai_translation)
        return ai_translation
    else:
        return source_text

def language_selector():
    """Creates a language selector widget in the Streamlit sidebar."""
    st.sidebar.subheader("Language")
    languages = {"English": "en", "简体中文": "zh_CN", "Español": "es", "Français": "fr"}
    current_lang_code = st.session_state.get('lang', 'en')
    current_lang_name_list = [name for name, code in languages.items() if code == current_lang_code]
    current_lang_name = current_lang_name_list[0] if current_lang_name_list else "English"

    def on_lang_change():
        new_lang_code = languages[st.session_state.lang_selector]
        st.session_state.lang = new_lang_code

    st.sidebar.selectbox(
        "Select Language",
        options=languages.keys(),
        index=list(languages.keys()).index(current_lang_name),
        key="lang_selector",
        on_change=on_lang_change
    )
