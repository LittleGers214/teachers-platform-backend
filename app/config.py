import os
from dotenv import load_dotenv  # установи python-dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-key'
    # Для PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://platform_user:strong_password@localhost:5432/platform_teachers'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    UPLOAD_FOLDER = os.makedirs(os.path.join(basedir, 'uploads', 'documents'), exist_ok=True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024