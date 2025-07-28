# File: pages/1_Dashboard.py

import streamlit as st
import os
import sys
import json
from PIL import Image


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import crud
from app.core import workflow_manager
from app.translator import initialize_state, t, language_selector, display_model_status

# --- Initialize State and Translator ---
initialize_state()
language_selector()
display_model_status()

st.set_page_config(page_title=t("Task Dashboard"), layout="wide")
st.title(f"📊 {t('Task Dashboard')}")
st.markdown(t("Manage and review all generation tasks."))

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
st.subheader(t("Filters"))
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        active_status_filter = st.session_state.get('dashboard_filter', None)
        if active_status_filter:
            st.info(f"{t('Filtering for status')}: **{t(active_status_filter.replace('_', ' ').title())}**")
            if st.button(t("Clear Status Filter")):
                del st.session_state['dashboard_filter']
                st.rerun()
    with col2:
        st.multiselect(
            t("Filter by Tags"),
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
st.subheader(t("Bulk Actions"))
t_col1, t_col2, t_col3, _ = st.columns([1, 2, 2, 6])
with t_col1:
    st.checkbox(t("Select All"), key="select_all_checkbox", on_change=toggle_all_tasks, args=(all_task_ids,))
with t_col2:
    if st.button(t("Delete Selected")):
        if st.session_state.selected_tasks:
            crud.delete_tasks_by_ids(list(st.session_state.selected_tasks))
            st.success(t("Deleted {} tasks.").format(len(st.session_state.selected_tasks)))
            st.session_state.selected_tasks.clear()
            st.rerun()
        else:
            st.warning(t("No tasks selected."))
with t_col3:
    if st.button(f"🚀 {t('Generate Selected')}", type="primary"):
        if st.session_state.selected_tasks:
            with st.spinner(t("Starting bulk generation... This may take a long time. Please wait.")):
                result_message = workflow_manager.bulk_generate_images(list(st.session_state.selected_tasks))
            st.success(t(result_message))
            st.session_state.selected_tasks.clear()
            st.rerun()
        else:
            st.warning(t("No tasks selected for generation."))

st.divider()

# --- Task List ---
st.subheader(f"{t('Displaying Tasks')} ({len(filtered_tasks)} of {len(all_tasks)} total)")
if not filtered_tasks:
    st.info(t("No tasks match the current filters or no tasks exist."))
else:
    for task in filtered_tasks:
        task_id = task['id']
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 2])
            
            with c1:
                st.checkbox("", value=(task_id in st.session_state.selected_tasks), key=f"select_{task_id}", on_change=toggle_task_selection, args=(task_id,))
            
            with c2:
                st.subheader(f"{t('Product')}: {task.get('product_code', 'N/A')}")
                product_name = task.get('product_name')
                if product_name:
                    st.markdown(f"**{t('AI Name')}:** {product_name}")
                tags_str = task.get('product_tags')
                if tags_str:
                    tags_dict = json.loads(tags_str)
                    tags_display = ", ".join(f"{k.title()}: {v}" for k, v in tags_dict.items())
                    st.markdown(f"**{t('AI Tags')}:** {tags_display}")
                st.text(f"{t('Task ID')}: {task_id} | {t('Created')}: {task.get('created_at', 'N/A')}")
                st.markdown(f"**{t('Original Images')}:**")
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
                    st.caption(t("No original images."))
                st.markdown(f"**{t('Spec Sheet')}:**")
                spec_text = task.get('spec_sheet_text') or t("Not generated yet.")
                st.text_area("", value=spec_text, height=100, disabled=True, key=f"spec_sheet_display_{task_id}")

            with c3:
                st.markdown(f"**{t('Final Image')}:**")
                generated_path = task.get('generated_image_path')
                if generated_path and os.path.exists(generated_path):
                    st.image(Image.open(generated_path), width=150)
                else:
                    st.caption(t("No final image yet"))
            
            with c4:
                st.markdown(f"**{t('Status')}:**")
                current_status_en = task.get('status', 'ERROR')
                st.info(t(current_status_en.replace('_', ' ').title()))
                st.markdown(f"**{t('Next Action')}:**")
                if current_status_en == 'PENDING_APPROVAL':
                    if st.button(t("Review Spec Sheet"), key=f"action_{task_id}"):
                        st.session_state['current_task_id'] = task_id
                        st.switch_page("pages/3_Approval_View.py")
                elif current_status_en == 'APPROVED':
                    if st.button(t("Generate Photo"), key=f"action_{task_id}", type="primary"):
                        st.session_state['current_task_id'] = task_id
                        st.switch_page("pages/3_Approval_View.py")
                elif current_status_en in ['PENDING_IMAGE_REVIEW', 'PENDING_REDO']:
                    if st.button(t("Finalize Image"), key=f"action_{task_id}"):
                        st.session_state['current_task_id'] = task_id
                        st.switch_page("pages/3_Approval_View.py")
                elif current_status_en == 'GENERATING':
                    st.warning(t("Processing..."))
                else:
                    st.caption(t("No further actions."))
