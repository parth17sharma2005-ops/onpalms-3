"""
Configuration settings for PALMS Chatbot
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'palms-chatbot-secret-key-2024'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # CORS settings
    CORS_ORIGINS = [
        "https://smartwms.onpalms.com",
        "https://onpalms.com",
        "https://www.onpalms.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Google Sheets (optional)
    GOOGLE_SHEETS_ENABLED = False
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    GOOGLE_SHEET_NAME = os.environ.get('GOOGLE_SHEET_NAME', 'PALMS Chatbot Leads')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
