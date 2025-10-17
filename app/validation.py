# app/validation.py

import os
import re
from typing import Optional, Tuple
import logging
from .constants import (
    MAX_FILE_SIZE_MB, ALLOWED_IMAGE_TYPES, ALLOWED_EXTENSIONS,
    MAX_SKU_LENGTH, MIN_SKU_LENGTH, SKU_PATTERN
)

logger = logging.getLogger(__name__)

def validate_file_upload(uploaded_file) -> Tuple[bool, str]:
    """
    Validate uploaded file for size, type, and security.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not uploaded_file:
        return False, "No file uploaded"

    # Check file size
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB}MB)"

    # Check file type
    if uploaded_file.type not in ALLOWED_IMAGE_TYPES:
        return False, f"File type '{uploaded_file.type}' not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"

    # Check file extension
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"File extension '{file_extension}' not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"

    # Basic security check - ensure it's actually an image
    try:
        from PIL import Image
        import io

        # Try to open the image to verify it's valid
        image_data = io.BytesIO(uploaded_file.getvalue())
        img = Image.open(image_data)
        img.verify()  # Verify the image is not corrupted

        # Reset file pointer for further use
        uploaded_file.seek(0)

    except Exception as e:
        logger.warning(f"Invalid image file uploaded: {e}")
        return False, "Uploaded file is not a valid image or is corrupted"

    return True, ""

def validate_sku(sku: str) -> Tuple[bool, str]:
    """
    Validate SKU input.

    Args:
        sku: SKU string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sku:
        return False, "SKU cannot be empty"

    sku = sku.strip()

    if len(sku) < MIN_SKU_LENGTH:
        return False, f"SKU must be at least {MIN_SKU_LENGTH} characters long"

    if len(sku) > MAX_SKU_LENGTH:
        return False, f"SKU cannot exceed {MAX_SKU_LENGTH} characters"

    if not re.match(SKU_PATTERN, sku):
        return False, "SKU can only contain letters, numbers, dashes (-), and underscores (_)"

    return True, ""

def validate_prompt_selection(prompt: str, available_prompts: list) -> Tuple[bool, str]:
    """
    Validate that selected prompt is in available options.

    Args:
        prompt: Selected prompt
        available_prompts: List of available prompt options

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt:
        return False, "Please select a prompt template"

    if prompt not in available_prompts:
        return False, f"Selected prompt '{prompt}' is not in available options"

    return True, ""

def validate_model_selection(model: str, available_models: list) -> Tuple[bool, str]:
    """
    Validate that selected model is in available options.

    Args:
        model: Selected model
        available_models: List of available model options

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not model:
        return False, "Please select an AI model"

    if model not in available_models:
        return False, f"Selected model '{model}' is not in available options"

    return True, ""

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)

    # Remove potentially dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Ensure it's not empty
    if not filename:
        filename = "uploaded_image"

    return filename

def validate_all_inputs(sku: str, uploaded_file, selected_prompt: str, selected_model: str,
                       available_prompts: list, available_models: list) -> Tuple[bool, str]:
    """
    Validate all user inputs at once and return first error found.

    Args:
        sku: Product SKU
        uploaded_file: Uploaded file object
        selected_prompt: Selected prompt template
        selected_model: Selected AI model
        available_prompts: List of available prompt options
        available_models: List of available model options

    Returns:
        Tuple of (all_valid, error_message)
    """
    # Validate SKU
    is_valid, error = validate_sku(sku)
    if not is_valid:
        return False, error

    # Validate file upload
    is_valid, error = validate_file_upload(uploaded_file)
    if not is_valid:
        return False, error

    # Validate prompt selection
    is_valid, error = validate_prompt_selection(selected_prompt, available_prompts)
    if not is_valid:
        return False, error

    # Validate model selection
    is_valid, error = validate_model_selection(selected_model, available_models)
    if not is_valid:
        return False, error

    return True, ""

def validate_redo_instructions(instructions: str) -> Tuple[bool, str]:
    """
    Validate redo instructions input.

    Args:
        instructions: Redo instructions text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not instructions or not instructions.strip():
        return False, "Please provide instructions for the redo"

    instructions = instructions.strip()

    if len(instructions) > 500:
        return False, "Redo instructions cannot exceed 500 characters"

    # Check for potentially harmful content (basic check)
    harmful_patterns = [
        r'<script', r'javascript:', r'on\w+\s*=',
        r'<\w+', r'>\w+'  # Basic HTML tag detection
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, instructions, re.IGNORECASE):
            return False, "Instructions contain potentially unsafe content"

    return True, ""

def validate_model_name(model_name: str) -> Tuple[bool, str]:
    """
    Validate AI model name input.

    Args:
        model_name: Model name string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not model_name or not model_name.strip():
        return False, "Model name cannot be empty"

    model_name = model_name.strip()

    # Allow alphanumeric, dash, underscore, and dot
    if not re.match(r'^[A-Za-z0-9\-_.]+$', model_name):
        return False, "Model name can only contain letters, numbers, dashes (-), underscores (_), and dots (.)"

    if len(model_name) > 100:
        return False, "Model name cannot exceed 100 characters"

    return True, ""

def validate_api_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Validate API key format (basic validation).

    Args:
        api_key: API key string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key cannot be empty"

    # Basic check for common API key patterns (starts with sk-, pk-, etc.)
    if not re.match(r'^[A-Za-z0-9\-_.]{20,}$', api_key):
        return False, "API key appears to be in an invalid format"

    return True, ""