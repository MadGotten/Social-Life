import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = False
    TESTING = False
    REMEMBER_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_EXTENSIONS = [".jpg", ".png"]
    UPLOAD_PROFILE_FOLDER = "website/static/profile_images"
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


class ProductionConfig(Config):
    FLASK_ENV = "production"


class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    FLASK_ENV = "development"
    TESTING = True
    SESSION_COOKIE_SECURE = False
