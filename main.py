from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from app.db import db  # <-- IMPORTUOJAME db iš app/db.py
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Pririšame db prie app

migrate = Migrate(app, db)

# Importuojame visus modelius (būtina migracijoms!)
from app.models import user

if __name__ == "__main__":
    app.run(debug=True)