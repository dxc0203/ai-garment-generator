# File: app/config.py

# --- Local AI Server URLs ---
LM_STUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
STABLE_DIFFUSION_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

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
