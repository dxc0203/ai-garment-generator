# File: app/core/ai_services.py

import requests
import json
import base64
import os
import time
from app.config import LM_STUDIO_API_URL, STABLE_DIFFUSION_API_URL, OUTPUTS_DIR
from app.settings_manager import load_settings # Import the function, not the variable

# --- NEW: Function to get available models from LM Studio ---
def get_available_lm_studio_models():
    """Gets a list of all models currently loaded in LM Studio."""
    try:
        # The endpoint for listing models is different from the chat endpoint
        models_url = LM_STUDIO_API_URL.replace("/chat/completions", "/models")
        response = requests.get(models_url)
        response.raise_for_status()
        models_data = response.json()
        # Extract the 'id' which is the model identifier
        return [model['id'] for model in models_data['data']]
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to LM Studio to get models: {e}")
        return [] # Return an empty list on error

# --- LLaVA Service for Spec Sheet Generation ---
def get_spec_from_image(image_paths: list, prompt_text: str):
    """Gets a text description for a list of images from the selected LLaVA model."""
    # --- THIS IS THE FIX ---
    # Load the most recent settings from the file every time.
    settings = load_settings()
    print("DEBUG: Settings loaded in get_spec_from_image:", settings)
    vision_model = settings.get("vision_model")
    if not vision_model:
        return "Error: No Vision Model has been selected in the Settings page."

    content_parts = [{"type": "text", "text": prompt_text}]
    for image_path in image_paths:
        base64_image = encode_image_to_base64(image_path)
        if base64_image:
            mime_type = get_file_mime_type(image_path)
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
            })
    
    headers = {"Content-Type": "application/json"}
    data = {
        "model": vision_model, # Use the model from settings
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": 1000,
    }
    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error communicating with AI model: {e}"

# --- Other functions (encode_image_to_base64, get_file_mime_type, generate_image_from_prompt) remain the same ---
def encode_image_to_base64(filepath):
    try:
        with open(filepath, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None
def get_file_mime_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return "image/png" if ext == ".png" else "image/jpeg"
def generate_image_from_prompt(prompt: str, product_code: str):
    payload = {
        "prompt": prompt,
        "negative_prompt": "deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, disgusting, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, blurry, ((((mutated hands and fingers)))), watermark, watermarked, oversaturated, censored, distorted hands, amputation, missing hands, obese, doubled face, double hands, text, error",
        "seed": -1,
        "steps": 25,
        "cfg_scale": 6,
        "width": 896,
        "height": 1152,
        "sampler_name": "DPM++ 2M Karras",
        "override_settings": {
            "sd_model_checkpoint": "RealVisXL_V4.0.safetensors"
        }
    }
    try:
        response = requests.post(url=STABLE_DIFFUSION_API_URL, json=payload)
        response.raise_for_status()
        r = response.json()
        if 'images' in r and r['images']:
            image_data = base64.b64decode(r['images'][0])
            os.makedirs(OUTPUTS_DIR, exist_ok=True)
            timestamp = int(time.time())
            output_filename = f"{product_code}_generated_{timestamp}.png"
            output_path = os.path.join(OUTPUTS_DIR, output_filename)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return output_path
        else:
            error_info = r.get('info', 'No image data received from the API.')
            return f"Error: {error_info}"
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Stable Diffusion API. {e}"
