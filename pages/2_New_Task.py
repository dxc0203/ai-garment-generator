# File: pages/2_New_Task.py

import streamlit as st
import os
import sys
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import crud
from app.core import ai_services
from app.config import UPLOADS_DIR, SPEC_SHEET_PROMPT_DIR, NAME_TAG_PROMPT_DIR
from app.translator import initialize_state, t, language_selector

# --- Initialize State and Translator ---
initialize_state()
language_selector()

# --- Helper Functions ---
def get_prompt_files(prompt_dir):
    """Returns a list of .txt files in the specified prompt directory."""
    if not os.path.exists(prompt_dir):
        os.makedirs(prompt_dir)
        return []
    return [f for f in os.listdir(prompt_dir) if f.endswith('.txt')]

def load_prompt_template(prompt_dir, filename):
    """Reads the content of a specific prompt file."""
    filepath = os.path.join(prompt_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Prompt file '{filename}' not found."

# --- Callback Functions ---
def clear_form():
    """Resets the input fields and log messages in the session state."""
    st.session_state.new_task_product_code = "SKU-"
    st.session_state.log_messages = []
    st.session_state.preview_data = {}
    if 'uploader_key' in st.session_state:
        st.session_state.uploader_key += 1
    else:
        st.session_state.uploader_key = 1

def submit_generation_task():
    """Contains all the logic for processing a new task."""
    st.session_state.log_messages = []
    st.session_state.preview_data = {}
    
    product_code = st.session_state.new_task_product_code
    uploader_widget_key = f"file_uploader_{st.session_state.uploader_key}"
    uploaded_files = st.session_state.get(uploader_widget_key, [])
    
    # Get selected prompts from the dropdowns
    spec_sheet_prompt_file = st.session_state.spec_sheet_selector
    name_tag_prompt_file = st.session_state.name_tag_selector

    if not product_code or product_code == "SKU-":
        st.session_state.log_messages.append(("error", t("Please enter a valid Product Code.")))
        return
    if not uploaded_files:
        st.session_state.log_messages.append(("error", t("Please upload at least one image.")))
        return
    if not spec_sheet_prompt_file or not name_tag_prompt_file:
        st.session_state.log_messages.append(("error", t("Please select a prompt template for each task.")))
        return

    with st.spinner(t("Processing... This may take a moment.")):
        st.session_state.log_messages.append(("info", t("1. Saving uploaded images...")))
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        saved_image_paths = []
        for i, uploaded_file in enumerate(uploaded_files):
            file_extension = os.path.splitext(uploaded_file.name)[1]
            new_filename = f"{product_code}_{i+1}{file_extension}"
            file_path = os.path.join(UPLOADS_DIR, new_filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_image_paths.append(file_path)
        
        st.session_state.log_messages.append(("success", t("Saved and renamed {} images.").format(len(saved_image_paths))))

        task_id = crud.create_task(product_code, saved_image_paths, f"batch_{int(time.time())}")
        if not task_id:
            st.session_state.log_messages.append(("error", t("Failed to create task record in the database.")))
            return
        st.session_state.log_messages.append(("success", t("Task record created with ID: {}").format(task_id)))

        # Load the content of the selected prompts
        spec_prompt = load_prompt_template(SPEC_SHEET_PROMPT_DIR, spec_sheet_prompt_file)
        name_tags_prompt = load_prompt_template(NAME_TAG_PROMPT_DIR, name_tag_prompt_file)

        st.session_state.log_messages.append(("info", t("3a. Calling AI for spec sheet...")))
        spec_sheet_text = ai_services.get_spec_from_image(saved_image_paths, spec_prompt)
        
        st.session_state.log_messages.append(("info", t("3b. Calling AI for product name and tags...")))
        name_and_tags_data = ai_services.get_name_and_tags_from_image(saved_image_paths, name_tags_prompt)
        
        product_name = name_and_tags_data.get("product_name", "N/A")
        tags = name_and_tags_data.get("tags", {})
        
        st.session_state.log_messages.append(("info", t("4. Saving all data to database...")))
        crud.add_initial_spec_sheet(task_id, spec_sheet_text)
        crud.update_task_with_ai_data(task_id, product_name, tags)
        
        st.session_state.log_messages.append(("success", t("Task is now ready for approval in the Dashboard!")))
        st.session_state.preview_data = {
            "name": product_name,
            "tags": tags,
            "spec_sheet": spec_sheet_text
        }
        st.balloons()

# --- Initialize Session State ---
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = {}
if 'new_task_product_code' not in st.session_state:
    st.session_state.new_task_product_code = "SKU-"

# --- Main Page UI ---
st.set_page_config(page_title=t("Create New Task"), layout="wide")
st.title(f"📝 {t('Create New Task')}")

if st.button(t("Start a New Task / Clear Form"), on_click=clear_form, type="secondary"):
    pass
st.divider()

# --- User Input Widgets ---
st.text_input(t("Product Code / SKU"), key="new_task_product_code")

# --- Prompt Selection Dropdowns ---
st.subheader(t("Prompt Template Selection"))
col1, col2 = st.columns(2)
with col1:
    spec_sheet_prompts = get_prompt_files(SPEC_SHEET_PROMPT_DIR)
    selected_spec_sheet = st.selectbox(
        t("Spec Sheet Prompt"),
        options=spec_sheet_prompts,
        key="spec_sheet_selector",
        index=0 if spec_sheet_prompts else None
    )
    # --- NEW: Preview for Spec Sheet Prompt ---
    if selected_spec_sheet:
        with st.expander(t("Preview Selected Prompt")):
            st.text(load_prompt_template(SPEC_SHEET_PROMPT_DIR, selected_spec_sheet))

with col2:
    name_tag_prompts = get_prompt_files(NAME_TAG_PROMPT_DIR)
    selected_name_tag = st.selectbox(
        t("Name & Tag Prompt"),
        options=name_tag_prompts,
        key="name_tag_selector",
        index=0 if name_tag_prompts else None
    )
    # --- NEW: Preview for Name & Tag Prompt ---
    if selected_name_tag:
        with st.expander(t("Preview Selected Prompt")):
            st.text(load_prompt_template(NAME_TAG_PROMPT_DIR, selected_name_tag))

uploaded_files = st.file_uploader(
    t("Upload Product Images (Front, Back, Side)"),
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.subheader(t("Image Previews"))
    cols = st.columns(len(uploaded_files))
    for i, uploaded_file in enumerate(uploaded_files):
        with cols[i]:
            st.image(uploaded_file, use_container_width=True)

st.button(t("Generate Spec Sheet & Name/Tags"), type="primary", on_click=submit_generation_task)
st.divider()

# --- Preview Area ---
if st.session_state.preview_data:
    with st.container(border=True):
        st.markdown(f"#### {t('Generated Data Preview')}")
        st.text_input(t("Product Name"), value=st.session_state.preview_data.get('name'), disabled=True)
        st.text_input(t("Tags"), value=json.dumps(st.session_state.preview_data.get('tags')), disabled=True)
        st.text_area(t("Spec Sheet"), value=st.session_state.preview_data.get('spec_sheet'), height=250, disabled=True)

# --- Log Display Area ---
log_container = st.container(border=True)
with log_container:
    st.markdown(f"#### {t('Process Log')}")
    for msg_type, msg in st.session_state.log_messages:
        if msg_type == "info": st.info(msg)
        elif msg_type == "success": st.success(msg)
        elif msg_type == "error": st.error(msg)
