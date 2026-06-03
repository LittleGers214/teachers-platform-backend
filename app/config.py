import os
from dotenv import load_dotenv  # установи python-dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-key'
    # Для PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://platform_user:123456789@localhost:5432/platform_teachers'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MAIL_SERVER = 'smtp.yandex.ru'   # или ваш SMTP
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'your-email@yandex.ru'
    MAIL_PASSWORD = 'your-password'
    MAIL_DEFAULT_SENDER = ('Platform', 'your-email@yandex.ru')