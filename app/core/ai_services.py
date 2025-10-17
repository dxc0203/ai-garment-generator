# File: app/core/ai_services.py

import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from app.config import logger, DATABASE_PATH

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

def encode_image(image_path):
    """
    Encode an image to a Base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def call_ai_service(user_message, task_id=None, model="gpt-4o", image_path=None, test_mode=False):
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
    
# Example usage:
# response = call_ai_service("Generate a spec sheet for the uploaded image.", task_id=123, image_path="/path/to/image.jpg")