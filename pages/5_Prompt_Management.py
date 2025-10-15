# File: pages/5_Prompt_Management.py

import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the new, specific prompt directories from the config
from app.config import SPEC_SHEET_PROMPT_DIR, NAME_TAG_PROMPT_DIR

# --- Initialize State ---
st.set_page_config(page_title="Prompt Management", layout="wide")
st.title(f"📝 Prompt Template Management")
st.markdown("Here you can view, edit, and create new prompt templates for different tasks.")

# --- A dictionary to manage our different prompt types ---
PROMPT_TYPES = {
    "Spec Sheet Prompts": SPEC_SHEET_PROMPT_DIR,
    "Name & Tag Prompts": NAME_TAG_PROMPT_DIR
}

# --- Helper functions now take a directory argument ---
def get_prompt_files(prompt_dir):
    """Returns a list of .txt files in the specified prompt directory."""
    if not os.path.exists(prompt_dir):
        os.makedirs(prompt_dir)
        return []
    return [f for f in os.listdir(prompt_dir) if f.endswith('.txt')]

def read_prompt_file(prompt_dir, filename):
    """Reads the content of a specific prompt file from a given directory."""
    filepath = os.path.join(prompt_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "File not found."

def save_prompt_file(prompt_dir, filename, content):
    """Saves content to a specific prompt file in a given directory."""
    filepath = os.path.join(prompt_dir, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        st.error("Failed to save file: {}".format(e))
        return False

# --- Main UI ---
# Create a tab for each prompt type
tab_list = st.tabs(list(PROMPT_TYPES.keys()))

for i, (tab_name, prompt_dir) in enumerate(PROMPT_TYPES.items()):
    with tab_list[i]:
        st.subheader(tab_name)
        
        prompt_files = get_prompt_files(prompt_dir)
        
        # --- Edit Existing Template Section ---
        st.header("Edit Existing Templates")
        if not prompt_files:
            st.info("No prompt templates found for this type. Please create one below.")
        else:
            selected_template = st.selectbox(
                "Select a template to view or edit", 
                options=prompt_files, 
                key=f"select_{prompt_dir}" # Unique key for each selectbox
            )
            
            if selected_template:
                template_content = read_prompt_file(prompt_dir, selected_template)
                
                edited_content = st.text_area(
                    "Template Content",
                    value=template_content,
                    height=300,
                    key=f"editor_{prompt_dir}_{selected_template}"
                )
                
                if st.button("Save Changes", key=f"save_{prompt_dir}_{selected_template}"):
                    if save_prompt_file(prompt_dir, selected_template, edited_content):
                        st.success("Template '{}' saved successfully!".format(selected_template))
                        st.rerun()
        
        st.divider()

        # --- Create New Template Section ---
        st.header("Create New Template")
        with st.form(key=f"new_template_form_{prompt_dir}"):
            new_filename = st.text_input(
                "New Template Filename (must end with .txt)",
                placeholder="e.g., marketing_prompt.txt",
                key=f"name_input_{prompt_dir}"
            )
            new_content = st.text_area(
                "New Template Content",
                height=200,
                placeholder="Enter the full text of your new prompt here...",
                key=f"content_input_{prompt_dir}"
            )
            
            submitted = st.form_submit_button("Create Template")
            
            if submitted:
                if not new_filename.endswith(".txt"):
                    st.error("Filename must end with .txt")
                elif not new_content:
                    st.error("Template content cannot be empty.")
                elif os.path.exists(os.path.join(prompt_dir, new_filename)):
                    st.error("A template with this filename already exists.")
                else:
                    if save_prompt_file(prompt_dir, new_filename, new_content):
                        st.success("New template '{}' created successfully!".format(new_filename))
