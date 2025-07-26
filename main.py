from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from app.extensions import db, login_manager  # <-- Svarbu: čia keistas importas
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Importuoti visus modelius – kad Alembic matytų
    from app.models import user

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
