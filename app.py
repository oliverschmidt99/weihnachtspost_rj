# app.py
import os
import re
import subprocess
import tempfile
import shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Mitarbeiter, Kunde, Weihnachtspost
from sqlalchemy import or_

# -- Konfiguration --
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"msg"}
STATUS_OPTIONEN = ["Neu", "In Ordnung", "Unklar", "Fehler", "Doppelt"]
STATUS_EMOJIS = {
    "Neu": "🆕",
    "In Ordnung": "✅",
    "Unklar": "❓",
    "Fehler": "❌",
    "Doppelt": "🔃",
}

app = Flask(__name__)
app.config["SECRET_KEY"] = "dein-super-geheimer-schluessel-hier"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weihnachtspost.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db.init_app(app)


# (Der Großteil der Datei bleibt unverändert)
# ...
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_vcard_text(text):
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
    return render_template("index.html")


@app.route("/uebersicht")
def uebersicht():
    query = db.session.query(Kunde)
    mitarbeiter_id = request.args.get("mitarbeiter_id")
    post_art = request.args.get("post_art")
    status = request.args.get("status")
    jahr = request.args.get("jahr", datetime.now().year, type=int)

    if mitarbeiter_id:
        query = query.filter(Kunde.mitarbeiter_id == mitarbeiter_id)
    if status:
        query = query.filter(Kunde.status == status)
    if post_art:
        query = query.join(Weihnachtspost).filter(Weihnachtspost.jahr == jahr)
        if post_art == "postkarte":
            query = query.filter(Weihnachtspost.postkarte == True)
        elif post_art == "kalender":
            query = query.filter(Weihnachtspost.kalender == True)
        elif post_art == "email_versand":
            query = query.filter(Weihnachtspost.email_versand == True)
        elif post_art == "speziell":
            query = query.filter(Weihnachtspost.speziell == True)

    return render_template(
        "uebersicht.html",
        kunden=query.all(),
        mitarbeiter_liste=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
        status_emojis=STATUS_EMOJIS,
        aktiver_mitarbeiter=mitarbeiter_id,
        aktive_post_art=post_art,
        aktiver_status=status,
        aktives_jahr=jahr,
    )


@app.route("/mitarbeiter")
def mitarbeiter_liste():
    return render_template("mitarbeiter.html", mitarbeiter=Mitarbeiter.query.all())


@app.route("/mitarbeiter/neu", methods=["POST"])
def mitarbeiter_neu():
    neuer_mitarbeiter = Mitarbeiter(**request.form)
    db.session.add(neuer_mitarbeiter)
    db.session.commit()
    flash("Mitarbeiter erfolgreich hinzugefügt!", "success")
    return redirect(url_for("mitarbeiter_liste"))


@app.route("/mitarbeiter/bearbeiten/<int:id>")
def mitarbeiter_bearbeiten(id):
    return render_template(
        "mitarbeiter_bearbeiten.html", mitarbeiter=Mitarbeiter.query.get_or_404(id)
    )


@app.route("/mitarbeiter/update/<int:id>", methods=["POST"])
def mitarbeiter_update(id):
    mitarbeiter = Mitarbeiter.query.get_or_404(id)
    for key, value in request.form.items():
        setattr(mitarbeiter, key, value)
    db.session.commit()
    flash("Mitarbeiter erfolgreich aktualisiert!", "success")
    return redirect(url_for("mitarbeiter_liste"))


@app.route("/mitarbeiter/loeschen/<int:id>", methods=["POST"])
def mitarbeiter_loeschen(id):
    mitarbeiter = Mitarbeiter.query.get_or_404(id)
    db.session.delete(mitarbeiter)
    db.session.commit()
    flash(
        "Mitarbeiter gelöscht. Kunden wurden keinem Mitarbeiter mehr zugeordnet.",
        "success",
    )
    return redirect(url_for("mitarbeiter_liste"))


@app.route("/kunden")
def kunden_liste():
    return render_template(
        "kunden.html",
        kunden=Kunde.query.all(),
        mitarbeiter=Mitarbeiter.query.all(),
        status_emojis=STATUS_EMOJIS,
    )


@app.route("/kunden/neu", methods=["GET"])
def kunde_neu_form():
    return render_template(
        "kunde_neu.html",
        mitarbeiter=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
        jahr=datetime.now().year,
    )


@app.route("/kunden/erstellen", methods=["POST"])
def kunde_erstellen():
    neuer_kunde = Kunde()
    for key, value in request.form.items():
        if hasattr(Kunde, key):
            setattr(neuer_kunde, key, value)
    db.session.add(neuer_kunde)
    db.session.flush()
    post_eintrag = Weihnachtspost(
        kunde_id=neuer_kunde.id,
        jahr=datetime.now().year,
        postkarte="postkarte" in request.form,
        kalender="kalender" in request.form,
        email_versand="email_versand" in request.form,
        speziell="speziell" in request.form,
    )
    db.session.add(post_eintrag)
    db.session.commit()
    flash("Kunde erfolgreich erstellt!", "success")
    return redirect(url_for("kunden_liste"))


@app.route("/kunden/bearbeiten/<int:id>")
def kunde_bearbeiten(id):
    return render_template(
        "kunde_bearbeiten.html",
        kunde=Kunde.query.get_or_404(id),
        mitarbeiter=Mitarbeiter.query.all(),
        status_optionen=STATUS_OPTIONEN,
    )


@app.route("/kunden/update/<int:id>", methods=["POST"])
def kunde_update(id):
    kunde = Kunde.query.get_or_404(id)
    if "mitarbeiter_id" in request.form and not request.form["mitarbeiter_id"]:
        kunde.mitarbeiter_id = None
        form_data = request.form.to_dict()
        del form_data["mitarbeiter_id"]
        for key, value in form_data.items():
            setattr(kunde, key, value)
    else:
        for key, value in request.form.items():
            setattr(kunde, key, value)
    db.session.commit()
    flash("Kunde erfolgreich aktualisiert!", "success")
    return redirect(url_for("kunden_liste"))


@app.route("/kunden/loeschen/<int:id>", methods=["POST"])
def kunde_loeschen(id):
    db.session.delete(Kunde.query.get_or_404(id))
    db.session.commit()
    flash("Kunde erfolgreich gelöscht!", "success")
    return redirect(url_for("kunden_liste"))


@app.route("/kunde/<int:kunde_id>/weihnachtspost")
def weihnachtspost_verwalten(kunde_id):
    kunde = Kunde.query.get_or_404(kunde_id)
    jahr = request.args.get("jahr", datetime.now().year, type=int)
    post_eintrag = Weihnachtspost.query.filter_by(kunde_id=kunde.id, jahr=jahr).first()
    return render_template(
        "weihnachtspost.html", kunde=kunde, post_eintrag=post_eintrag, jahr=jahr
    )


@app.route("/kunde/<int:kunde_id>/weihnachtspost/speichern", methods=["POST"])
def weihnachtspost_speichern(kunde_id):
    jahr = request.form.get("jahr", type=int)
    post_eintrag = Weihnachtspost.query.filter_by(kunde_id=kunde_id, jahr=jahr).first()
    if not post_eintrag:
        post_eintrag = Weihnachtspost(kunde_id=kunde_id, jahr=jahr)
        db.session.add(post_eintrag)
    post_eintrag.postkarte = "postkarte" in request.form
    post_eintrag.kalender = "kalender" in request.form
    post_eintrag.email_versand = "email_versand" in request.form
    post_eintrag.speziell = "speziell" in request.form
    db.session.commit()
    flash(f"Weihnachtspost-Auswahl für {jahr} gespeichert.", "success")
    return redirect(url_for("weihnachtspost_verwalten", kunde_id=kunde_id, jahr=jahr))


@app.route("/import/msg", methods=["POST"])
def upload_msg():
    files = request.files.getlist("msg_files")
    mitarbeiter_id = request.form.get("mitarbeiter_id")
    if not mitarbeiter_id:
        flash("Bitte einen Mitarbeiter für den Import auswählen!", "danger")
        return redirect(url_for("kunden_liste"))

    post_auswahl = {
        "postkarte": "postkarte" in request.form,
        "kalender": "kalender" in request.form,
        "email_versand": "email_versand" in request.form,
        "speziell": "speziell" in request.form,
    }
    erfolgreich, aktualisiert, fehler = 0, 0, 0
    temp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            if not (file and allowed_file(file.filename)):
                continue

            msg_filepath = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(msg_filepath)
            subprocess.run(
                ["python", "-m", "extract_msg", "--out", temp_dir, msg_filepath],
                capture_output=True,
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
            email = data.get("email")
            kunde = Kunde.query.filter_by(email=email).first() if email else None

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
                post_eintrag = Weihnachtspost(
                    kunde_id=neuer_kunde.id, jahr=datetime.now().year, **post_auswahl
                )
                db.session.add(post_eintrag)
                erfolgreich += 1

            os.remove(message_txt_path)
        db.session.commit()
    except Exception as e:
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
    return redirect(url_for("kunden_liste"))


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    with app.app_context():
        db.create_all()
    # KORREKTUR: Port auf 6060 geändert
    app.run(host="0.0.0.0", port=6060, debug=True)
