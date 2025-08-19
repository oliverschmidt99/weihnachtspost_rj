# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Mitarbeiter(db.Model):
    """
    Stellt einen Mitarbeiter in der Datenbank dar.
    """

    id = db.Column(db.Integer, primary_key=True)
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)
    abteilung = db.Column(db.String(100))
    position = db.Column(db.String(100))
    telefon = db.Column(db.String(50))

    # Beziehung: Ein Mitarbeiter kann viele Kunden haben.
    kunden = db.relationship(
        "Kunde", backref="mitarbeiter", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Mitarbeiter {self.vorname} {self.nachname}>"


class Kunde(db.Model):
    """
    Stellt einen Kunden in der Datenbank dar.
    Jeder Kunde ist einem Mitarbeiter zugeordnet.
    """

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(50))
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)
    strasse = db.Column(db.String(200))
    postleitzahl = db.Column(db.String(20))
    ort = db.Column(db.String(100))
    land = db.Column(db.String(100))
    anschriftswahl = db.Column(db.String(50))
    firma1 = db.Column(db.String(150))
    firma2 = db.Column(db.String(150))
    abteilung = db.Column(db.String(100))
    funktion = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    telefon_beruflich = db.Column(db.String(50))
    durchwahl_buero = db.Column(db.String(50))
    mobil_telefon = db.Column(db.String(50))
    faxnummer = db.Column(db.String(50))
    telefon_privat = db.Column(db.String(50))
    anmerkungen = db.Column(db.Text)

    mitarbeiter_id = db.Column(
        db.Integer, db.ForeignKey("mitarbeiter.id"), nullable=False
    )

    # Beziehung zur Weihnachtspost
    weihnachtspost = db.relationship(
        "Weihnachtspost", backref="kunde", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Kunde {self.vorname} {self.nachname}>"


class Weihnachtspost(db.Model):
    """
    Stellt die Auswahl der Weihnachtspost für einen Kunden in einem bestimmten Jahr dar.
    """

    id = db.Column(db.Integer, primary_key=True)
    jahr = db.Column(db.Integer, nullable=False)

    # Physische Post
    postkarte = db.Column(db.Boolean, default=False)
    kalender = db.Column(db.Boolean, default=False)

    # Digitale Post
    email_versand = db.Column(db.Boolean, default=False)

    # Spezielle Post
    speziell = db.Column(db.Boolean, default=False)

    # Fremdschlüssel zum Kunden
    kunde_id = db.Column(db.Integer, db.ForeignKey("kunde.id"), nullable=False)

    def __repr__(self):
        return f"<Weihnachtspost {self.kunde.nachname} ({self.jahr})>"
