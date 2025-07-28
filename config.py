import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Saugumas ir duomenų bazė
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Uploads (Flask-Uploads / Flask-Reuploaded)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5 MB
    # Flask-Uploads photos set name
    UPLOADED_PHOTOS_DEST = os.environ.get('UPLOADED_PHOTOS_DEST', UPLOAD_FOLDER)

    # Flask-Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))

    # Flask-Admin (galima papildomai konfigūruoti, jei reikia)
    ADMIN_SWATCH = os.environ.get('ADMIN_SWATCH', 'cerulean')

    # Leidžiami failų tipai nuotraukoms (naudojant Flask-Uploads)
    ALLOWED_IMAGE_EXTENSIONS = os.environ.get('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,gif,webp').split(',')

    # Galimi papildomi nustatymai
    ADMINS = [email.strip() for email in os.environ.get('ADMINS', '').split(',') if email.strip()]

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

# Jei reikia – naudok taip:
# app.config.from_object('config.DevelopmentConfig')