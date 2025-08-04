from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_caching import Cache

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()
cache = Cache()


try:
    from flask_uploads import UploadSet, IMAGES
    photos = UploadSet('photos', IMAGES)
except ImportError:
    photos = None

import stripe

def init_stripe(app):
    stripe.api_key = app.config['STRIPE_SECRET_KEY']