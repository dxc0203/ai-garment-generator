# File: app/settings_manager.py

import json
import os

SETTINGS_FILE = "data/settings.json"
DEFAULT_SETTINGS = {
    "vision_model": None,
    "language_model": None
}

def load_settings():
    """Loads the settings from the JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_SETTINGS

def save_settings(settings: dict):
    """Saves the settings to the JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

# Load the settings once when the app starts
settings = load_settings()
