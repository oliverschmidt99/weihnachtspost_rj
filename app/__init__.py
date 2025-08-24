# app/__init__.py
import os
from flask import Flask
from flask_migrate import Migrate
from .models import db

def create_app():
    """Erstellt und konfiguriert die Flask-Anwendung."""
    app = Flask(__name__, 
                static_folder="../static", 
                template_folder="../templates",
                instance_relative_config=True)

    # Konfiguration
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    upload_path = os.path.join(basedir, '..', 'upload_files')
    os.makedirs(upload_path, exist_ok=True)

    app.config["SECRET_KEY"] = "dein-super-geheimer-schluessel-hier"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_path, 'kundenverwaltung.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = upload_path
    
    # Datenbank und Migration initialisieren
    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        # Blueprints (Routen-Gruppen) registrieren
        from .routes import main, vorlagen, kontakte, api, import_export
        app.register_blueprint(main.bp)
        app.register_blueprint(vorlagen.bp)
        app.register_blueprint(kontakte.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(import_export.bp)

        return app