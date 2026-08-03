import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-flask-secret-key')
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-flask-secret-key')  # Standard Flask secret key
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # Long-lived sessions for production
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/smartinbox')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
