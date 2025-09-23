# File: pages/6_Settings.py
import streamlit as st
import os
import sys
from dotenv import load_dotenv, dotenv_values, set_key
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core import ai_services
from app.settings_manager import load_settings, save_settings
from app.translator import initialize_state, t, language_selector, display_model_status

load_dotenv()
initialize_state()
language_selector()
display_model_status()
st.set_page_config(page_title=t("Settings"), layout="wide")
st.title(f"⚙️ {t('Application Settings')}")
st.markdown(t("Configure the AI models used by the application."))

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
    # Vision Service
    st.header(t("Vision Service (for Spec Sheets & Tags)"))
    vision_local_model, vision_openai_model = get_model_val("vision_service")
    vision_provider = st.radio(
        t("Select Vision Provider"),
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_settings.get("vision_service", {}).get("provider", "local")),
        key="vision_provider_selector"
    )
    vision_selected = PROVIDER_OPTIONS[vision_provider]
    # local: 只留掃描！(不再text_input)
    if available_local_models:
        vidx = available_local_models.index(vision_local_model) if vision_local_model in available_local_models else 0
    else:
        vidx = 0
    vision_local_model_name = st.selectbox(
        t("Scan & Select Local Model"),
        options=available_local_models if available_local_models else ["(none found, please check server)"],
        index=vidx if available_local_models else 0,
        key="vision_local_model"
    )
    # openai
    vision_openai_model_name = st.text_input(
        t("Specify model name for OpenAI"),
        value=vision_openai_model,
        key="vision_openai_model"
    )
    api_key_name = "OPENAI_API_KEY"
    if vision_selected == "openai":
        if os.getenv(api_key_name):
            st.success(t("✅ API Key found for OpenAI"))
        else:
            st.error(t(f"⚠️ API Key not found. Please add {api_key_name} to your .env file."))
    st.divider()

    # Language Service 同樣邏輯
    st.header(t("Language Service (for Translations)"))
    lang_local_model, lang_openai_model = get_model_val("language_service")
    lang_provider = st.radio(
        t("Select Language Provider"),
        options=PROVIDER_OPTIONS.keys(),
        index=list(PROVIDER_OPTIONS.values()).index(current_settings.get("language_service", {}).get("provider", "local")),
        key="lang_provider_selector"
    )
    lang_selected = PROVIDER_OPTIONS[lang_provider]
    if available_local_models:
        lidx = available_local_models.index(lang_local_model) if lang_local_model in available_local_models else 0
    else:
        lidx = 0
    lang_local_model_name = st.selectbox(
        t("Scan & Select Local Model"),
        options=available_local_models if available_local_models else ["(none found, please check server)"],
        index=lidx if available_local_models else 0,
        key="lang_local_model"
    )
    lang_openai_model_name = st.text_input(
        t("Specify model name for OpenAI"),
        value=lang_openai_model,
        key="lang_openai_model"
    )
    if lang_selected == "openai":
        if os.getenv(api_key_name):
            st.success(t("✅ API Key found for OpenAI"))
        else:
            st.error(t(f"⚠️ API Key not found. Please add {api_key_name} to your .env file."))
    submitted = st.form_submit_button(t("Save All Settings"))
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
        st.success(t("Settings saved successfully!"))

st.markdown("---")
st.header("API Key 編輯設定（OpenAI）")
env_path = ".env"
env_dict = dotenv_values(env_path) if os.path.exists(env_path) else {}
key = "OPENAI_API_KEY"
now = env_dict.get(key, "")
val = st.text_input(f"{key} (範例：sk-...)", value=now, key=f"{key}_input_api")
if st.button(f"儲存/更新 {key}", key=f"save_{key}_api"):
    set_key(env_path, key, val)
    st.success(f"已儲存 {key} 到 .env！")
    env_dict[key] = val
st.info("API key 說明：儲存後會寫入本地 .env 檔，不會流向雲端，請勿上傳到 GitHub。")
