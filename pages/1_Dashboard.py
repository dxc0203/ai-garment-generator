# File: pages/1_Dashboard.py

import streamlit as st
import os
import sys
import json
import logging
from PIL import Image


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import crud
from app.core import workflow_manager
# TEMPORARILY DISABLE WARNING MONITOR
# from app.warning_monitor import initialize_warning_monitor

# Initialize warning monitor
# warning_monitor = initialize_warning_monitor()

logger = logging.getLogger(__name__)

# --- Initialize State ---
st.set_page_config(page_title="Task Dashboard", layout="wide")
st.title(f"📊 Task Dashboard")
st.markdown("Manage and review all generation tasks.")

# Handle retry spec sheet
if 'retry_task_id' in st.session_state:
    task_id = st.session_state['retry_task_id']
    task = crud.get_task_by_id(task_id)
    if task and task.get('uploaded_image_paths'):
        with st.spinner("Generating spec sheet..."):
            try:
                # Use default prompt for retry
                prompt = "Describe this garment product in detail for e-commerce."
                model = "gpt-4o"  # Use vision-capable model
                
                # Get image path
                image_paths = task['uploaded_image_paths'].split(',')
                image_path = image_paths[0] if image_paths else None
                
                if image_path and os.path.exists(image_path):
                    from app.core.ai_services import call_ai_service
                    ai_response = call_ai_service(prompt, task_id=task_id, model=model, image_path=image_path)
                    
                    if ai_response:
                        crud.add_initial_spec_sheet(task_id, ai_response)
                        crud.update_task_status(task_id, 'PENDING_APPROVAL')
                        st.success("Spec sheet generated successfully!")
                    else:
                        st.error("Failed to generate spec sheet.")
                else:
                    st.error("No valid image found for this task.")
            except Exception as e:
                logger.error(f"Error retrying spec sheet for task {task_id}: {e}")
                st.error("An error occurred while generating the spec sheet.")
    
    del st.session_state['retry_task_id']
    st.rerun()

# --- Initialize session state ---
if 'selected_tasks' not in st.session_state:
    st.session_state.selected_tasks = set()
if 'tag_filter' not in st.session_state:
    st.session_state.tag_filter = []

# --- Callback Functions ---
def update_status(task_id, status_map):
    translated_status = st.session_state.get(f"status_select_{task_id}")
    if translated_status:
        original_status = status_map.get(translated_status, "ERROR")
        crud.update_task_status(task_id, original_status)

def toggle_task_selection(task_id):
    if task_id in st.session_state.selected_tasks:
        st.session_state.selected_tasks.remove(task_id)
    else:
        st.session_state.selected_tasks.add(task_id)

def toggle_all_tasks(all_ids):
    if st.session_state.get('select_all_checkbox', False):
        st.session_state.selected_tasks = set(all_ids)
    else:
        st.session_state.selected_tasks = set()

# --- Fetch all tasks and unique tags ---
all_tasks = crud.get_all_tasks()
unique_tags = crud.get_all_unique_tags()

# --- Filter Bar ---
st.subheader("Filters")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        active_status_filter = st.session_state.get('dashboard_filter', None)
        if active_status_filter:
            st.info(f"Filtering for status: **{active_status_filter.replace('_', ' ').title()}**")
            if st.button("Clear Status Filter"):
                del st.session_state['dashboard_filter']
                st.rerun()
    with col2:
        st.multiselect(
            "Filter by Tags",
            options=unique_tags,
            key="tag_filter"
        )

# --- Apply Filters ---
filtered_tasks = all_tasks
if active_status_filter:
    filtered_tasks = [task for task in filtered_tasks if task.get('status') == active_status_filter]

if st.session_state.tag_filter:
    selected_tags = st.session_state.tag_filter
    tasks_to_display = []
    for task in filtered_tasks:
        tags_str = task.get('product_tags')
        if tags_str:
            try:
                tags_dict = json.loads(tags_str)
                task_tags = {f"{k.title()}: {v}" for k, v in tags_dict.items()}
                if set(selected_tags).issubset(task_tags):
                    tasks_to_display.append(task)
            except (json.JSONDecodeError, TypeError):
                continue
    filtered_tasks = tasks_to_display

all_task_ids = [task['id'] for task in filtered_tasks]

# --- Toolbar ---
st.subheader("Bulk Actions")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.checkbox("Select All", key="select_all_checkbox", on_change=toggle_all_tasks, args=(all_task_ids,))

with col2:
    if st.button("🗑️ Delete Selected"):
        if st.session_state.selected_tasks:
            crud.delete_tasks_by_ids(list(st.session_state.selected_tasks))
            st.success("Deleted {} tasks.".format(len(st.session_state.selected_tasks)))
            st.session_state.selected_tasks.clear()
            st.rerun()
        else:
            st.warning("No tasks selected.")

with col3:
    if st.button("📝 Generate Spec Sheets", type="secondary"):
        if st.session_state.selected_tasks:
            # Filter for tasks that don't have spec sheets yet
            tasks_to_process = []
            for task_id in st.session_state.selected_tasks:
                task = crud.get_task_by_id(task_id)
                if task and not task.get('spec_sheet_text'):
                    tasks_to_process.append(task_id)
            
            if tasks_to_process:
                with st.spinner("Generating spec sheets... This may take a few minutes."):
                    success_count = 0
                    error_count = 0
                    
                    for task_id in tasks_to_process:
                        try:
                            task = crud.get_task_by_id(task_id)
                            if task and task.get('uploaded_image_paths'):
                                # Use default prompt for bulk generation
                                prompt = "Describe this garment product in detail for e-commerce."
                                model = "gpt-4o"  # Use vision-capable model
                                
                                # Get image path
                                image_paths = task['uploaded_image_paths'].split(',')
                                image_path = image_paths[0] if image_paths else None
                                
                                if image_path and os.path.exists(image_path):
                                    from app.core.ai_services import call_ai_service
                                    ai_response = call_ai_service(prompt, task_id=task_id, model=model, image_path=image_path)
                                    
                                    if ai_response:
                                        crud.add_initial_spec_sheet(task_id, ai_response)
                                        crud.update_task_status(task_id, 'PENDING_APPROVAL')
                                        success_count += 1
                                    else:
                                        error_count += 1
                                else:
                                    error_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            logger.error(f"Error generating spec sheet for task {task_id}: {e}")
                            error_count += 1
                    
                    st.success(f"Spec sheet generation complete. Success: {success_count}, Errors: {error_count}")
                    st.session_state.selected_tasks.clear()
                    st.rerun()
            else:
                st.warning("No eligible tasks selected (tasks must have images but no spec sheets).")
        else:
            st.warning("No tasks selected.")

with col4:
    if st.button("🚀 Generate Images", type="primary"):
        if st.session_state.selected_tasks:
            with st.spinner("Starting bulk generation... This may take a long time. Please wait."):
                result_message = workflow_manager.bulk_generate_images(list(st.session_state.selected_tasks))
            st.success(result_message)
            st.session_state.selected_tasks.clear()
            st.rerun()
        else:
            st.warning("No tasks selected for generation.")

with col5:
    # Status change dropdown for bulk actions
    status_options = ["PENDING_APPROVAL", "APPROVED", "REJECTED", "COMPLETED"]
    selected_status = st.selectbox("Change Status To:", ["Select Status"] + status_options, key="bulk_status_change")
    
    if selected_status != "Select Status" and st.button("Apply Status Change"):
        if st.session_state.selected_tasks:
            updated_count = 0
            for task_id in st.session_state.selected_tasks:
                try:
                    crud.update_task_status(task_id, selected_status)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating status for task {task_id}: {e}")
            
            st.success(f"Updated status to {selected_status} for {updated_count} tasks.")
            st.session_state.selected_tasks.clear()
            st.rerun()
        else:
            st.warning("No tasks selected.")

st.divider()

# --- Task List by Status ---
st.subheader(f"Displaying Tasks ({len(filtered_tasks)} of {len(all_tasks)} total)")

if not filtered_tasks:
    st.info("No tasks match the current filters or no tasks exist.")
else:
    # Group tasks by status
    status_groups = {}
    for task in filtered_tasks:
        status = task.get('status', 'UNKNOWN')
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(task)
    
    # Define status order for display
    status_order = ['NEW', 'PENDING_APPROVAL', 'APPROVED', 'PENDING_IMAGE_REVIEW', 'PENDING_REDO', 'GENERATING', 'COMPLETED', 'REJECTED']
    
    # Display tasks grouped by status
    for status in status_order:
        if status in status_groups:
            tasks_in_status = status_groups[status]
            with st.expander(f"📋 {status.replace('_', ' ').title()} ({len(tasks_in_status)} tasks)", expanded=(status == 'NEW')):
                for task in tasks_in_status:
                    task_id = task['id']
                    with st.container():
                        c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 2])
                        
                        with c1:
                            st.checkbox("", value=(task_id in st.session_state.selected_tasks), key=f"select_{task_id}", on_change=toggle_task_selection, args=(task_id,))
                        
                        with c2:
                            st.subheader(f"Product: {task.get('product_code', 'N/A')}")
                            product_name = task.get('product_name')
                            if product_name:
                                st.markdown(f"**AI Name**: {product_name}")
                            tags_str = task.get('product_tags')
                            if tags_str:
                                tags_dict = json.loads(tags_str)
                                tags_display = ", ".join(f"{k.title()}: {v}" for k, v in tags_dict.items())
                                st.markdown(f"**AI Tags**: {tags_display}")
                            st.text(f"Task ID: {task_id} | Created: {task.get('created_at', 'N/A')}")
                            st.markdown(f"**Original Images**:")
                            image_paths_str = task.get('uploaded_image_paths', '')
                            if image_paths_str:
                                image_paths = image_paths_str.split(',')
                                img_cols = st.columns(min(len(image_paths), 4))
                                for i, path in enumerate(image_paths):
                                    try:
                                        if path and os.path.exists(path):
                                            with img_cols[i % 4]:
                                                st.image(Image.open(path), width=100)
                                    except Exception: pass
                            else:
                                st.caption("No original images.")
                            st.markdown(f"**Spec Sheet**:")
                            spec_text = task.get('spec_sheet_text') or "Not generated yet."
                            st.text_area("Spec Sheet", value=spec_text, height=100, disabled=True, key=f"spec_sheet_display_{task_id}", label_visibility="hidden")

                        with c3:
                            st.markdown(f"**Final Image**:")
                            generated_path = task.get('generated_image_path')
                            if generated_path and os.path.exists(generated_path):
                                st.image(Image.open(generated_path), width=150)
                            else:
                                st.caption("No final image yet")
                        
                        with c4:
                            st.markdown(f"**Status**:")
                            current_status_en = task.get('status', 'ERROR')
                            st.info(current_status_en.replace('_', ' ').title())
                            st.markdown(f"**Next Action**:")
                            if current_status_en == 'PENDING_APPROVAL':
                                if st.button("Review Spec Sheet", key=f"action_{task_id}"):
                                    st.session_state['current_task_id'] = task_id
                                    st.session_state['navigate_to'] = 'approval_view'
                                    st.rerun()
                            elif current_status_en == 'APPROVED':
                                if st.button("Generate Photo", key=f"action_{task_id}", type="primary"):
                                    st.session_state['current_task_id'] = task_id
                                    st.session_state['navigate_to'] = 'approval_view'
                                    st.rerun()
                            elif current_status_en in ['PENDING_IMAGE_REVIEW', 'PENDING_REDO']:
                                if st.button("Finalize Image", key=f"action_{task_id}"):
                                    st.session_state['current_task_id'] = task_id
                                    st.session_state['navigate_to'] = 'approval_view'
                                    st.rerun()
                            elif current_status_en == 'GENERATING':
                                st.warning("Processing...")
                            elif current_status_en == 'NEW' and not task.get('spec_sheet_text'):
                                # Task was created but spec sheet generation failed
                                if st.button("Retry Spec Sheet", key=f"retry_{task_id}", type="secondary"):
                                    st.session_state['retry_task_id'] = task_id
                                    st.rerun()
                            else:
                                st.caption("No further actions.")
                    
                    st.divider()
