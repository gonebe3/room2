from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config

# Tik extension'ai, be jokių blueprint'ų!
from app.utils.extensions import db, migrate

# IMPORTUOK TIK TUOS MODELIUS, KURIUOS NORI MIGRUOTI
import app.models.user
import app.models.product
# NERA import app.models.cart
# NERA import app.models.order

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)