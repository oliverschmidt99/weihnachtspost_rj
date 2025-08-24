# run.py
import os
from app import create_app, db

app = create_app()

def seed_standard_templates():
    """Initialisiert die Standard-Vorlagen in der Datenbank."""
    from app.models import Vorlage, Gruppe, Eigenschaft
    import json

    with app.app_context():
        # Standard-Kunde Vorlage
        if not Vorlage.query.filter_by(name="Standard-Kunde").first():
            print("Erstelle Standard-Vorlage: Kunde...")
            try:
                with open('data/standard_vorlage_kunde.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    neue_vorlage = Vorlage(name=data['name'])
                    db.session.add(neue_vorlage)
                    db.session.flush()
                    for gruppe_data in data.get('gruppen', []):
                        gruppe = Gruppe(name=gruppe_data['name'], vorlage_id=neue_vorlage.id)
                        db.session.add(gruppe)
                        db.session.flush()
                        for eigenschaft_data in gruppe_data.get('eigenschaften', []):
                            eigenschaft = Eigenschaft(
                                name=eigenschaft_data['name'],
                                datentyp=eigenschaft_data['datentyp'],
                                optionen=eigenschaft_data.get('optionen', ''),
                                gruppe_id=gruppe.id
                            )
                            db.session.add(eigenschaft)
                    db.session.commit()
            except Exception as e:
                print(f"Fehler beim Erstellen der Kunden-Vorlage: {e}")
                db.session.rollback()
        
        # (Hier kann bei Bedarf die Logik für weitere Standard-Vorlagen eingefügt werden)

def setup_database(app_instance):
    """Erstellt die Datenbank und füllt sie mit initialen Daten, falls nötig."""
    with app_instance.app_context():
        db_path = app_instance.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.exists(db_path):
             print("Datenbank wird erstellt...")
             db.create_all()
             print("Standard-Vorlagen werden hinzugefügt...")
             seed_standard_templates()
        else:
             print("Datenbank existiert bereits. Prüfe auf Standard-Vorlagen...")
             seed_standard_templates()

if __name__ == '__main__':
    setup_database(app)
    app.run(port=6060, debug=True)