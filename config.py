import os

class Config:
    # Secret key for signing sessions and cookies
    SECRET_KEY = os.environ.get('SECRET_KEY', 'schemeai_super_secret_key_1029384756')
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite Database URI (for SQLAlchemy if upgraded, or direct connection paths)
    DB_PATH = os.path.join(BASE_DIR, 'database', 'schemeai.db')
    
    # Upload folder for scheme images and CSV uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'csv', 'png', 'jpg', 'jpeg'}
    
    # Application settings
    APP_NAME = "SchemeAI"
    TAGLINE = "Find the Right Government Scheme in Seconds with AI"
