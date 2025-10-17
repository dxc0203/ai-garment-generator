# File: pages/2_New_Task.py

import streamlit as st
import os
import sys
import time
import json
import logging

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import crud
from app.core import ai_services
from app.core.ai_services import call_ai_service
from app.config import UPLOADS_DIR, SPEC_SHEET_PROMPT_DIR, NAME_TAG_PROMPT_DIR
from app.validation import validate_all_inputs, sanitize_filename


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
    st.title("New Task")

    # Input for SKU
    sku = st.text_input("Enter SKU")

    # Dropdown for prompt template selection
    prompt_templates = ["Template 1: Describe the product", "Template 2: Highlight key features"]
    selected_prompt = st.selectbox("Select a Prompt Template", prompt_templates)

    # File uploader for image
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    # Dropdown for model selection (cheapest for text: gpt-3.5-turbo, for vision: gpt-4o, and a test mode)
    model_options = [
        "gpt-3.5-turbo",  # Cheapest for text
        "gpt-4o",         # Cheapest for vision/multimodal
        "[TEST MODE]"     # Test mode
    ]
    model = st.selectbox("Select AI Model", model_options, index=0)

    # Determine if test_mode should be enabled
    test_mode = model == "[TEST MODE]"

    if st.button("Generate Spec Sheet"):
        # Validate all inputs
        is_valid, validation_error = validate_all_inputs(
            sku, uploaded_file, selected_prompt, model,
            prompt_templates, model_options
        )

        if not is_valid:
            st.error(f"Validation Error: {validation_error}")
            logger.warning(f"Input validation failed: {validation_error}")
        elif uploaded_file and sku and selected_prompt:
            logger.info(f"Starting spec sheet generation for SKU: {sku}, model: {model}, test_mode: {test_mode}")

            # Sanitize filename for security
            safe_filename = sanitize_filename(uploaded_file.name)
            temp_image_path = f"temp_{safe_filename}"

            try:
                # Save the uploaded file temporarily
                with open(temp_image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Call the AI service with test_mode if selected
                ai_response = call_ai_service(selected_prompt, model=model if not test_mode else "gpt-4o", image_path=temp_image_path, test_mode=test_mode)
                st.success("Spec Sheet Generated:")
                st.text(ai_response)
                logger.info(f"Spec sheet generated successfully for SKU: {sku}")

                # 1. Create a new task in the database
                batch_id = None  # You can update this if you have batch logic
                task_id = crud.create_task(sku, [temp_image_path], batch_id)

                # 2. Save the generated spec sheet to the task
                if task_id:
                    crud.add_initial_spec_sheet(task_id, ai_response)
                    st.success(f"Spec Sheet saved to task ID: {task_id}. It will appear in the Dashboard.")
                    logger.info(f"New task created with ID {task_id} for SKU {sku}")
                else:
                    logger.error(f"Failed to create database task for SKU {sku}")
                    st.error("Failed to create a new task in the database.")

            except RuntimeError as e:
                logger.error(f"Failed to generate spec sheet for SKU {sku}: {e}")
                st.error(f"Error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during spec sheet generation for SKU {sku}: {e}")
                st.error(f"An unexpected error occurred: {e}")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_image_path):
                    try:
                        os.remove(temp_image_path)
                        logger.debug(f"Cleaned up temporary file: {temp_image_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up temporary file {temp_image_path}: {e}")
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
