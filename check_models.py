#!/usr/bin/env python3
"""
Model Availability Checker for AI Garment Generator
Checks which OpenAI models are still available and suggests replacements for deprecated ones.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Monkey patch httpx to handle the proxies argument issue
import httpx
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    # Remove proxies from kwargs if it exists
    kwargs.pop('proxies', None)
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

from openai import OpenAI
from app.constants import OPENAI_MODELS, DEFAULT_MODELS
from app.settings_manager import load_settings, save_settings

def check_model_availability():
    """Check which models are available and suggest replacements for unavailable ones."""
    print("🔍 Checking OpenAI model availability...")

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("   Please set your OpenAI API key in the .env file.")
        return False

    try:
        client = OpenAI(api_key=api_key)
        available_models = client.models.list()
        available_model_ids = {model.id for model in available_models.data}

        print(f"✅ Successfully connected to OpenAI API. Found {len(available_model_ids)} available models.")

        # Check all models in our constants
        unavailable_models = []
        all_configured_models = set()

        for category, models in OPENAI_MODELS.items():
            all_configured_models.update(models)

        for model in all_configured_models:
            if model not in available_model_ids:
                unavailable_models.append(model)

        if unavailable_models:
            print(f"\n⚠️  {len(unavailable_models)} configured models are no longer available:")
            print("-" * 60)

            # Group by category and suggest replacements
            replacements_suggested = set()
            suggestions_list = []

            for model in unavailable_models:
                category = None
                for cat, models in OPENAI_MODELS.items():
                    if model in models:
                        category = cat
                        break

                replacement = suggest_replacement(model, category, available_model_ids)

                print(f"❌ {model}")
                if replacement:
                    print(f"   ➡️  Suggested replacement: {replacement}")
                    replacements_suggested.add(replacement)
                    suggestions_list.append({
                        "unavailable_model": model,
                        "suggested_replacement": replacement,
                        "category": category
                    })
                else:
                    print("   ➡️  No suitable replacement found in current available models")
                    suggestions_list.append({
                        "unavailable_model": model,
                        "suggested_replacement": None,
                        "category": category
                    })
                print()

            # Save suggestions to settings
            if suggestions_list:
                current_settings = load_settings()
                current_settings["model_suggestions"] = suggestions_list
                save_settings(current_settings)
                print("💾 Model replacement suggestions saved to settings.")
                print("   You can review and update your default models in the Settings page.")
                print()

            if replacements_suggested:
                print("💡 To update your configuration:")
                print("   1. Edit app/constants.py")
                print("   2. Replace unavailable models with suggested replacements")
                print("   3. Or update your default models in the Settings page")
                print()

            return len(unavailable_models) == 0
        else:
            print("✅ All configured models are available!")
            return True

    except Exception as e:
        print(f"❌ Failed to check model availability: {e}")
        print("   This might be due to network issues or invalid API key.")
        return False

def suggest_replacement(unavailable_model, category, available_models):
    """Suggest a replacement model based on the unavailable model's characteristics."""

    # Define replacement mappings for common deprecated models
    replacements = {
        # GPT-3.5 variants
        'gpt-3.5-turbo': 'gpt-3.5-turbo',
        'gpt-3.5-turbo-0301': 'gpt-3.5-turbo',
        'gpt-3.5-turbo-0613': 'gpt-3.5-turbo',
        'gpt-3.5-turbo-16k': 'gpt-3.5-turbo',
        'gpt-3.5-turbo-16k-0613': 'gpt-3.5-turbo',

        # GPT-4 variants
        'gpt-4': 'gpt-4o',
        'gpt-4-0314': 'gpt-4o',
        'gpt-4-0613': 'gpt-4o',
        'gpt-4-32k': 'gpt-4o',
        'gpt-4-32k-0314': 'gpt-4o',
        'gpt-4-32k-0613': 'gpt-4o',

        # GPT-4 Turbo variants
        'gpt-4-turbo': 'gpt-4o',
        'gpt-4-turbo-2024-04-09': 'gpt-4o',
        'gpt-4-turbo-preview': 'gpt-4o',

        # GPT-4 Vision variants
        'gpt-4-vision-preview': 'gpt-4o',
        'gpt-4-1106-vision-preview': 'gpt-4o',

        # DALL-E variants
        'dall-e-2': 'dall-e-2',  # Still available
        'dall-e-3': 'dall-e-3',  # Still available

        # Audio models
        'whisper-1': 'whisper-1',  # Still available
        'tts-1': 'tts-1',  # Still available
        'tts-1-1106': 'tts-1',
        'tts-1-hd': 'tts-1-hd',
        'tts-1-hd-1106': 'tts-1-hd',
    }

    # Check if we have a direct replacement mapping
    if unavailable_model in replacements:
        replacement = replacements[unavailable_model]
        if replacement in available_models:
            return replacement

    # If no direct mapping, find a suitable replacement based on category
    if category == 'text':
        # For text models, prefer newer GPT models in this order
        preferred_text_models = [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4.1', 'gpt-4.1-mini',
            'gpt-3.5-turbo', 'gpt-3.5-turbo-0125'
        ]
        for model in preferred_text_models:
            if model in available_models:
                return model

    elif category == 'image':
        # For image models, prefer DALL-E 3 over DALL-E 2
        if 'dall-e-3' in available_models:
            return 'dall-e-3'
        elif 'dall-e-2' in available_models:
            return 'dall-e-2'

    # If we can't find a category-specific replacement, return the first available model
    # from the same category if any exist
    if category and category in OPENAI_MODELS:
        for model in OPENAI_MODELS[category]:
            if model in available_models:
                return model

    return None

if __name__ == "__main__":
    success = check_model_availability()
    sys.exit(0 if success else 1)