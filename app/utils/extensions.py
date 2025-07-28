from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_caching import Cache
from flask_admin import Admin

# Duomenų bazė (ORM)
db = SQLAlchemy()

# Autentifikacija/sesijos
login_manager = LoginManager()

# El. paštas
mail = Mail()

# CSRF apsauga visoms POST formoms (integruojasi su Flask-WTF)
csrf = CSRFProtect()

# Migracijų sistema (Alembic) – inicijuosite su app pagrindiniame faile
migrate = Migrate()

# Cache (naudokite SimpleCache arba, jei reikia, Redis ar Memcached)
cache = Cache()

# Admino panelė
admin = Admin()

# (Papildomai, jei naudosite Flask-Uploads)
try:
    from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
    photos = UploadSet('photos', IMAGES)
except ImportError:
    photos = None 