# File: app/config.py

import logging
import os
from pathlib import Path

# --- Logging Configuration ---
def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Set specific loggers
    logging.getLogger("openai").setLevel(logging.WARNING)  # Reduce OpenAI library noise
    logging.getLogger("streamlit").setLevel(logging.WARNING)  # Reduce Streamlit noise
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

# --- NEW: Separate Prompt Folder Paths ---
# Path to the folder for spec sheet generation prompts
SPEC_SHEET_PROMPT_DIR = "data/prompts/spec_sheet"
# Path to the folder for name & tag generation prompts
NAME_TAG_PROMPT_DIR = "data/prompts/name_tag"

# Default prompt template files to use
DEFAULT_SPEC_SHEET_PROMPT = "data/prompts/spec_sheet/spec_sheet_sop.txt"
DEFAULT_NAME_TAG_PROMPT = "data/prompts/name_tag/name_and_tags_sop.txt"

# --- File Paths ---
UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"

# --- Database Configuration ---
DATABASE_PATH = "app.db"
