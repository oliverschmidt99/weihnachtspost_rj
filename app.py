# app.py
import os
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Mitarbeiter, Kunde, Weihnachtspost
from extract_msg import Message

# -- Konfiguration --
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"msg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "eine-zufaellige-geheime-zeichenkette"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weihnachtspost.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db.init_app(app)


# -- Hilfsfunktionen --
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_email_body(body):
    data = {}
    patterns = {
        "nachname": r"(?:Nachname|Name):\s*(.+)",
        "vorname": r"Vorname:\s*(.+)",
        "firma1": r"(?:Firma|Unternehmen):\s*(.+)",
        "strasse": r"(?:Straße|Strasse):\s*(.+)",
        "postleitzahl": r"PLZ:\s*(\d+)",
        "ort": r"Ort:\s*(.+)",
        "email": r"E-Mail:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        "telefon_beruflich": r"Telefon:\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()
    if "nachname" in data and "vorname" not in data and " " in data["nachname"]:
        parts = data["nachname"].split(" ", 1)
        data["vorname"], data["nachname"] = parts[0], parts[1]
    return data


# -- Haupt-Routen --
@app.route("/")
def index():
    return render_template("index.html")


# -- Mitarbeiter-Routen (unverändert) --
@app.route("/mitarbeiter")
def mitarbeiter_liste():
    return render_template("mitarbeiter.html", mitarbeiter=Mitarbeiter.query.all())


@app.route("/mitarbeiter/neu", methods=["POST"])
def mitarbeiter_neu():
    neuer_mitarbeiter = Mitarbeiter(
        anrede=request.form["anrede"],
        vorname=request.form["vorname"],
        nachname=request.form["nachname"],
        abteilung=request.form["abteilung"],
        position=request.form["position"],
        telefon=request.form["telefon"],
    )
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
    mitarbeiter.anrede, mitarbeiter.vorname, mitarbeiter.nachname = (
        request.form["anrede"],
        request.form["vorname"],
        request.form["nachname"],
    )
    mitarbeiter.abteilung, mitarbeiter.position, mitarbeiter.telefon = (
        request.form["abteilung"],
        request.form["position"],
        request.form["telefon"],
    )
    db.session.commit()
    flash("Mitarbeiter erfolgreich aktualisiert!", "success")
    return redirect(url_for("mitarbeiter_liste"))


@app.route("/mitarbeiter/loeschen/<int:id>", methods=["POST"])
def mitarbeiter_loeschen(id):
    db.session.delete(Mitarbeiter.query.get_or_404(id))
    db.session.commit()
    flash("Mitarbeiter und zugehörige Kunden gelöscht!", "success")
    return redirect(url_for("mitarbeiter_liste"))


# -- Kunden-Routen (unverändert) --
@app.route("/kunden")
def kunden_liste():
    return render_template(
        "kunden.html", kunden=Kunde.query.all(), mitarbeiter=Mitarbeiter.query.all()
    )


@app.route("/kunden/neu", methods=["GET"])
def kunde_neu_form():
    return render_template(
        "kunde_neu.html", mitarbeiter=Mitarbeiter.query.all(), jahr=datetime.now().year
    )


@app.route("/kunden/erstellen", methods=["POST"])
def kunde_erstellen():
    neuer_kunde = Kunde()
    for key, value in request.form.items():
        if key not in ["postkarte", "kalender", "email_versand", "speziell"]:
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
    flash("Kunde und Weihnachtspost-Auswahl erfolgreich erstellt!", "success")
    return redirect(url_for("kunden_liste"))


@app.route("/kunden/bearbeiten/<int:id>")
def kunde_bearbeiten(id):
    return render_template(
        "kunde_bearbeiten.html",
        kunde=Kunde.query.get_or_404(id),
        mitarbeiter=Mitarbeiter.query.all(),
    )


@app.route("/kunden/update/<int:id>", methods=["POST"])
def kunde_update(id):
    kunde = Kunde.query.get_or_404(id)
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


# -- Weihnachtspost-Routen (unverändert) --
@app.route("/kunde/<int:kunde_id>/weihnachtspost", methods=["GET"])
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


# -- MSG-Import Route (AKTUALISIERT mit HTML-Verarbeitung) --
@app.route("/import/msg", methods=["POST"])
def upload_msg():
    files = request.files.getlist("msg_files")
    mitarbeiter_id = request.form.get("mitarbeiter_id")
    if not mitarbeiter_id:
        flash("Bitte einen Mitarbeiter für den Import auswählen!", "danger")
        return redirect(url_for("kunden_liste"))

    erfolgreich, aktualisiert, fehler = 0, 0, 0
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            try:
                with Message(filepath) as msg:
                    # NEU: HTML-Body bevorzugen und bereinigen
                    body_content = ""
                    if msg.htmlBody:
                        # Entferne HTML-Tags, um reinen Text zu erhalten
                        cleaner = re.compile("<.*?>")
                        body_content = re.sub(cleaner, "", msg.htmlBody.decode())
                    else:
                        body_content = msg.body

                    # --- DEBUG-AUSGABE ---
                    print("=" * 50)
                    print(f"VERARBEITE DATEI: {filename}")
                    print("-" * 50)
                    print("BEREINIGTER INHALT ZUR ANALYSE:")
                    print(body_content)
                    print("-" * 50)

                    data = parse_email_body(body_content)

                    print("EXTRRAHIERTE FELDER:")
                    print(data)
                    print("=" * 50)
                    # --- DEBUG-AUSGABE ENDE ---

                    email = data.get("email") or (
                        msg.sender if msg.sender and "@" in msg.sender else None
                    )
                    kunde = (
                        Kunde.query.filter_by(email=email).first() if email else None
                    )
                    if kunde:
                        for key, val in data.items():
                            if not getattr(kunde, key, None):
                                setattr(kunde, key, val)
                        kunde.anmerkungen += (
                            f"\n\n--- UPDATE aus '{filename}' ---\n{body_content}"
                        )
                        aktualisiert += 1
                    else:
                        nachname = data.get("nachname") or (
                            email.split("@")[0] if email else "Unbekannt"
                        )
                        neuer_kunde = Kunde(
                            nachname=nachname,
                            vorname=data.get("vorname", ""),
                            email=email,
                            firma1=data.get("firma1"),
                            strasse=data.get("strasse"),
                            postleitzahl=data.get("postleitzahl"),
                            ort=data.get("ort"),
                            telefon_beruflich=data.get("telefon_beruflich"),
                            anmerkungen=f"Importiert aus '{filename}'\n\n---\n\n{body_content}",
                            mitarbeiter_id=mitarbeiter_id,
                        )
                        db.session.add(neuer_kunde)
                        erfolgreich += 1
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"FEHLER bei {filename}: {e}")
                fehler += 1
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
    flash(
        f"{erfolgreich} neu importiert, {aktualisiert} aktualisiert, {fehler} Fehler.",
        "info",
    )
    return redirect(url_for("kunden_liste"))


# -- Hauptausführung --
if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
