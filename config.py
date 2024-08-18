import os
from dotenv import load_dotenv
load_dotenv(override=True)

FLASK_ENV = os.getenv('FLASK_ENV')
DEBUG = os.getenv('DEBUG')
TESTING = os.getenv('TESTING')
SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI =  os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE')
REMEMBER_COOKIE_SAMESITE = 'Lax'
UPLOAD_PROFILE_FOLDER = 'website/static/profile_images'
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
UPLOAD_EXTENSIONS = ['.jpg', '.png']