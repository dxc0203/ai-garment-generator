# File: pages/2_New_Task.py

import streamlit as st
import os
import sys
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import crud
from app.core import ai_services
from app.core.ai_services import call_ai_service
from app.config import UPLOADS_DIR, SPEC_SHEET_PROMPT_DIR, NAME_TAG_PROMPT_DIR
from app.constants import MODEL_CAPABILITIES, DEFAULT_MODELS
from app.settings_manager import load_settings
from app.constants import MODEL_CAPABILITIES, DEFAULT_MODELS


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


def new_task_page():
    """
    Streamlit page for creating a new task and generating a spec sheet.
    """
    # Check if this is a retry from dashboard
    retry_task_id = st.session_state.get('retry_task_id')
    is_retry = retry_task_id is not None
    
    if is_retry:
        st.title("🔄 Retry Spec Sheet Generation")
        st.info(f"Retrying spec sheet generation for Task ID: {retry_task_id}")
        
        # Load existing task data
        existing_task = crud.get_task_by_id(retry_task_id)
        if not existing_task:
            st.error(f"Task {retry_task_id} not found.")
            return
    else:
        st.title("New Task")

    # Input for SKU - pre-populate if retry
    default_sku = existing_task.get('product_code', '') if is_retry else ''
    sku = st.text_input("Enter SKU", value=default_sku)

    # Dropdown for prompt template selection
    prompt_templates = ["Template 1: Describe the product", "Template 2: Highlight key features"]
    selected_prompt = st.selectbox("Select a Prompt Template", prompt_templates)

    # File uploader for image - handle existing image if retry
    if is_retry and existing_task.get('uploaded_image_paths'):
        st.info("Using existing uploaded image from the task.")
        # Get the first image path
        image_paths = existing_task['uploaded_image_paths'].split(',')
        existing_image_path = image_paths[0] if image_paths else None
        
        if existing_image_path and os.path.exists(existing_image_path):
            st.image(existing_image_path, caption="Existing Image", width=200)
            uploaded_file = None  # Don't need to upload new file
            image_path = existing_image_path
        else:
            st.warning("Original image not found. Please upload a new image.")
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            image_path = None
    else:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        image_path = None

    # Dropdown for model selection based on input/output types
    # Determine available models based on whether we have an image input
    has_image_input = bool(image_path or uploaded_file)
    
    # Load user-set default models from settings
    settings = load_settings()
    user_defaults = settings.get("default_models", {})
    
    if has_image_input:
        # For vision tasks (image input), prefer vision-capable models
        available_models = MODEL_CAPABILITIES['image_input']
        default_model = user_defaults.get('vision', DEFAULT_MODELS['vision'])
        model_description = "Vision-capable models (can process images)"
    else:
        # For text-only tasks, use text models
        available_models = MODEL_CAPABILITIES['text_input']
        default_model = user_defaults.get('text_only', DEFAULT_MODELS['text_only'])
        model_description = "Text models (for text-only tasks)"
    
    # Ensure the default model is still available, otherwise fall back to constants
    if default_model not in available_models:
        if has_image_input:
            default_model = DEFAULT_MODELS['vision']
        else:
            default_model = DEFAULT_MODELS['text_only']
    
    # Add test mode option
    model_options = available_models + ["[TEST MODE]"]
    
    # Set default index to the appropriate model
    try:
        default_index = model_options.index(default_model)
    except ValueError:
        default_index = 0
    
    model = st.selectbox(f"Select AI Model ({model_description})", model_options, index=default_index)

    # Determine if test_mode should be enabled
    test_mode = model == "[TEST MODE]"

    button_text = "Retry Generate Spec Sheet" if is_retry else "Generate Spec Sheet"
    if st.button(button_text):
        # Validation
        if is_retry:
            # For retry, we already have the SKU and image
            valid_inputs = sku and image_path
        else:
            # For new task, need uploaded file
            valid_inputs = uploaded_file and sku and selected_prompt
        
        if valid_inputs:
            # Handle image path
            if is_retry:
                temp_image_path = image_path
            else:
                # Save the uploaded file temporarily
                temp_image_path = f"temp_{uploaded_file.name}"
                with open(temp_image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Call the AI service with test_mode if selected
            ai_response = None
            try:
                ai_response = call_ai_service(selected_prompt, model=model if not test_mode else "gpt-4o", image_path=temp_image_path, test_mode=test_mode)
                st.success("Spec Sheet Generated:")
                st.text(ai_response)
            except RuntimeError as e:
                st.error(f"Error: {e}")
                ai_response = None

            if is_retry:
                # Update existing task with the new spec sheet
                if ai_response is not None:
                    crud.add_initial_spec_sheet(retry_task_id, ai_response)
                    st.success(f"Spec Sheet updated for Task ID: {retry_task_id}. It will appear in the Dashboard.")
                    # Clear the retry state
                    del st.session_state['retry_task_id']
                    st.rerun()
                else:
                    st.warning("Spec sheet generation failed. Please try again.")
            else:
                # Create new task (existing logic)
                batch_id = None  # You can update this if you have batch logic
                task_id = crud.create_task(sku, [temp_image_path], batch_id)

                # Save the generated spec sheet to the task
                if task_id and ai_response is not None:
                    crud.add_initial_spec_sheet(task_id, ai_response)
                    st.success(f"Spec Sheet saved to task ID: {task_id}. It will appear in the Dashboard.")
                elif task_id and ai_response is None:
                    st.warning(f"Task created with ID: {task_id}, but spec sheet generation failed. You can try again from the Dashboard.")
                else:
                    st.error("Failed to create a new task in the database.")
        else:
            if is_retry:
                st.warning("Please ensure SKU is filled and image exists.")
            else:
                st.warning("Please fill in all fields and upload an image.")

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



# Replace `submit_generation_task` with a placeholder function
def submit_generation_task():
    st.info("Task submission logic is not yet implemented.")

if 'uploaded_file' in st.session_state:
    st.subheader("Image Preview")
    st.image(st.session_state.uploaded_file, use_column_width=True)

# --- Preview Area ---
if st.session_state.preview_data:
    with st.container():
        st.markdown(f"#### {'Generated Data Preview'}")
        st.text_input("Product Name", value=st.session_state.preview_data.get('name'), disabled=True)
        st.text_input("Tags", value=json.dumps(st.session_state.preview_data.get('tags')), disabled=True)
        st.text_area("Spec Sheet", value=st.session_state.preview_data.get('spec_sheet'), height=250, disabled=True)

# --- Log Display Area ---
log_container = st.container()
with log_container:
    st.markdown(f"#### {'Process Log'}")
    for msg_type, msg in st.session_state.log_messages:
        if msg_type == "info": st.info(msg)
        elif msg_type == "success": st.success(msg)
        elif msg_type == "error": st.error(msg)

# Call the function to render the page
new_task_page()
