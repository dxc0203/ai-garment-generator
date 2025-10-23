# File: pages/8_Streamlit_Warnings.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Import warning monitor
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.warning_monitor import get_monitor

# Initialize monitor
monitor = get_monitor()

# Page config
st.set_page_config(page_title="Streamlit Warnings Monitor", layout="wide")
st.title("⚠️ Streamlit Warnings Monitor")
st.markdown("Monitor and manage Streamlit deprecation warnings and compatibility issues.")

# Get warning statistics
stats = monitor.get_warning_stats()

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Warnings", stats.get('total', 0))

with col2:
    unresolved = stats.get('unresolved', 0)
    st.metric("Unresolved", unresolved, delta=f"{'⚠️' if unresolved > 0 else '✅'}")

with col3:
    recent = stats.get('recent_24h', 0)
    st.metric("Last 24h", recent, delta=f"{'🔥' if recent > 5 else '📊'}")

with col4:
    st.metric("Categories", len(stats.get('by_category', {})))

st.markdown("---")

# Filters
st.subheader("Filters & Search")

col1, col2, col3, col4 = st.columns(4)

with col1:
    show_resolved = st.checkbox("Show Resolved", value=False)

with col2:
    category_filter = st.selectbox(
        "Filter by Category",
        ["All"] + list(stats.get('by_category', {}).keys()),
        index=0
    )

with col3:
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All", "error", "warning", "deprecation", "info"],
        index=0
    )

with col4:
    limit = st.selectbox(
        "Show Last",
        [50, 100, 200, 500, 1000],
        index=1
    )

# Get filtered warnings
warnings = monitor.get_warnings(
    limit=limit,
    resolved=None if show_resolved else False,
    category=None if category_filter == "All" else category_filter,
    severity=None if severity_filter == "All" else severity_filter
)

st.markdown("---")

# Charts section
st.subheader("Warning Analytics")

if warnings:
    # Convert to DataFrame for analysis
    df = pd.DataFrame(warnings)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Warnings by category
        if not df.empty:
            category_counts = df['category'].value_counts()
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Warnings by Category",
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        # Warnings over time (last 30 days)
        if not df.empty:
            df_last_30 = df[df['timestamp'] >= (datetime.now() - timedelta(days=30))]
            if not df_last_30.empty:
                daily_counts = df_last_30.groupby(df_last_30['timestamp'].dt.date).size()
                fig = px.line(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    title="Warnings Over Time (30 days)",
                    labels={'x': 'Date', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Warnings table
st.subheader(f"Warning Details ({len(warnings)} warnings)")

if warnings:
    # Prepare data for display
    display_data = []
    for w in warnings:
        display_data.append({
            'ID': w['id'],
            'Timestamp': datetime.fromisoformat(w['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
            'Category': w['category'],
            'Severity': w['severity'],
            'Message': w['message'][:100] + '...' if len(w['message']) > 100 else w['message'],
            'File': w['filename'] or 'N/A',
            'Line': w['lineno'] or 'N/A',
            'Resolved': '✅' if w['resolved'] else '❌'
        })

    df_display = pd.DataFrame(display_data)

    # Add selection column for bulk actions
    if 'selected_warnings' not in st.session_state:
        st.session_state.selected_warnings = set()

    # Display table with checkboxes
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={
            'ID': st.column_config.NumberColumn('ID', width='small'),
            'Timestamp': st.column_config.TextColumn('Timestamp', width='medium'),
            'Category': st.column_config.TextColumn('Category', width='medium'),
            'Severity': st.column_config.TextColumn('Severity', width='small'),
            'Message': st.column_config.TextColumn('Message', width='large'),
            'File': st.column_config.TextColumn('File', width='medium'),
            'Line': st.column_config.TextColumn('Line', width='small'),
            'Resolved': st.column_config.TextColumn('Resolved', width='small')
        }
    )

    # Bulk actions
    st.subheader("Bulk Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    with col2:
        if st.button("✅ Mark Selected as Resolved", type="secondary"):
            # For now, just show info - would need selection UI
            st.info("Select warnings from the table above to mark as resolved")

    with col3:
        if st.button("🗑️ Clear Old Resolved Warnings", type="secondary"):
            if st.checkbox("Confirm deletion of resolved warnings older than 30 days"):
                # This would delete old resolved warnings
                st.success("Old resolved warnings cleared (feature not yet implemented)")

else:
    st.info("No warnings found matching the current filters.")

# Individual warning details
st.markdown("---")
st.subheader("Warning Details")

if warnings:
    # Simple expander for each warning
    for i, warning in enumerate(warnings[:10]):  # Show first 10
        with st.expander(f"Warning {warning['id']}: {warning['category']} - {warning['message'][:50]}..."):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Timestamp:** {datetime.fromisoformat(warning['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Category:** {warning['category']}")
                st.write(f"**Severity:** {warning['severity']}")
                st.write(f"**Resolved:** {'Yes' if warning['resolved'] else 'No'}")

            with col2:
                st.write(f"**File:** {warning['filename'] or 'N/A'}")
                st.write(f"**Line:** {warning['lineno'] or 'N/A'}")
                st.write(f"**Function:** {warning['function'] or 'N/A'}")

            st.write(f"**Message:** {warning['message']}")

            if warning['stack_trace']:
                st.write(f"**Stack Trace:** {warning['stack_trace']}")

            # Action buttons
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if not warning['resolved']:
                    if st.button(f"Mark as Resolved #{warning['id']}", key=f"resolve_{warning['id']}"):
                        notes = st.text_input(f"Resolution notes for #{warning['id']}", key=f"notes_{warning['id']}")
                        if notes:
                            monitor.mark_resolved(warning['id'], notes)
                            st.success(f"Warning #{warning['id']} marked as resolved!")
                            st.rerun()

            with action_col2:
                if st.button(f"View Full Details #{warning['id']}", key=f"details_{warning['id']}"):
                    st.json(warning)

# Footer with recommendations
st.markdown("---")
st.subheader("Recommendations")

if stats.get('unresolved', 0) > 0:
    st.warning(f"⚠️ You have {stats['unresolved']} unresolved warnings. Consider reviewing and addressing them.")

if stats.get('recent_24h', 0) > 5:
    st.error("🔥 High warning frequency detected! Check for compatibility issues.")

st.info("""
**Maintenance Tips:**
- Review deprecation warnings regularly
- Update to newer Streamlit versions when safe
- Test updates in a development environment first
- Use the compatibility checker before major updates
""")

# Auto-refresh option
st.markdown("---")
auto_refresh = st.checkbox("Auto-refresh every 30 seconds", value=False)
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()