# File: app/core/ai_services.py

import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_connection():
    """Test the connection to OpenAI's API using the cheapest model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not found in .env file."

    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cheapest model
            messages=[{"role": "user", "content": "Hello"}]
        )
        return f"Connection successful. Response: {response['choices'][0]['message']['content']}"
    except Exception as e:
        return f"Error: {e}"

def call_ai_service(user_message, task_id=None):
    """
    Call the AI service with a user message and optional task ID for context.
    """
    import openai
    import sqlite3

    # Prepare the conversation history if task_id is provided
    conversation_history = []
    if task_id:
        conn = sqlite3.connect("app.db")  # Update with your database name
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE task_id = ?", (task_id,))
        conversation_history = cursor.fetchall()
        conn.close()

    # Format the conversation for the AI
    messages = []
    for user_msg, ai_resp in conversation_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_resp})

    # Add the new user message
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI API using the latest interface
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        ai_response = response["choices"][0]["message"]["content"]
        return ai_response
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"Failed to call OpenAI API: {e}")


test_openai_connection()