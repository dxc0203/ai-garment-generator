# File: pages/4_Database_View.py (renamed from 3_...)

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database.models import DATABASE_NAME, create_tables
from app.translator import initialize_state

# --- Initialize State and Translator ---
initialize_state()

st.set_page_config(page_title="Database View", layout="wide")
st.title(f"🗄️ {'Raw Database View'}")
st.markdown("This page displays the raw data from the application's database tables for debugging and verification.")

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

# --- Database Control Functions ---
def execute_query(query: str, params: tuple = ()): 
    """Execute a SQL query with optional parameters."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        st.success("Query executed successfully.")
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
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

# --- Display the 'translations' table ---
st.subheader("Translations Table")
st.markdown("This table contains the real-time translation cache.")
translations_df = fetch_table_as_dataframe("translations")
if not translations_df.empty:
    st.dataframe(translations_df, use_container_width=True)
else:
    st.info("The 'translations' table is currently empty.")

# --- Add Record ---
st.subheader("Add Record to Tasks Table")
with st.form("add_record_form"):
    product_code = st.text_input("Product Code")
    status = st.selectbox("Status", ["NEW", "IN_PROGRESS", "COMPLETED"])
    product_name = st.text_input("Product Name")
    product_tags = st.text_input("Product Tags")
    batch_id = st.text_input("Batch ID")
    submitted = st.form_submit_button("Add Record")

    if submitted:
        query = """
        INSERT INTO tasks (product_code, status, product_name, product_tags, batch_id)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (product_code, status, product_name, product_tags, batch_id))

# --- Delete Record ---
st.subheader("Delete Record from Tasks Table")
record_id = st.number_input("Enter the ID of the record to delete", min_value=1, step=1)
if st.button("Delete Record"):
    query = "DELETE FROM tasks WHERE id = ?"
    execute_query(query, (record_id,))

# --- Update Record ---
st.subheader("Update Record in Tasks Table")
with st.form("update_record_form"):
    update_id = st.number_input("Enter the ID of the record to update", min_value=1, step=1)
    new_status = st.selectbox("New Status", ["NEW", "IN_PROGRESS", "COMPLETED"])
    new_product_name = st.text_input("New Product Name")
    new_product_tags = st.text_input("New Product Tags")
    update_submitted = st.form_submit_button("Update Record")

    if update_submitted:
        query = """
        UPDATE tasks
        SET status = ?, product_name = ?, product_tags = ?
        WHERE id = ?
        """
        execute_query(query, (new_status, new_product_name, new_product_tags, update_id))

# --- Ensure Database Initialization ---
st.subheader("Database Initialization")
if st.button("Initialize Database"):
    try:
        create_tables()
        st.success("Database tables have been successfully initialized.")
    except Exception as e:
        st.error(f"An error occurred during database initialization: {e}")
