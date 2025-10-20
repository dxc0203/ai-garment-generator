# app/constants.py

TASK_STATUS_PENDING = "PENDING_APPROVAL"
TASK_STATUS_APPROVED = "APPROVED"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_ERROR = "ERROR"

IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]

# Validation constants
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
MAX_SKU_LENGTH = 50
MIN_SKU_LENGTH = 3
SKU_PATTERN = r'^[A-Za-z0-9\-_]+$'  # Alphanumeric, dash, underscore only

# OpenAI Models by Category
OPENAI_MODELS = {
    'text': [
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-0125',
        'gpt-3.5-turbo-1106',
        'gpt-3.5-turbo-16k',
        'gpt-3.5-turbo-instruct',
        'gpt-3.5-turbo-instruct-0914',
        'gpt-4.1',
        'gpt-4.1-2025-04-14',
        'gpt-4.1-mini',
        'gpt-4.1-mini-2025-04-14',
        'gpt-4.1-nano',
        'gpt-4.1-nano-2025-04-14',
        'gpt-4o',
        'gpt-4o-2024-05-13',
        'gpt-4o-2024-08-06',
        'gpt-4o-2024-11-20',
        'gpt-4o-audio-preview',
        'gpt-4o-audio-preview-2024-10-01',
        'gpt-4o-audio-preview-2024-12-17',
        'gpt-4o-audio-preview-2025-06-03',
        'gpt-4o-mini',
        'gpt-4o-mini-2024-07-18',
        'gpt-4o-mini-audio-preview',
        'gpt-4o-mini-audio-preview-2024-12-17',
        'gpt-4o-mini-search-preview',
        'gpt-4o-mini-search-preview-2025-03-11',
        'gpt-4o-mini-transcribe',
        'gpt-4o-mini-tts',
        'gpt-4o-search-preview',
        'gpt-4o-search-preview-2025-03-11',
        'gpt-4o-transcribe',
        'gpt-4o-transcribe-diarize',
        'gpt-5',
        'gpt-5-2025-08-07',
        'gpt-5-chat-latest',
        'gpt-5-codex',
        'gpt-5-mini',
        'gpt-5-mini-2025-08-07',
        'gpt-5-nano',
        'gpt-5-nano-2025-08-07',
        'gpt-5-pro',
        'gpt-5-pro-2025-10-06',
        'gpt-5-search-api',
        'gpt-5-search-api-2025-10-14',
        'gpt-audio',
        'gpt-audio-2025-08-28',
        'gpt-audio-mini',
        'gpt-audio-mini-2025-10-06',
        'gpt-image-1',
        'gpt-image-1-mini',
        'text-embedding-3-large',
        'text-embedding-3-small',
        'text-embedding-ada-002',
    ],
    'image': [
        'dall-e-2',
        'dall-e-3',
    ],
    'other': [
        'babbage-002',
        'davinci-002',
        'o1',
        'o1-2024-12-17',
        'o1-mini',
        'o1-mini-2024-09-12',
        'o3',
        'o3-2025-04-16',
        'o3-mini',
        'o3-mini-2025-01-31',
        'o4-mini',
        'o4-mini-2025-04-16',
        'omni-moderation-2024-09-26',
        'omni-moderation-latest',
        'sora-2',
        'sora-2-pro',
        'tts-1',
        'tts-1-1106',
        'tts-1-hd',
        'tts-1-hd-1106',
        'whisper-1',
    ]
}

# Default models for different use cases
DEFAULT_MODELS = {
    'text_only': 'gpt-3.5-turbo',  # Cheapest for text-only tasks
    'vision': 'gpt-4o',            # Best for vision/multimodal tasks
    'image_generation': 'dall-e-3' # Best for image generation
}

# Model capabilities mapping
MODEL_CAPABILITIES = {
    'text_input': OPENAI_MODELS['text'] + OPENAI_MODELS['other'],  # Models that can process text input
    'image_input': [model for model in OPENAI_MODELS['text'] if 'vision' in model.lower() or '4o' in model or '4.1' in model or '5' in model],  # Vision-capable models
    'text_output': OPENAI_MODELS['text'],  # Models that output text
    'image_output': OPENAI_MODELS['image']  # Models that output images
}