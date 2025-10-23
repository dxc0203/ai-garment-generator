#!/usr/bin/env python3
"""
Test script to generate sample Streamlit warnings for testing the monitoring system.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.warning_monitor import log_custom_warning, get_monitor

def test_warning_generation():
    """Generate various types of warnings for testing."""
    print("Generating test warnings...")

    # Test different types of warnings
    warnings = [
        ("DeprecationWarning", "st.cache is deprecated, use @st.cache_data instead", "deprecation"),
        ("StreamlitWarning", "Using deprecated beta features", "warning"),
        ("CompatibilityWarning", "Streamlit version may have compatibility issues", "warning"),
        ("CustomWarning", "Custom application warning for testing", "info"),
        ("ErrorWarning", "Potential error condition detected", "error")
    ]

    monitor = get_monitor()

    for category, message, severity in warnings:
        log_custom_warning(message, category, severity)
        print(f"Logged: {category} - {message}")

    # Test getting warnings
    print("\nRetrieving warnings...")
    recent_warnings = monitor.get_warnings(limit=10)
    print(f"Found {len(recent_warnings)} warnings")

    for w in recent_warnings[-5:]:  # Show last 5
        print(f"  {w['category']}: {w['message'][:50]}...")

    # Test statistics
    print("\nWarning statistics:")
    stats = monitor.get_warning_stats()
    print(f"  Total: {stats['total']}")
    print(f"  Unresolved: {stats['unresolved']}")
    print(f"  Recent (24h): {stats['recent_24h']}")

if __name__ == "__main__":
    test_warning_generation()
    print("\nTest completed! Check the warnings page in the Streamlit app.")