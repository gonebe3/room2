from dotenv import load_dotenv
load_dotenv()
import os

from flask import Flask
from config import ProductionConfig, DevelopmentConfig


# Extensions 
from app.utils.extensions import db, login_manager, mail, csrf, migrate, cache, photos, init_stripe
from app.utils.context_processors import inject_categories, inject_now

# --- Modelių importai MIGRACIJOMS ---
import app.models.user
import app.models.product
import app.models.cart
import app.models.order
import app.models.review
import app.models.discount
import app.models.order_item
import app.models.category
import app.models.login_attempt
import app.models.payment_attempt


def create_app():
    app = Flask(__name__)

    config_name = os.environ.get('FLASK_CONFIG', 'DevelopmentConfig')
    if config_name == 'ProductionConfig':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    app.context_processor(inject_now)
    app.context_processor(inject_categories)

    # Inicializuojame visus extension’us
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    init_stripe(app)
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
    from app.routes.stripe_routes import stripe_bp
    from app.routes.error_routes import errors_bp


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
    app.register_blueprint(stripe_bp)
    app.register_blueprint(errors_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)