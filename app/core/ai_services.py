# File: app/core/ai_services.py

import requests
import json
import base64
import os
import time
from app.config import LM_STUDIO_API_URL, STABLE_DIFFUSION_API_URL, OUTPUTS_DIR

# --- LLaVA Service Functions ---

def encode_image_to_base64(filepath):
    """Encodes an image file to a base64 string."""
    try:
        with open(filepath, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None

def get_file_mime_type(filepath):
    """Determines the MIME type based on the file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    return "image/png" if ext == ".png" else "image/jpeg"

def _call_llava_api(prompt_text: str, image_paths: list):
    """A generic helper function to call the LLaVA model."""
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
        "model": "cjpais/llava-1.6-mistral-7b-gguf",
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": 1000,
    }
    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def get_spec_from_image(image_paths: list, prompt_text: str):
    """Gets a text description for a list of images."""
    return _call_llava_api(prompt_text, image_paths)

def get_name_and_tags_from_image(image_paths: list, prompt_text: str):
    """
    Gets a product name and structured tags from the LLaVA model.
    Returns a dictionary, e.g., {"product_name": "...", "tags": {...}}
    """
    raw_response = _call_llava_api(prompt_text, image_paths)
    try:
        # Clean up potential markdown code fences
        cleaned_response = raw_response.strip().replace("```json", "").replace("```", "")
        # Parse the JSON string into a Python dictionary
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, TypeError):
        print(f"Failed to parse JSON from AI response: {raw_response}")
        return {"product_name": "AI Parsing Error", "tags": {}}

# --- Stable Diffusion Service (Omitted for brevity, assume it is here) ---
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
