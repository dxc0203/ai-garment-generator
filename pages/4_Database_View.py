# File: pages/4_Database_View.py (renamed from 3_...)

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import logging
from PIL import Image

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database.models import DATABASE_NAME, create_tables
from app.database import crud
from app.config import UPLOADS_DIR

# --- Initialize State ---
st.set_page_config(page_title="Database View", layout="wide")
st.title(f"🗄️ {'Raw Database View'}")
st.markdown("This page displays the raw data from the application's database tables for debugging and verification.")

# --- Bulk Task Creation ---
st.header("Bulk Task Creation")
st.markdown("Create multiple tasks at once without generating spec sheets. You can generate spec sheets later from the dashboard.")

with st.form("bulk_task_creation"):
    col1, col2 = st.columns(2)
    
    with col1:
        task_count = st.number_input("Number of tasks to create", min_value=1, max_value=50, value=5)
        base_sku = st.text_input("Base SKU prefix", value="BULK-", help="Tasks will be created as BULK-001, BULK-002, etc.")
    
    with col2:
        uploaded_files = st.file_uploader(
            "Upload images (optional)", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            help="Upload multiple images. They will be distributed among the tasks."
        )
    
    create_tasks = st.form_submit_button("Create Tasks", type="primary")
    
    if create_tasks:
        if not base_sku.strip():
            st.error("Please provide a base SKU prefix.")
        else:
            # Create tasks
            created_tasks = []
            for i in range(task_count):
                sku = "04d"
                task_id = crud.create_task(sku, [], None)  # Empty image list initially
                if task_id:
                    created_tasks.append(task_id)
            
            if created_tasks:
                st.success(f"✅ Created {len(created_tasks)} tasks: {', '.join(map(str, created_tasks))}")
                
                # If images were uploaded, distribute them among tasks
                if uploaded_files:
                    images_per_task = len(uploaded_files) // len(created_tasks)
                    extra_images = len(uploaded_files) % len(created_tasks)
                    
                    image_index = 0
                    for i, task_id in enumerate(created_tasks):
                        task_images = []
                        # Calculate how many images this task gets
                        num_images = images_per_task + (1 if i < extra_images else 0)
                        
                        for j in range(num_images):
                            if image_index < len(uploaded_files):
                                # Save the uploaded file
                                uploaded_file = uploaded_files[image_index]
                                image_path = os.path.join(UPLOADS_DIR, f"task_{task_id}_{j+1}_{uploaded_file.name}")
                                
                                # Ensure upload directory exists
                                os.makedirs(UPLOADS_DIR, exist_ok=True)
                                
                                with open(image_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                task_images.append(image_path)
                                image_index += 1
                        
                        if task_images:
                            # Update task with images
                            crud.update_task_images(task_id, task_images)
                
                st.info("💡 You can now generate spec sheets for these tasks from the Dashboard by selecting 'Retry Spec Sheet' on NEW tasks.")
                st.rerun()
            else:
                st.error("Failed to create tasks.")

st.divider()

def fetch_table_as_dataframe(table_name: str):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        st.error(f"An error occurred while fetching data from table '{table_name}': {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- Display the 'tasks' table ---
st.subheader("Tasks Table")
st.markdown("This table contains the main record for each generation task.")
tasks_df = fetch_table_as_dataframe("tasks")
if not tasks_df.empty:
    st.dataframe(tasks_df, use_container_width=True)
else:
    st.info("The 'tasks' table is currently empty.")

st.divider()

# --- Display the 'spec_sheet_versions' table ---
st.subheader("Spec Sheet Versions Table")
st.markdown("This table contains the complete edit history for every spec sheet.")
versions_df = fetch_table_as_dataframe("spec_sheet_versions")
if not versions_df.empty:
    st.dataframe(versions_df, use_container_width=True)
else:
    st.info("The 'spec_sheet_versions' table is currently empty.")

st.divider()

# --- Display the 'chat_history' table ---
st.subheader("Chat History Table")
st.markdown("This table contains the chat history for each task.")
chat_history_df = fetch_table_as_dataframe("chat_history")
if not chat_history_df.empty:
    st.dataframe(chat_history_df, use_container_width=True)
else:
    st.info("The 'chat_history' table is currently empty.")

st.divider()

# --- Ensure Database Initialization ---
st.subheader("Database Initialization")
if st.button("Initialize Database"):
    try:
        create_tables()
        st.success("Database tables have been successfully initialized.")
    except Exception as e:
        st.error(f"An error occurred during database initialization: {e}")
