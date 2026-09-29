import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecom_demand_forecasting_secret_key_2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'data', 'processed')
    MODEL_FOLDER = os.path.join(BASE_DIR, 'models')
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'database.db')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB Max Upload Size
    ALLOWED_EXTENSIONS = {'csv'}

    # Ensure required directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
