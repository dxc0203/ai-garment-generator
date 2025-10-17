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