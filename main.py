from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config

# Extensions – tik objektai, be .init_app()
from app.utils.extensions import db, login_manager, mail, csrf, migrate, cache, admin, photos

# --- Modelių importai MIGRACIJOMS ---
import app.models.user
import app.models.product
import app.models.cart
import app.models.order
import app.models.review
import app.models.discount
import app.models.order_item
# --- Modelių importų BLOKAS pabaiga ---

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from datetime import datetime

    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    # Inicializuojame visus extension’us
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    admin.init_app(app)
    if photos:
        from flask_uploads import configure_uploads, patch_request_class
        configure_uploads(app, photos)
        patch_request_class(app, size=5 * 1024 * 1024)  # 5 MB limitas

    # -------- BLUEPRINT'Ų REGISTRACIJA --------
    # SVARBU: blueprint'us importuok ir registruok TIK VIENĄ KARTĄ!
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.discount_routes import discount_bp
    from app.routes.order_routes import order_bp
    from app.routes.product_routes import product_bp
    from app.routes.review_routes import review_bp
    from app.routes.user_routes import user_bp
    from app.routes.main_routes import main_bp

    # Registruok blueprint'us tik vieną kartą (jokių dublikatų)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(discount_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)

    # Error handleriai, jei yra
    try:
        from app.routes.errors import register_error_handlers
        register_error_handlers(app)
    except ImportError:
        pass

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)