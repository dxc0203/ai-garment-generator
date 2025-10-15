# File: Home.py

import streamlit as st
import os
import sys
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.database import crud

# --- Initialize State, Language, and Model Status ---

# --- Page Config ---
st.set_page_config(
    page_title="AI Garment Generator",
    page_icon="🏠",
    layout="wide"
)

# --- Main Page Content ---
st.title("Welcome to the AI Garment Generator 🤖")
st.markdown("---")
st.markdown("This internal tool automates the creation of standardized, on-model product imagery for our e-commerce platform.")

st.subheader("System Status Overview")

def set_filter_and_switch(status_filter):
    st.session_state['dashboard_filter'] = status_filter
    st.switch_page("pages/1_Dashboard.py")

try:
    all_tasks = crud.get_all_tasks()
    status_counts = Counter(task['status'] for task in all_tasks)
    
    prompt_stage_statuses = {"PENDING_APPROVAL": "orange"}
    photo_stage_statuses = {
        "APPROVED": "blue",
        "GENERATING": "violet",
        "PENDING_IMAGE_REVIEW": "orange",
        "PENDING_REDO": "orange"
    }
    finalized_statuses = {
        "COMPLETED": "green",
        "REJECTED": "gray",
        "ERROR": "red"
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            st.markdown(f"#### {'Prompt Stage'}")
            st.caption('Tasks related to spec sheet creation and approval.')
            for status, color in prompt_stage_statuses.items():
                count = status_counts.get(status, 0)
                if st.button(f"{status.replace('_', ' ').title()}: {count}", key=f"status_btn_{status}", use_container_width=True):
                    set_filter_and_switch(status)
                st.markdown(f"<hr style='margin-top: -10px; border-top: 3px solid {color};'>", unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown(f"#### {'Photo Stage'}")
            st.caption('Tasks related to image generation and review.')
            for status, color in photo_stage_statuses.items():
                count = status_counts.get(status, 0)
                if st.button(f"{status.replace('_', ' ').title()}: {count}", key=f"status_btn_{status}", use_container_width=True):
                    set_filter_and_switch(status)
                st.markdown(f"<hr style='margin-top: -10px; border-top: 3px solid {color};'>", unsafe_allow_html=True)

    with col3:
        with st.container():
            st.markdown(f"#### {'Finalized Tasks'}")
            st.caption('Tasks that are completed or have exited the workflow.')
            for status, color in finalized_statuses.items():
                count = status_counts.get(status, 0)
                if st.button(f"{status.replace('_', ' ').title()}: {count}", key=f"status_btn_{status}", use_container_width=True):
                    set_filter_and_switch(status)
                st.markdown(f"<hr style='margin-top: -10px; border-top: 3px solid {color};'>", unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Could not connect to the database to load stats. Please ensure it is available. Error: {e}")

st.markdown("---")

st.subheader("How to Get Started")

guide_col1, guide_col2 = st.columns(2)

with guide_col1:
    with st.container():
        st.markdown(f"#### 1. {'Create a New Task'}")
        st.write('Navigate to the New Task page from the sidebar to begin.')
        if st.button('Go to New Task Page'):
            st.switch_page("pages/2_New_Task.py")

with guide_col2:
    with st.container():
        st.markdown(f"#### 2. {'Manage and Approve Tasks'}")
        st.write('Navigate to the Dashboard page to see all tasks.')
        if st.button('Go to Dashboard'):
            if 'dashboard_filter' in st.session_state:
                del st.session_state['dashboard_filter']
            st.switch_page("pages/1_Dashboard.py")
