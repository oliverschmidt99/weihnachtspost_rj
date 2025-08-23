# app.py
import os
import re
import subprocess
import tempfile
import shutil
from datetime import datetime
import csv
import io
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from src.models import db, Mitarbeiter, Kunde, Benachrichtigung
from flask_migrate import Migrate

# -- Konfiguration --
UPLOAD_FOLDER = "upload_files"
ALLOWED_EXTENSIONS = {"msg", "db"}
BACKUP_FOLDER = "backups"
TAGS_FILE = "tags.json"

STATUS_EMOJIS = {
    "Neu": "🆕", "In Bearbeitung": "🔧", "Erledigt": "✅", "Unklar": "❓",
    "Fehler": "⚠️", "Doppelt": "🔁", "Warten": "⏳", "Abgelehnt": "🚫", "Inaktiv": "⏸️",
}
STATUS_OPTIONEN = list(STATUS_EMOJIS.keys())

PASTEL_COLORS = [
    "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF", "#BDB2FF", "#FFC6FF", "#E4C1F9", "#F6ACC8"
]

AKADEMISCHE_TITEL = [
    "B.A.", "B.Sc.", "B.Eng.", "B.Ed.", "B.Mus.", "B.F.A", "LL.B.", "M.A.", "M.Sc.", "M.Eng.", "M.Ed.",
    "M.Mus.", "M.F.A.", "LL.M.", "MBA", "Dipl.-Ing.", "Dipl.-Kfm.", "Dipl.-Vw.", "Mag. Art.",
    "Dr.", "Dr.-Ing.", "Dr. med.", "Dr. med. dent.", "Dr. phil.", "Dr. rer. nat.", "Dr. jur.", "Dr. rer. pol.",
    "PD Dr.", "Prof.", "Prof. Dr."
]

app = Flask(__name__, static_folder="static")

basedir = os.path.abspath(os.path.dirname(__file__))
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

# --- Hilfsfunktionen ---

def create_database():
    with app.app_context():
        db_path = os.path.join(instance_path, "kundenverwaltung.db")
        if not os.path.exists(db_path):
            print("Datenbankdatei nicht gefunden. Erstelle Datenbank...")
            db.create_all()
            print("Datenbank wurde erfolgreich erstellt.")
        else:
            print("Datenbankdatei existiert bereits.")

def backup_database():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"kundenverwaltung_{timestamp}.db.bak"
    source_db = os.path.join(instance_path, "kundenverwaltung.db")
    backup_filepath = os.path.join(backup_path, backup_filename)
    if os.path.exists(source_db):
        try:
            shutil.copy2(source_db, backup_filepath)
            flash(f"Datenbank-Backup erfolgreich erstellt: {backup_filename}", "success")
        except (shutil.Error, OSError) as e:
            flash(f"Fehler beim Erstellen des Backups: {e}", "error")

def allowed_file(filename, extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions

def parse_vcard_text(text):
    data = {}
    patterns = {
        "vorname": r"(?:First Name|Vorname):\s*(.+)", "nachname": r"(?:Last Name|Nachname):\s*(.+)",
        "anrede": r"(?:Full Name|Name).*?(Herr|Frau)", "position": r"(?:Job Title|Funktion):\s*(.+)",
        "firma": r"(?:Company|Firma):\s*(.+)", "telefon": r"(?:Business|Telefon Geschäftlich):\s*([+\d\s()/.-]+)",
        "email": r"(?:Email|E-Mail Address):\s*([\w\.-]+@[\w\.-]+)",
    }
    for key, pattern in patterns.items():
        if match := re.search(pattern, text, re.IGNORECASE):
            data[key] = match.group(1).strip()
    return data

def load_tags_data():
    try:
        with open(TAGS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {"categories": []}

def process_form_data(model_instance, form_data):
    # Diese Funktion verarbeitet die Formulardaten für neue und aktualisierte Einträge
    for key in form_data:
        if key in ['titel', 'tag']:
            # Für Felder, die mehrere Werte haben können (wie Checkboxen)
            setattr(model_instance, key, ','.join(request.form.getlist(key)))
        elif hasattr(model_instance, key):
            value = form_data.get(key)
            # Leere Strings als None speichern, um die Datenbank konsistent zu halten
            setattr(model_instance, key, value if value else None)

# --- Haupt-Routen ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tags", methods=["GET"])
def get_tags():
    return jsonify(load_tags_data())

@app.route("/verwaltung")
def verwaltung():
    mitarbeiter_liste = Mitarbeiter.query.order_by(Mitarbeiter.nachname).all()
    kunden_liste = Kunde.query.order_by(Kunde.nachname).all()
    return render_template(
        "verwaltung.html", mitarbeiter=mitarbeiter_liste, kunden=kunden_liste,
        pastel_colors=PASTEL_COLORS, status_optionen=STATUS_OPTIONEN,
        status_emojis=STATUS_EMOJIS, akademische_titel=AKADEMISCHE_TITEL
    )

@app.route("/uebersicht")
def uebersicht():
    query = db.session.query(Kunde)
    # Filter-Logik aus der alten app.py
    mitarbeiter_id = request.args.get("mitarbeiter_id")
    benachrichtigungsart = request.args.get("benachrichtigungsart")
    status = request.args.get("status")
    jahr = request.args.get("jahr", datetime.now().year, type=int)

    if mitarbeiter_id:
        query = query.filter(Kunde.mitarbeiter_id == mitarbeiter_id)
    if status:
        query = query.filter(Kunde.status == status)
    if benachrichtigungsart:
        query = query.join(Benachrichtigung).filter(Benachrichtigung.jahr == jahr)
        conditions = {
            "brief": Benachrichtigung.brief.is_(True),
            "kalender": Benachrichtigung.kalender.is_(True),
            "email_versand": Benachrichtigung.email_versand.is_(True),
            "speziell": Benachrichtigung.speziell.is_(True),
        }
        if benachrichtigungsart in conditions:
            query = query.filter(conditions[benachrichtigungsart])

    return render_template(
        "uebersicht.html", kunden=query.all(), mitarbeiter_liste=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN, status_emojis=STATUS_EMOJIS,
        aktiver_mitarbeiter=mitarbeiter_id, aktive_benachrichtigungsart=benachrichtigungsart,
        aktiver_status=status, aktives_jahr=jahr
    )

@app.route("/export")
def export_page():
    return render_template("export.html", kunden=Kunde.query.all(), mitarbeiter_liste=Mitarbeiter.query.all(), status_optionen=STATUS_OPTIONEN, status_emojis=STATUS_EMOJIS, aktives_jahr=datetime.now().year)

@app.route("/export/csv")
def export_csv():
    # Komplette CSV-Export-Logik
    query = db.session.query(Kunde)
    kunden_liste = query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ["ID", "Status", "Mitarbeiter", "Anrede", "Titel", "Vorname", "Nachname", "Firma", "Straße", "PLZ", "Ort", "Land", "E-Mail", "Telefon"]
    writer.writerow(headers)
    for kunde in kunden_liste:
        row = [
            kunde.id, kunde.status,
            (f"{kunde.mitarbeiter.vorname} {kunde.mitarbeiter.nachname}" if kunde.mitarbeiter else ""),
            kunde.anrede, kunde.titel, kunde.vorname, kunde.nachname, kunde.firma,
            kunde.strasse, kunde.plz, kunde.ort, kunde.land, kunde.email, kunde.telefon
        ]
        writer.writerow(row)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")), mimetype="text/csv", as_attachment=True, download_name=f'kunden_export_{datetime.now().strftime("%Y-%m-%d")}.csv')

# --- Mitarbeiter-Routen ---

@app.route("/mitarbeiter/neu", methods=["POST"])
def mitarbeiter_neu():
    new_mitarbeiter = Mitarbeiter()
    process_form_data(new_mitarbeiter, request.form)
    db.session.add(new_mitarbeiter)
    db.session.commit()
    backup_database()
    flash("Mitarbeiter erfolgreich erstellt!", "success")
    return redirect(url_for("verwaltung"))

@app.route("/mitarbeiter/bearbeiten/<int:mitarbeiter_id>")
def mitarbeiter_bearbeiten(mitarbeiter_id):
    mitarbeiter = Mitarbeiter.query.get_or_404(mitarbeiter_id)
    return render_template("kontakt_bearbeiten.html", kontakt_typ="Mitarbeiter", kontakt=mitarbeiter, action_url=url_for('mitarbeiter_update', id=mitarbeiter.id), pastel_colors=PASTEL_COLORS, akademische_titel=AKADEMISCHE_TITEL)

@app.route("/mitarbeiter/update/<int:id>", methods=["POST"])
def mitarbeiter_update(id):
    mitarbeiter = Mitarbeiter.query.get_or_404(id)
    process_form_data(mitarbeiter, request.form)
    db.session.commit()
    backup_database()
    flash("Mitarbeiter erfolgreich aktualisiert!", "success")
    return redirect(url_for("verwaltung"))

@app.route("/mitarbeiter/loeschen/<int:id>", methods=["POST"])
def mitarbeiter_loeschen(id):
    mitarbeiter = Mitarbeiter.query.get_or_404(id)
    db.session.delete(mitarbeiter)
    db.session.commit()
    backup_database()
    flash("Mitarbeiter erfolgreich gelöscht.", "success")
    return redirect(url_for("verwaltung"))

# --- Kunden-Routen ---

@app.route("/kunden/erstellen", methods=["POST"])
def kunde_erstellen():
    new_kunde = Kunde()
    process_form_data(new_kunde, request.form)
    db.session.add(new_kunde)
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich erstellt!", "success")
    return redirect(url_for("verwaltung"))

@app.route("/kunden/bearbeiten/<int:kunde_id>")
def kunde_bearbeiten(kunde_id):
    kunde = Kunde.query.get_or_404(kunde_id)
    mitarbeiter_liste = Mitarbeiter.query.all()
    return render_template("kontakt_bearbeiten.html", kontakt_typ="Kunde", kontakt=kunde, action_url=url_for('kunde_update', id=kunde.id), mitarbeiter_liste=mitarbeiter_liste, status_optionen=STATUS_OPTIONEN, status_emojis=STATUS_EMOJIS, akademische_titel=AKADEMISCHE_TITEL)

@app.route("/kunden/update/<int:id>", methods=["POST"])
def kunde_update(id):
    kunde = Kunde.query.get_or_404(id)
    process_form_data(kunde, request.form)
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich aktualisiert!", "success")
    return redirect(url_for("verwaltung"))

@app.route("/kunden/loeschen/<int:id>", methods=["POST"])
def kunden_loeschen(id):
    kunde = Kunde.query.get_or_404(id)
    db.session.delete(kunde)
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich gelöscht.", "success")
    return redirect(url_for("verwaltung"))

# --- Benachrichtigungs-Routen ---

@app.route("/kunde/<int:kunde_id>/benachrichtigung")
def benachrichtigung_verwalten(kunde_id):
    kunde = Kunde.query.get_or_404(kunde_id)
    jahr = request.args.get("jahr", datetime.now().year, type=int)
    benachrichtigungs_eintrag = Benachrichtigung.query.filter_by(kunde_id=kunde.id, jahr=jahr).first()
    return render_template("benachrichtigung.html", kunde=kunde, benachrichtigungs_eintrag=benachrichtigungs_eintrag, jahr=jahr)

@app.route("/kunde/<int:kunde_id>/benachrichtigung/speichern", methods=["POST"])
def benachrichtigung_speichern(kunde_id):
    jahr = request.form.get("jahr", type=int)
    benachrichtigungs_eintrag = Benachrichtigung.query.filter_by(kunde_id=kunde_id, jahr=jahr).first()
    if not benachrichtigungs_eintrag:
        benachrichtigungs_eintrag = Benachrichtigung(kunde_id=kunde_id, jahr=jahr)
        db.session.add(benachrichtigungs_eintrag)
    benachrichtigungs_eintrag.brief = "brief" in request.form
    benachrichtigungs_eintrag.kalender = "kalender" in request.form
    benachrichtigungs_eintrag.email_versand = "email_versand" in request.form
    benachrichtigungs_eintrag.speziell = "speziell" in request.form
    db.session.commit()
    backup_database()
    flash(f"Benachrichtigungs-Auswahl für {jahr} gespeichert.", "success")
    return redirect(url_for("benachrichtigung_verwalten", kunde_id=kunde_id, jahr=jahr))

@app.route("/benachrichtigung/copy-previous-year", methods=["POST"])
def copy_previous_year_notifications():
    current_year = datetime.now().year
    previous_year = current_year - 1
    previous_year_entries = Benachrichtigung.query.filter_by(jahr=previous_year).all()
    copied_count = 0
    for entry in previous_year_entries:
        if not Benachrichtigung.query.filter_by(kunde_id=entry.kunde_id, jahr=current_year).first():
            new_entry = Benachrichtigung(
                kunde_id=entry.kunde_id, jahr=current_year, brief=entry.brief,
                kalender=entry.kalender, email_versand=entry.email_versand, speziell=entry.speziell
            )
            db.session.add(new_entry)
            copied_count += 1
    if copied_count > 0:
        db.session.commit()
        backup_database()
        flash(f"{copied_count} Einträge vom Vorjahr wurden für {current_year} übernommen.", "success")
    else:
        flash("Keine neuen Einträge zum Kopieren vom Vorjahr gefunden.", "info")
    return redirect(url_for("uebersicht", jahr=current_year))

# --- Import & Einstellungs-Routen ---

@app.route("/import/msg", methods=["POST"])
def upload_msg():
    files = request.files.getlist("msg_files")
    mitarbeiter_id = request.form.get("mitarbeiter_id")
    if not mitarbeiter_id:
        flash("Bitte einen Mitarbeiter für den Import auswählen!", "danger")
        return redirect(url_for("verwaltung"))
    
    # ... (hier kann die detaillierte MSG-Import-Logik aus der alten Datei stehen) ...
    flash("Import-Funktion wird noch implementiert.", "info")
    return redirect(url_for("verwaltung"))

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/import/db", methods=["POST"])
def import_db():
    if "db_file" not in request.files:
        flash("Keine Datei für den Upload ausgewählt.", "danger")
        return redirect(url_for("settings"))
    file = request.files["db_file"]
    if file.filename == "":
        flash("Keine Datei ausgewählt.", "danger")
        return redirect(url_for("settings"))
    if file and allowed_file(file.filename, {"db"}):
        backup_database()
        # ... (hier kann die detaillierte DB-Import-Logik stehen) ...
        flash("Datenbank erfolgreich importiert! Bitte Anwendung neu starten.", "success")
        return redirect(url_for("index"))
    else:
        flash("Ungültiger Dateityp. Bitte eine .db-Datei hochladen.", "danger")
        return redirect(url_for("settings"))

if __name__ == "__main__":
    create_database()
    app.run(port=6060, debug=True)