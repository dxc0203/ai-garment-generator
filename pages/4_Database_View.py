# File: pages/4_Database_View.py (renamed from 3_...)

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import logging

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database.models import DATABASE_NAME, create_tables

# --- Initialize State ---
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

# --- Display the 'chat_history' table ---
st.subheader("Chat History Table")
st.markdown("This table contains the chat history for each task.")
chat_history_df = fetch_table_as_dataframe("chat_history")
if not chat_history_df.empty:
    st.dataframe(chat_history_df, use_container_width=True)
else:
    st.info("The 'chat_history' table is currently empty.")

# --- Ensure Database Initialization ---
st.subheader("Database Initialization")
if st.button("Initialize Database"):
    try:
        create_tables()
        st.success("Database tables have been successfully initialized.")
    except Exception as e:
        st.error(f"An error occurred during database initialization: {e}")
