# app.py
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import (Flask, render_template, request, redirect, url_for, 
                   flash, jsonify, send_from_directory, Response)
from flask_migrate import Migrate
from sqlalchemy.orm import joinedload

from src.models import db, Vorlage, Gruppe, Eigenschaft, Kontakt
from src import importer, exporter # Nur noch diese beiden werden benötigt

# -- Konfiguration --
BACKUP_FOLDER = "backups"
UPLOAD_FOLDER = "upload_files"
ALLOWED_EXTENSIONS = {"csv", "msg", "oft", "txt", "vcf", "xlsx"} # rtf entfernt, da nicht implementiert

app = Flask(__name__, static_folder="static")

basedir = os.path.abspath(os.path.dirname(__file__))
# ... (Rest der Konfiguration bleibt gleich) ...
instance_path = os.path.join(basedir, "instance")
os.makedirs(instance_path, exist_ok=True)
backup_path = os.path.join(basedir, BACKUP_FOLDER)
os.makedirs(backup_path, exist_ok=True)
upload_path = os.path.join(basedir, UPLOAD_FOLDER)
os.makedirs(upload_path, exist_ok=True)

app.config["SECRET_KEY"] = "dein-super-geheimer-schluessel-hier"
app.config["SQLALCHEMY_DATABASE_URI"] = (f"sqlite:///{os.path.join(instance_path, 'kundenverwaltung.db')}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = upload_path

db.init_app(app)
migrate = Migrate(app, db)

from src import models
# ... (seed_standard_templates und create_database bleiben gleich) ...
def seed_standard_templates():
    with app.app_context():
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
                            eigenschaft = Eigenschaft(name=eigenschaft_data['name'],datentyp=eigenschaft_data['datentyp'],optionen=eigenschaft_data.get('optionen', ''),gruppe_id=gruppe.id)
                            db.session.add(eigenschaft)
                    db.session.commit()
            except Exception as e:
                print(f"Fehler beim Erstellen der Kunden-Vorlage: {e}")
                db.session.rollback()

        if not Vorlage.query.filter_by(name="Standard-Mitarbeiter").first():
            print("Erstelle Standard-Vorlage: Mitarbeiter...")
            try:
                with open('data/standard_vorlage_mitarbeiter.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mitarbeiter_vorlage_id_fuer_verknuepfung = Vorlage.query.count() + 1
                    neue_vorlage = Vorlage(name=data['name'])
                    db.session.add(neue_vorlage)
                    db.session.flush()
                    for gruppe_data in data.get('gruppen', []):
                        gruppe = Gruppe(name=gruppe_data['name'], vorlage_id=neue_vorlage.id)
                        db.session.add(gruppe)
                        db.session.flush()
                        for eigenschaft_data in gruppe_data.get('eigenschaften', []):
                            optionen = eigenschaft_data.get('optionen', '')
                            if "vorlage_id" in optionen:
                                optionen = f"vorlage_id:{mitarbeiter_vorlage_id_fuer_verknuepfung}"
                            eigenschaft = Eigenschaft(name=eigenschaft_data['name'],datentyp=eigenschaft_data['datentyp'],optionen=optionen,gruppe_id=gruppe.id)
                            db.session.add(eigenschaft)
                    db.session.commit()
            except Exception as e:
                print(f"Fehler beim Erstellen der Mitarbeiter-Vorlage: {e}")
                db.session.rollback()

def create_database():
    with app.app_context():
        db_path = os.path.join(instance_path, "kundenverwaltung.db")
        if not os.path.exists(db_path):
            db.create_all()
            seed_standard_templates()
        else:
            seed_standard_templates()

# --- Routen ---
@app.route("/")
def index():
    return render_template("index.html")

# ... (API-Routen bleiben gleich) ...
@app.route("/api/attribute-suggestions")
def attribute_suggestions():
    return send_from_directory('data', 'attribute_suggestions.json')

@app.route("/api/selection-options")
def selection_options():
    return send_from_directory('data', 'selection_options.json')

@app.route("/api/kontakte-by-vorlage/<int:vorlage_id>")
def get_kontakte_by_vorlage(vorlage_id):
    kontakte = Kontakt.query.filter_by(vorlage_id=vorlage_id).all()
    result = []
    for k in kontakte:
        data = k.get_data()
        display_name = data.get('Name') or f"{data.get('Vorname', '')} {data.get('Nachname', '')}".strip() or data.get('Firmenname', f"Kontakt ID: {k.id}")
        result.append({"id": k.id, "display_name": display_name})
    return jsonify(result)

@app.route("/api/kontakt/<int:kontakt_id>/update", methods=["POST"])
def update_kontakt_field(kontakt_id):
    kontakt = Kontakt.query.get_or_404(kontakt_id)
    data = request.get_json()
    field_name = data.get('field')
    new_value = data.get('value')
    if field_name is None or new_value is None:
        return jsonify({"success": False, "error": "Fehlende Daten"}), 400
    kontakt_daten = kontakt.get_data()
    kontakt_daten[field_name] = new_value
    kontakt.set_data(kontakt_daten)
    db.session.commit()
    return jsonify({"success": True, "message": "Feld aktualisiert"})
    
@app.route("/api/kontakt/neu", methods=["POST"])
def create_kontakt():
    data = request.get_json()
    vorlage_id = data.get('vorlage_id')
    kontakt_daten = data.get('daten')
    if not vorlage_id or kontakt_daten is None:
        return jsonify({"success": False, "error": "Fehlende Daten"}), 400
    neuer_kontakt = Kontakt(vorlage_id=vorlage_id)
    neuer_kontakt.set_data(kontakt_daten)
    db.session.add(neuer_kontakt)
    db.session.commit()
    response_data = {"id": neuer_kontakt.id, "daten": neuer_kontakt.get_data()}
    return jsonify({"success": True, "kontakt": response_data})

# --- Import/Export-Routen (jetzt vereinfacht) ---

@app.route("/import/upload", methods=["POST"])
def upload_import_file():
    if 'file' not in request.files:
        return jsonify({"error": "Keine Datei im Request gefunden."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Keine Datei ausgewählt."}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Dateityp nicht erlaubt. Erlaubt sind: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        data = importer.import_file(file)
        if isinstance(data, dict) and "error" in data:
             return jsonify(data), 400
        
        headers = list(data[0].keys()) if data else []
        preview_data = data[:5]
        return jsonify({"headers": headers, "preview_data": preview_data, "original_data": data})

    except Exception as e:
        return jsonify({"error": f"Fehler beim Verarbeiten der Datei: {str(e)}"}), 500

@app.route("/import/finalize", methods=["POST"])
def finalize_import():
    # ... (Diese Route bleibt unverändert) ...
    data = request.get_json()
    vorlage_id = data.get('vorlage_id')
    mappings = data.get('mappings')
    original_data = data.get('original_data')

    if not vorlage_id or not mappings or not original_data:
        return jsonify({"success": False, "error": "Fehlende Daten für den Import."}), 400
    
    vorlage = Vorlage.query.get(vorlage_id)
    if not vorlage:
        return jsonify({"success": False, "error": "Vorlage nicht gefunden."}), 404

    count = 0
    for row in original_data:
        new_kontakt_data = {}
        for import_header, vorlage_prop in mappings.items():
            if vorlage_prop and import_header in row:
                new_kontakt_data[vorlage_prop] = row[import_header]
        
        if new_kontakt_data:
            kontakt = Kontakt(vorlage_id=vorlage_id)
            kontakt.set_data(new_kontakt_data)
            db.session.add(kontakt)
            count += 1
            
    db.session.commit()
    flash(f"{count} Kontakte wurden erfolgreich importiert.", "success")
    return jsonify({"success": True, "redirect_url": url_for('kontakte_auflisten')})

@app.route("/export/<int:vorlage_id>/<string:file_format>")
def export_data(vorlage_id, file_format):
    vorlage_model = Vorlage.query.options(joinedload(Vorlage.kontakte), joinedload(Vorlage.gruppen).joinedload(Gruppe.eigenschaften)).get_or_404(vorlage_id)
    
    kontakte_data = [{"id": k.id, "daten": k.get_data()} for k in vorlage_model.kontakte]
    
    vorlage_struktur = {
        "name": vorlage_model.name,
        "gruppen": [{"name": g.name, "eigenschaften": [{"name": e.name} for e in g.eigenschaften]} for g in vorlage_model.gruppen]
    }
    
    content, mimetype = exporter.export_data(file_format, kontakte_data, vorlage_struktur)
    
    if not content:
        return "Ungültiges Export-Format", 400
        
    filename = f"{vorlage_model.name}_export_{datetime.now().strftime('%Y-%m-%d')}.{file_format}"
        
    return Response(
        content,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

# --- (Restliche Routen für Vorlagen- und Kontakt-Management bleiben gleich) ---
@app.route("/vorlagen")
def vorlagen_verwalten():
    return render_template("vorlagen_verwaltung.html", vorlagen=Vorlage.query.order_by(Vorlage.name).all())

@app.route("/vorlagen/editor", methods=["GET"])
def vorlage_editor():
    vorlage_id = request.args.get('vorlage_id', type=int)
    all_vorlagen = Vorlage.query.all()
    if vorlage_id:
        vorlage = Vorlage.query.get_or_404(vorlage_id)
        vorlage_data = {"name": vorlage.name, "gruppen": [{"name": g.name, "eigenschaften": [{"name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]} for g in vorlage.gruppen]}
        action_url = url_for('vorlage_speichern', vorlage_id=vorlage.id)
    else:
        vorlage_data = {"name": "", "gruppen": [{"name": "Allgemein", "eigenschaften": []}]}
        action_url = url_for('vorlage_speichern')
    
    all_vorlagen_data = [{"id": v.id, "name": v.name} for v in all_vorlagen]
    
    return render_template("vorlage_editor.html", 
                           vorlage_data=json.dumps(vorlage_data), 
                           action_url=action_url, 
                           all_vorlagen_data=json.dumps(all_vorlagen_data))

@app.route("/vorlagen/speichern", methods=["POST"])
@app.route("/vorlagen/speichern/<int:vorlage_id>", methods=["POST"])
def vorlage_speichern(vorlage_id=None):
    data = request.get_json()
    if vorlage_id:
        vorlage = Vorlage.query.get_or_404(vorlage_id)
        vorlage.name = data['name']
        Gruppe.query.filter_by(vorlage_id=vorlage_id).delete()
        db.session.flush()
    else:
        vorlage = Vorlage(name=data['name'])
        db.session.add(vorlage)
        db.session.flush()
    for gruppe_data in data.get('gruppen', []):
        gruppe = Gruppe(name=gruppe_data['name'], vorlage_id=vorlage.id)
        db.session.add(gruppe)
        db.session.flush()
        for eigenschaft_data in gruppe_data.get('eigenschaften', []):
            eigenschaft = Eigenschaft(name=eigenschaft_data['name'], datentyp=eigenschaft_data['datentyp'], optionen=eigenschaft_data.get('optionen', ''), gruppe_id=gruppe.id)
            db.session.add(eigenschaft)
    db.session.commit()
    return jsonify({"redirect_url": url_for('vorlagen_verwalten')})

@app.route("/vorlagen/loeschen/<int:vorlage_id>", methods=["POST"])
def vorlage_loeschen(vorlage_id):
    vorlage = Vorlage.query.get_or_404(vorlage_id)
    db.session.delete(vorlage)
    db.session.commit()
    return redirect(url_for("vorlagen_verwalten"))

@app.route("/kontakte")
def kontakte_auflisten():
    vorlagen_query = Vorlage.query.options(
        joinedload(Vorlage.kontakte),
        joinedload(Vorlage.gruppen).joinedload(Gruppe.eigenschaften)
    ).order_by(Vorlage.name).all()
    
    vorlagen_data = []
    for v in vorlagen_query:
        vorlage_dict = {
            "id": v.id,
            "name": v.name,
            "eigenschaften": [
                {
                    "id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen
                } for g in v.gruppen for e in g.eigenschaften
            ],
            "kontakte": [{"id": k.id, "daten": k.get_data()} for k in v.kontakte],
            "gruppen": [
                {
                    "id": g.id, "name": g.name,
                    "eigenschaften": [{"id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]
                } for g in v.gruppen
            ]
        }
        vorlagen_data.append(vorlage_dict)

    vorlagen_json_string = json.dumps(vorlagen_data)
    return render_template("kontakte_liste.html", vorlagen_for_json=vorlagen_json_string)

@app.route("/kontakte/editor", methods=["GET", "POST"])
def kontakt_editor():
    kontakt_id = request.args.get('kontakt_id', type=int)
    vorlage_id = request.args.get('vorlage_id', type=int)
    
    if kontakt_id:
        kontakt = Kontakt.query.get_or_404(kontakt_id)
        vorlage = kontakt.vorlage
        action_url = url_for('kontakt_editor', kontakt_id=kontakt.id)
    elif vorlage_id:
        kontakt = None
        vorlage = Vorlage.query.get_or_404(vorlage_id)
        action_url = url_for('kontakt_editor', vorlage_id=vorlage.id)
    else:
        return redirect(url_for('vorlagen_verwalten'))

    if request.method == "POST":
        form_daten = request.form.to_dict()
        if kontakt:
            kontakt.set_data(form_daten)
        else:
            neuer_kontakt = Kontakt(vorlage_id=vorlage.id)
            neuer_kontakt.set_data(form_daten)
            db.session.add(neuer_kontakt)
        db.session.commit()
        return redirect(url_for('kontakte_auflisten'))
        
    vorlage_for_json = {
        "id": vorlage.id, "name": vorlage.name,
        "gruppen": [{"id": g.id, "name": g.name, "eigenschaften": [{"id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]} for g in vorlage.gruppen]
    }
    kontakt_daten_for_json = kontakt.get_data() if kontakt else {}
    
    return render_template("kontakt_editor.html", 
                           action_url=action_url,
                           kontakt=kontakt,
                           vorlage_for_json=json.dumps(vorlage_for_json), 
                           kontakt_daten_for_json=json.dumps(kontakt_daten_for_json))

@app.route("/kontakte/loeschen/<int:kontakt_id>", methods=["POST"])
def kontakt_loeschen(kontakt_id):
    kontakt = Kontakt.query.get_or_404(kontakt_id)
    db.session.delete(kontakt)
    db.session.commit()
    return redirect(url_for("kontakte_auflisten"))
    
@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    create_database()
    app.run(port=6060, debug=True)