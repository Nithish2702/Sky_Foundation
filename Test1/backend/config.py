"""
Configuration for Qatar Foundation Admin Portal Backend
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Secret key for session management (loaded from .env)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    
    # Database configuration
    # Render provides DATABASE_URL, but SQLAlchemy needs postgresql:// not postgres://
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///qatar_foundation.db'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Default session lifetime
    
    # Production vs Development settings
    IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
    
    if IS_PRODUCTION:
        SESSION_COOKIE_SECURE = True  # HTTPS only in production
        SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
        SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin with credentials
    else:
        SESSION_COOKIE_SECURE = False
        SESSION_COOKIE_HTTPONLY = False
        SESSION_COOKIE_SAMESITE = 'Lax'
    
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    
    # CORS configuration
    CORS_HEADERS = 'Content-Type'
    
    # JSON configuration
    JSON_SORT_KEYS = False
