# File: app/core/ai_services.py

import requests
import json
import base64
import os
import time
from app.config import LM_STUDIO_API_URL, STABLE_DIFFUSION_API_URL, OUTPUTS_DIR
from app.settings_manager import load_settings

# --- 辅助函数 ---
def encode_image_to_base64(filepath):
    try:
        with open(filepath, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError: return None

def get_file_mime_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return "image/png" if ext == ".png" else "image/jpeg"

# --- 针对不同服务商的函数 ---

def _call_local_vision_model(prompt_text: str, image_paths: list, model_name: str):
    """调用本地LM Studio服务器执行视觉任务"""
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
    data = {"model": model_name, "messages": [{"role": "user", "content": content_parts}], "max_tokens": 1000}
    
    try:
        response = requests.post(LM_STUDIO_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def _call_online_vision_model(prompt_text: str, image_paths: list, model_name: str, provider: str):
    """一个用于调用任何在线视觉模型的通用占位函数"""
    api_key_name = f"{provider.upper()}_API_KEY"
    api_key = os.getenv(api_key_name)
    if not api_key:
        return f"Error: {api_key_name} not found in .env file."
    
    return f"Placeholder: Would call {provider.title()} model '{model_name}' with the provided images."

# --- 主要的路由函数 ---

def get_spec_from_image(image_paths: list, prompt_text: str):
    """用于获取规格表的主路由函数"""
    settings = load_settings()
    service_config = settings.get("vision_service", {})
    provider = service_config.get("provider")
    model = service_config.get("model")

    if not provider or not model:
        return "Error: Vision service not configured in Settings."

    if provider == "local":
        return _call_local_vision_model(prompt_text, image_paths, model)
    elif provider in ["google", "openai", "anthropic"]:
        return _call_online_vision_model(prompt_text, image_paths, model, provider)
    else:
        return f"Error: Unknown vision provider '{provider}'."

def get_name_and_tags_from_image(image_paths: list, prompt_text: str):
    """用于获取产品名称和标签的主路由函数"""
    settings = load_settings()
    service_config = settings.get("vision_service", {})
    provider = service_config.get("provider")
    model = service_config.get("model")

    if not provider or not model:
        return {"product_name": "Error", "tags": {"error": "Vision service not configured"}}

    raw_response = "Error: Provider not configured"
    if provider == "local":
        raw_response = _call_local_vision_model(prompt_text, image_paths, model)
    elif provider in ["google", "openai", "anthropic"]:
        raw_response = _call_online_vision_model(prompt_text, image_paths, model, provider)

    try:
        cleaned_response = raw_response.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, TypeError):
        return {"product_name": "AI Parsing Error", "tags": {}}

def get_available_lm_studio_models():
    try:
        models_url = LM_STUDIO_API_URL.replace("/chat/completions", "/models")
        response = requests.get(models_url)
        response.raise_for_status()
        models_data = response.json()
        return [model['id'] for model in models_data['data']]
    except requests.exceptions.RequestException:
        return []

# --- Stable Diffusion 服务 (未改变) ---
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
