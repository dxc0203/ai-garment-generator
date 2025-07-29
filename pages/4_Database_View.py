# File: pages/4_Database_View.py (renamed from 3_...)

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database.models import DATABASE_NAME
from app.translator import initialize_state, t, language_selector, display_model_status

# --- Initialize State and Translator ---
initialize_state()
language_selector()
display_model_status()

st.set_page_config(page_title=t("Database View"), layout="wide")
st.title(f"🗄️ {t('Raw Database View')}")
st.markdown(t("This page displays the raw data from the application's database tables for debugging and verification."))

def fetch_table_as_dataframe(table_name: str):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        st.error(t("An error occurred while fetching data from table '{}': {}").format(table_name, e))
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- Display the 'tasks' table ---
st.subheader(t("Tasks Table"))
st.markdown(t("This table contains the main record for each generation task."))
tasks_df = fetch_table_as_dataframe("tasks")
if not tasks_df.empty:
    st.dataframe(tasks_df, use_container_width=True)
else:
    st.info(t("The 'tasks' table is currently empty."))

st.divider()

# --- Display the 'spec_sheet_versions' table ---
st.subheader(t("Spec Sheet Versions Table"))
st.markdown(t("This table contains the complete edit history for every spec sheet."))
versions_df = fetch_table_as_dataframe("spec_sheet_versions")
if not versions_df.empty:
    st.dataframe(versions_df, use_container_width=True)
else:
    st.info(t("The 'spec_sheet_versions' table is currently empty."))

st.divider()

# --- Display the 'translations' table ---
st.subheader(t("Translations Table"))
st.markdown(t("This table contains the real-time translation cache."))
translations_df = fetch_table_as_dataframe("translations")
if not translations_df.empty:
    st.dataframe(translations_df, use_container_width=True)
else:
    st.info(t("The 'translations' table is currently empty."))
