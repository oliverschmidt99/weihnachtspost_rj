# app.py
import os
import re
import subprocess
import tempfile
import shutil
from datetime import datetime
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from src.models import db, Mitarbeiter, Kunde, Benachrichtigung

# Import für Datenbank-Migrationen
from flask_migrate import Migrate

# -- Konfiguration --
UPLOAD_FOLDER = "upload_files"
ALLOWED_EXTENSIONS = {"msg", "db"}
BACKUP_FOLDER = "backups"

STATUS_EMOJIS = {
    "Neu": "🆕",
    "In Bearbeitung": "🔧",
    "Erledigt": "✅",
    "Unklar": "❓",
    "Fehler": "⚠️",
    "Doppelt": "🔁",
    "Warten": "⏳",
    "Abgelehnt": "🚫",
    "Inaktiv": "⏸️",
}
STATUS_OPTIONEN = list(STATUS_EMOJIS.keys())

PASTEL_COLORS = [
    "#FFADAD",
    "#FFD6A5",
    "#FDFFB6",
    "#CAFFBF",
    "#9BF6FF",
    "#A0C4FF",
    "#BDB2FF",
    "#FFC6FF",
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
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(instance_path, 'kundenverwaltung.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = upload_path
db.init_app(app)

# Flask-Migrate initialisieren
migrate = Migrate(app, db)


def create_database():
    """Erstellt die Datenbank, falls sie noch nicht existiert."""
    with app.app_context():
        db_path = os.path.join(instance_path, "kundenverwaltung.db")
        if not os.path.exists(db_path):
            print("Datenbankdatei nicht gefunden. Erstelle Datenbank...")
            db.create_all()
            print("Datenbank wurde erfolgreich erstellt.")
        else:
            print("Datenbankdatei existiert bereits.")


def backup_database():
    """Erstellt ein Backup der aktuellen Datenbank."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"kundenverwaltung_{timestamp}.db.bak"
    source_db = os.path.join(instance_path, "kundenverwaltung.db")
    backup_filepath = os.path.join(backup_path, backup_filename)
    if os.path.exists(source_db):
        try:
            shutil.copy2(source_db, backup_filepath)
            flash(
                f"Datenbank-Backup erfolgreich erstellt: {backup_filename}", "success"
            )
        except (shutil.Error, OSError) as e:
            flash(f"Fehler beim Erstellen des Backups: {e}", "error")


def allowed_file(filename, extensions):
    """Überprüft, ob die Dateiendung erlaubt ist."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions


def parse_vcard_text(text):
    """Extrahiert Kontaktdaten aus Text."""
    data = {}
    patterns = {
        "vorname": r"(?:First Name|Vorname):\s*(.+)",
        "nachname": r"(?:Last Name|Nachname):\s*(.+)",
        "anrede": r"(?:Full Name|Name).*?(Herr|Frau)",
        "funktion": r"(?:Job Title|Funktion):\s*(.+)",
        "firma1": r"(?:Company|Firma):\s*(.+)",
        "telefon_beruflich": r"(?:Business|Telefon Geschäftlich):\s*([+\d\s()/.-]+)",
        "telefon_privat": r"(?:Home|Telefon Privat):\s*([+\d\s()/.-]+)",
        "mobil_telefon": r"(?:Mobile|Mobiltelefon):\s*([+\d\s()/.-]+)",
        "faxnummer": r"(?:Fax|Faxnummer):\s*([+\d\s()/.-]+)",
        "email": r"(?:Email|E-Mail Address):\s*([\w\.-]+@[\w\.-]+)",
    }
    for key, pattern in patterns.items():
        if match := re.search(pattern, text, re.IGNORECASE):
            data[key] = match.group(1).strip()
    if match := re.search(
        r"(?:Business Address|Geschäftsadresse):\s*(.*)", text, re.IGNORECASE
    ):
        addr = match.group(1).strip().replace("\r\n", " ")
        if addr_match := re.match(r"(.+?)\s+(\d{4,5})\s+(.+)", addr):
            data["strasse"], data["postleitzahl"], data["ort"] = (
                addr_match.group(1).strip(),
                addr_match.group(2).strip(),
                addr_match.group(3).strip(),
            )
        else:
            data["strasse"] = addr
    if match := re.search(r"Notes:\s*(.*)", text, re.DOTALL | re.IGNORECASE):
        data["anmerkungen"] = match.group(1).strip()
    return data


@app.route("/")
def index():
    """Rendert die Startseite."""
    return render_template("index.html")


@app.route("/verwaltung")
def verwaltung():
    """Rendert die Verwaltungsseite für Mitarbeiter und Kunden."""
    mitarbeiter_liste = Mitarbeiter.query.all()
    kunden_liste = Kunde.query.all()
    return render_template(
        "verwaltung.html",
        mitarbeiter=mitarbeiter_liste,
        kunden=kunden_liste,
        pastel_colors=PASTEL_COLORS,
        status_emojis=STATUS_EMOJIS,
        status_optionen=STATUS_OPTIONEN,
        jahr=datetime.now().year,
    )


@app.route("/uebersicht")
def uebersicht():
    """Rendert die Kundenübersicht mit Filteroptionen."""
    query = db.session.query(Kunde)
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
        "uebersicht.html",
        kunden=query.all(),
        mitarbeiter_liste=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
        status_emojis=STATUS_EMOJIS,
        aktiver_mitarbeiter=mitarbeiter_id,
        aktive_benachrichtigungsart=benachrichtigungsart,
        aktiver_status=status,
        aktives_jahr=jahr,
    )


@app.route("/export")
def export_page():
    """Rendert die Exportseite mit Filteroptionen."""
    query = db.session.query(Kunde)
    mitarbeiter_id = request.args.get("mitarbeiter_id")
    status = request.args.get("status")
    benachrichtigungsart = request.args.get("benachrichtigungsart")
    jahr = request.args.get("jahr", type=int, default=datetime.now().year)

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
        "export.html",
        kunden=query.all(),
        mitarbeiter_liste=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
        status_emojis=STATUS_EMOJIS,
        aktiver_mitarbeiter=mitarbeiter_id,
        aktive_benachrichtigungsart=benachrichtigungsart,
        aktiver_status=status,
        aktives_jahr=jahr,
    )


@app.route("/export/csv")
def export_csv():
    """Exportiert gefilterte Kundendaten als CSV."""
    query = db.session.query(Kunde)
    mitarbeiter_id = request.args.get("mitarbeiter_id")
    status = request.args.get("status")
    benachrichtigungsart = request.args.get("benachrichtigungsart")
    jahr = request.args.get("jahr", type=int, default=datetime.now().year)

    if mitarbeiter_id:
        query = query.filter(Kunde.mitarbeiter_id == mitarbeiter_id)
    if status:
        query = query.filter(Kunde.status == status)
    if benachrichtigungsart:
        query = query.join(Benachrichtigung).filter(Benachrichtigung.jahr == jahr)
        conditions = {
            "brief": Benachrichtigung.brief is True,
            "kalender": Benachrichtigung.kalender is True,
            "email_versand": Benachrichtigung.email_versand is True,
            "speziell": Benachrichtigung.speziell is True,
        }
        if benachrichtigungsart in conditions:
            query = query.filter(conditions[benachrichtigungsart])

    kunden_liste = query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "ID",
        "Status",
        "Mitarbeiter",
        "Anrede",
        "Titel",
        "Vorname",
        "Nachname",
        "Firma",
        "Straße",
        "PLZ",
        "Ort",
        "Land",
        "E-Mail",
        "Telefon",
    ]
    writer.writerow(headers)

    for kunde in kunden_liste:
        row = [
            kunde.id,
            kunde.status,
            (
                f"{kunde.mitarbeiter.vorname} {kunde.mitarbeiter.nachname}"
                if kunde.mitarbeiter
                else ""
            ),
            kunde.anrede,
            kunde.titel,
            kunde.vorname,
            kunde.nachname,
            kunde.firma1,
            kunde.strasse,
            kunde.postleitzahl,
            kunde.ort,
            kunde.land,
            kunde.email,
            kunde.telefon_beruflich,
        ]
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f'kunden_export_{datetime.now().strftime("%Y-%m-%d")}.csv',
    )


@app.route("/mitarbeiter/neu", methods=["POST"])
def mitarbeiter_neu():
    """Fügt einen neuen Mitarbeiter hinzu."""
    new_mitarbeiter = Mitarbeiter(**request.form)
    db.session.add(new_mitarbeiter)
    db.session.commit()
    backup_database()
    flash("Mitarbeiter erfolgreich hinzugefügt!", "success")
    return redirect(url_for("verwaltung"))


@app.route("/mitarbeiter/bearbeiten/<int:mitarbeiter_id>")
def mitarbeiter_bearbeiten(mitarbeiter_id):
    """Rendert die Seite zum Bearbeiten eines Mitarbeiters."""
    return render_template(
        "mitarbeiter_bearbeiten.html",
        mitarbeiter=Mitarbeiter.query.get_or_404(mitarbeiter_id),
        pastel_colors=PASTEL_COLORS,
    )


@app.route("/mitarbeiter/update/<int:mitarbeiter_id>", methods=["POST"])
def mitarbeiter_update(mitarbeiter_id):
    """Aktualisiert die Daten eines Mitarbeiters."""
    mitarbeiter = Mitarbeiter.query.get_or_404(mitarbeiter_id)
    for key, value in request.form.items():
        setattr(mitarbeiter, key, value)
    db.session.commit()
    backup_database()
    flash("Mitarbeiter erfolgreich aktualisiert!", "success")
    return redirect(url_for("verwaltung"))


@app.route("/mitarbeiter/loeschen/<int:mitarbeiter_id>", methods=["POST"])
def mitarbeiter_loeschen(mitarbeiter_id):
    """Löscht einen Mitarbeiter."""
    db.session.delete(Mitarbeiter.query.get_or_404(mitarbeiter_id))
    db.session.commit()
    backup_database()
    flash("Mitarbeiter gelöscht.", "success")
    return redirect(url_for("verwaltung"))


@app.route("/kunden/erstellen", methods=["POST"])
def kunde_erstellen():
    """Erstellt einen neuen Kunden."""
    new_kunde = Kunde()
    for key, value in request.form.items():
        if hasattr(Kunde, key):
            setattr(new_kunde, key, value)
    db.session.add(new_kunde)
    db.session.flush()
    benachrichtigungs_eintrag = Benachrichtigung(
        kunde_id=new_kunde.id,
        jahr=datetime.now().year,
        brief="brief" in request.form,
        kalender="kalender" in request.form,
        email_versand="email_versand" in request.form,
        speziell="speziell" in request.form,
    )
    db.session.add(benachrichtigungs_eintrag)
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich erstellt!", "success")
    return redirect(url_for("verwaltung"))


@app.route("/kunden/bearbeiten/<int:kunde_id>")
def kunde_bearbeiten(kunde_id):
    """Rendert die Seite zum Bearbeiten eines Kunden."""
    return render_template(
        "kunde_bearbeiten.html",
        kunde=Kunde.query.get_or_404(kunde_id),
        mitarbeiter=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
        status_emojis=STATUS_EMOJIS,
    )


@app.route("/kunden/update/<int:id>", methods=["POST"])
def kunde_update(kunde_id):
    """Aktualisiert die Daten eines Kunden."""
    kunde = Kunde.query.get_or_404(kunde_id)
    form_data = request.form.to_dict()
    if "mitarbeiter_id" in form_data and not form_data["mitarbeiter_id"]:
        kunde.mitarbeiter_id = None
        del form_data["mitarbeiter_id"]
    for key, value in form_data.items():
        setattr(kunde, key, value)
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich aktualisiert!", "success")
    return redirect(url_for("verwaltung"))


@app.route("/kunden/loeschen/<int:kunde_id>", methods=["POST"])
def kunde_loeschen(kunde_id):
    """Löscht einen Kunden."""
    db.session.delete(Kunde.query.get_or_404(kunde_id))
    db.session.commit()
    backup_database()
    flash("Kunde erfolgreich gelöscht!", "success")
    return redirect(url_for("verwaltung"))


@app.route("/kunde/<int:kunde_id>/benachrichtigung")
def benachrichtigung_verwalten(kunde_id):
    """Rendert die Seite zum Verwalten der Benachrichtigungen eines Kunden."""
    kunde = Kunde.query.get_or_404(kunde_id)
    jahr = request.args.get("jahr", datetime.now().year, type=int)
    benachrichtigungs_eintrag = Benachrichtigung.query.filter_by(
        kunde_id=kunde.id, jahr=jahr
    ).first()
    return render_template(
        "benachrichtigung.html",
        kunde=kunde,
        benachrichtigungs_eintrag=benachrichtigungs_eintrag,
        jahr=jahr,
    )


@app.route("/kunde/<int:kunde_id>/benachrichtigung/speichern", methods=["POST"])
def benachrichtigung_speichern(kunde_id):
    """Speichert die Benachrichtigungsauswahl eines Kunden für ein bestimmtes Jahr."""
    jahr = request.form.get("jahr", type=int)
    benachrichtigungs_eintrag = Benachrichtigung.query.filter_by(
        kunde_id=kunde_id, jahr=jahr
    ).first()
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


@app.route("/import/msg", methods=["POST"])
def upload_msg():
    """Importiert Kunden aus MSG-Dateien."""
    files = request.files.getlist("msg_files")
    mitarbeiter_id = request.form.get("mitarbeiter_id")

    if not mitarbeiter_id:
        flash("Bitte einen Mitarbeiter für den Import auswählen!", "danger")
        return redirect(url_for("verwaltung"))

    benachrichtigungs_auswahl = {
        "brief": "brief" in request.form,
        "kalender": "kalender" in request.form,
        "email_versand": "email_versand" in request.form,
        "speziell": "speziell" in request.form,
    }

    erfolgreich, aktualisiert, fehler = 0, 0, 0
    temp_dir = tempfile.mkdtemp()
    try:
        for file in files:
            if not (file and allowed_file(file.filename, {"msg"})):
                continue

            msg_filepath = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(msg_filepath)
            subprocess.run(
                ["python", "-m", "extract_msg", "--out", temp_dir, msg_filepath],
                capture_output=True,
                check=False,
            )

            message_txt_path = next(
                (
                    os.path.join(r, f)
                    for r, _, fs in os.walk(temp_dir)
                    for f in fs
                    if f.lower() == "message.txt"
                ),
                None,
            )

            if not message_txt_path:
                fehler += 1
                continue

            with open(message_txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            data = parse_vcard_text(text)
            kunde = None
            if email := data.get("email"):
                kunde = Kunde.query.filter_by(email=email).first()

            if (
                not kunde
                and (vorname := data.get("vorname"))
                and (nachname := data.get("nachname"))
            ):
                kunde = Kunde.query.filter(
                    db.func.lower(Kunde.vorname) == vorname.lower(),
                    db.func.lower(Kunde.nachname) == nachname.lower(),
                ).first()

            if kunde:
                for key, value in data.items():
                    if value and not getattr(kunde, key, None):
                        setattr(kunde, key, value)
                aktualisiert += 1
            else:
                neuer_kunde = Kunde(mitarbeiter_id=mitarbeiter_id, status="Neu")
                for key, value in data.items():
                    setattr(neuer_kunde, key, value)
                db.session.add(neuer_kunde)
                db.session.flush()

                benachrichtigungs_eintrag = Benachrichtigung(
                    kunde_id=neuer_kunde.id,
                    jahr=datetime.now().year,
                    **benachrichtigungs_auswahl,
                )
                db.session.add(benachrichtigungs_eintrag)
                erfolgreich += 1

            os.remove(message_txt_path)
            for item in os.listdir(temp_dir):
                if item.startswith(secure_filename(file.filename).rsplit(".", 1)[0]):
                    shutil.rmtree(os.path.join(temp_dir, item))

        db.session.commit()
        backup_database()

    except (subprocess.CalledProcessError, OSError) as e:
        db.session.rollback()
        print(f"Schwerwiegender Fehler beim Import: {e}")
        flash(f"Ein Fehler ist aufgetreten: {e}", "danger")
        fehler += len(files) - (erfolgreich + aktualisiert)
    finally:
        shutil.rmtree(temp_dir)

    flash(
        f"{erfolgreich} neu importiert, {aktualisiert} aktualisiert, {fehler} Fehler.",
        "info",
    )
    return redirect(url_for("verwaltung"))


@app.route("/benachrichtigung/copy-previous-year", methods=["POST"])
def copy_previous_year_notifications():
    """Kopiert Benachrichtigungseinträge aus dem Vorjahr."""
    current_year = datetime.now().year
    previous_year = current_year - 1
    previous_year_entries = Benachrichtigung.query.filter_by(jahr=previous_year).all()
    copied_count = 0

    for entry in previous_year_entries:
        if not Benachrichtigung.query.filter_by(
            kunde_id=entry.kunde_id, jahr=current_year
        ).first():
            new_entry = Benachrichtigung(
                kunde_id=entry.kunde_id,
                jahr=current_year,
                brief=entry.brief,
                kalender=entry.kalender,
                email_versand=entry.email_versand,
                speziell=entry.speziell,
            )
            db.session.add(new_entry)
            copied_count += 1

    if copied_count > 0:
        db.session.commit()
        backup_database()
        flash(
            f"{copied_count} Benachrichtigungs-Einträge vom Vorjahr wurden für "
            f"{current_year} übernommen.",
            "success",
        )
    else:
        flash(
            "Keine neuen Benachrichtigungs-Einträge zum Kopieren vom Vorjahr gefunden.",
            "info",
        )

    return redirect(url_for("uebersicht", jahr=current_year))


@app.route("/settings")
def settings():
    """Rendert die Einstellungsseite."""
    return render_template("settings.html")


@app.route("/import/db", methods=["POST"])
def import_db():
    """Importiert eine Datenbankdatei."""
    if "db_file" not in request.files:
        flash("Keine Datei für den Upload ausgewählt.", "danger")
        return redirect(url_for("settings"))

    file = request.files["db_file"]

    if file.filename == "":
        flash("Keine Datei ausgewählt.", "danger")
        return redirect(url_for("settings"))

    if file and allowed_file(file.filename, {"db"}):
        backup_database()
        filename = secure_filename(file.filename)
        upload_filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_filepath)
        current_db_path = os.path.join(instance_path, "kundenverwaltung.db")
        try:
            if os.path.exists(current_db_path):
                os.rename(current_db_path, current_db_path + ".old")
            shutil.copy2(upload_filepath, current_db_path)
            flash(
                "Datenbank erfolgreich importiert! Bitte starte die Anwendung manuell neu.",
                "success",
            )
            os.remove(upload_filepath)
            if os.path.exists(current_db_path + ".old"):
                os.remove(current_db_path + ".old")
        except OSError as e:
            flash(
                f"Ein Fehler ist beim Ersetzen der Datenbank aufgetreten: {e}", "danger"
            )
            if os.path.exists(current_db_path + ".old"):
                os.rename(current_db_path + ".old", current_db_path)
            return redirect(url_for("settings"))
        return redirect(url_for("index"))
    else:
        flash("Ungültiger Dateityp. Bitte eine .db-Datei hochladen.", "danger")
        return redirect(url_for("settings"))


if __name__ == "__main__":
    create_database()
    app.run(port=6060, debug=True)
