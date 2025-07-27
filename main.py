from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config

# Importuojame tik extension'ų instancijas
from app.utils.extensions import db, login_manager, mail, csrf, migrate, cache, admin, photos

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Prijungiame extension'us
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

    # Blueprint'ų registracija – pilnai atskirtas maršrutų valdymas
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.discount_routes import discount_bp
    from app.routes.order_routes import order_bp
    from app.routes.product_routes import product_bp
    from app.routes.review_routes import review_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(discount_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(user_bp)

    # Error handleriai (jei sukursite app/routes/errors.py ar panašiai)
    try:
        from app.routes.errors import register_error_handlers
        register_error_handlers(app)
    except ImportError:
        pass  # Jei dar neturite error handlerių – praleidžia

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
