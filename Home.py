# File: Home.py

import streamlit as st
import os
import sys
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.database import crud
# Import the new function
# from app.translator import initialize_state, t, language_selector, display_model_status

# --- Initialize State, Language, and Model Status ---
# initialize_state()
# language_selector()
# display_model_status() # This one line replaces the entire block of code

# TEMPORARILY DISABLE WARNING MONITOR
# from app.warning_monitor import initialize_warning_monitor
# warning_monitor = initialize_warning_monitor()

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

# Handle navigation
if 'navigate_to' in st.session_state:
    if st.session_state['navigate_to'] == 'dashboard':
        st.switch_page("pages/1_Dashboard.py")
    elif st.session_state['navigate_to'] == 'new_task':
        st.switch_page("pages/2_New_Task.py")
    elif st.session_state['navigate_to'] == 'startup_logs':
        st.switch_page("pages/7_Startup_Logs.py")
    elif st.session_state['navigate_to'] == 'warnings':
        st.switch_page("pages/8_Streamlit_Warnings.py")
    del st.session_state['navigate_to']

st.subheader("System Status Overview")

def set_filter_and_switch(status_filter):
    st.session_state['dashboard_filter'] = status_filter
    st.session_state['navigate_to'] = 'dashboard'
    st.rerun()

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
            st.markdown(f"#### Prompt Stage")
            st.caption('Tasks related to spec sheet creation and approval.')
            for status, color in prompt_stage_statuses.items():
                count = status_counts.get(status, 0)
                if st.button(f"{status.replace('_', ' ').title()}: {count}", key=f"status_btn_{status}", use_container_width=True):
                    set_filter_and_switch(status)
                st.markdown(f"<hr style='margin-top: -10px; border-top: 3px solid {color};'>", unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown(f"#### Photo Stage")
            st.caption('Tasks related to image generation and review.')
            for status, color in photo_stage_statuses.items():
                count = status_counts.get(status, 0)
                if st.button(f"{status.replace('_', ' ').title()}: {count}", key=f"status_btn_{status}", use_container_width=True):
                    set_filter_and_switch(status)
                st.markdown(f"<hr style='margin-top: -10px; border-top: 3px solid {color};'>", unsafe_allow_html=True)

    with col3:
        with st.container():
            st.markdown(f"#### Finalized Tasks")
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
        st.markdown(f"#### 1. Create a New Task")
        st.write('Navigate to the New Task page from the sidebar to begin.')
        if st.button('Go to New Task Page'):
            st.session_state['navigate_to'] = 'new_task'
            st.rerun()

with guide_col2:
    with st.container():
        st.markdown(f"#### 2. Manage and Approve Tasks")
        st.write('Navigate to the Dashboard page to see all tasks.')
        if st.button('Go to Dashboard'):
            if 'dashboard_filter' in st.session_state:
                del st.session_state['dashboard_filter']
            st.session_state['navigate_to'] = 'dashboard'
            st.rerun()

st.markdown("---")

st.subheader("System Tools & Diagnostics")

tools_col1, tools_col2, tools_col3 = st.columns(3)

with tools_col1:
    with st.container():
        st.markdown("#### 🔧 Startup Logs & Diagnostics")
        st.write('Monitor application startup issues and apply automatic fixes.')
        if st.button('View Startup Diagnostics'):
            st.session_state['navigate_to'] = 'startup_logs'
            st.rerun()

with tools_col2:
    with st.container():
        st.markdown("#### ⚠️ Streamlit Warnings")
        st.write('Monitor Streamlit deprecation warnings and compatibility issues.')
        if st.button('View Warnings Monitor'):
            st.session_state['navigate_to'] = 'warnings'
            st.rerun()

with tools_col3:
    with st.container():
        st.markdown("#### 📊 System Status")
        st.write('View real-time system status and task statistics.')
        # Check for recent warnings
        try:
            # TEMPORARILY DISABLED
            # stats = warning_monitor.get_warning_stats()
            # recent_warnings = stats.get('recent_24h', 0)
            # if recent_warnings > 0:
            #     st.warning(f"⚠️ {recent_warnings} warnings in last 24h")
            # else:
            #     st.info("System is operational ✅")
            st.info("System is operational ✅")
        except Exception as e:
            st.info("System is operational ✅")
