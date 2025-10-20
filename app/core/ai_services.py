# File: app/core/ai_services.py

import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from app.config import logger, DATABASE_PATH
from app.constants import DEFAULT_MODELS, MODEL_CAPABILITIES, OPENAI_MODELS

# Load environment variables from .env file
load_dotenv()

# Monkey patch httpx to handle the proxies argument issue
import httpx
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    # Remove proxies from kwargs if it exists
    kwargs.pop('proxies', None)
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

def get_openai_client():
    """Get or create OpenAI client with proper configuration."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Create client - httpx proxy issue is handled by monkey patch above
    return OpenAI(api_key=api_key)

def get_models_by_capability(capability):
    """
    Get OpenAI models filtered by capability.
    
    Args:
        capability: One of 'text_input', 'image_input', 'text_output', 'image_output'
    
    Returns:
        List of model names that support the given capability
    """
    return MODEL_CAPABILITIES.get(capability, [])

def get_available_openai_models():
    """
    Fetch all currently available OpenAI models from the API.
    
    Returns:
        Dict with categorized models or None if error
    """
    try:
        client = get_openai_client()
        models = client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        logger.error(f"Failed to fetch OpenAI models: {e}")
        return []

# Global client reference
client = None

def encode_image(image_path):
    """
    Encode an image to a Base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def call_ai_service(user_message, task_id=None, model=DEFAULT_MODELS['vision'], image_path=None, test_mode=False):
    """
    Call the AI service with a user message, optional task ID for context, model selection, optional image input, and test mode.
    If test_mode is True, return a mock response for testing purposes.
    """
    import sqlite3
    
    logger.info(f"AI service called with model: {model}, task_id: {task_id}, test_mode: {test_mode}, has_image: {image_path is not None}")
    
    if test_mode:
        # Return a mock response for testing
        response = f"[TEST MODE] AI response for prompt: '{user_message}' using model: {model}"
        if image_path:
            response = f"[TEST MODE] Spec sheet generated for image '{image_path}' with prompt: '{user_message}' using model: {model}"
        logger.info(f"Test mode response: {response}")
        return response

    # Prepare the conversation history if task_id is provided
    conversation_history = []
    if task_id:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE task_id = ?", (task_id,))
            conversation_history = cursor.fetchall()
            conn.close()
            logger.debug(f"Retrieved {len(conversation_history)} conversation history items for task {task_id}")
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving conversation history: {e}")
            raise RuntimeError(f"Failed to retrieve conversation history: {e}")

    # Format the conversation for the AI
    messages = []
    for user_msg, ai_resp in conversation_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_resp})

    # Add the new user message
    if image_path:
        try:
            base64_image = encode_image(image_path)
            user_content = [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
            ]
            logger.debug(f"Encoded image for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise RuntimeError(f"Failed to process image: {e}")
    else:
        user_content = user_message

    messages.append({"role": "user", "content": user_content})

    # Call OpenAI API using the specified model
    try:
        logger.info(f"Making OpenAI API call with model {model}")
        # Get client if not already initialized
        global client
        if client is None:
            client = get_openai_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI API call successful, response length: {len(ai_response)}")
        return ai_response
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise RuntimeError(f"Failed to call OpenAI API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in AI service: {e}")
        raise RuntimeError(f"Unexpected error: {e}")
    
