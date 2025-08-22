# src/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Mitarbeiter(db.Model):
    """
    Stellt einen Mitarbeiter in der Datenbank dar.
    Enthält jetzt erweiterte Kontakt- und Firmendaten.
    """

    id = db.Column(db.Integer, primary_key=True)
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)

    # Bestehende Felder
    telefon = db.Column(db.String(50))
    farbe = db.Column(db.String(7), default="#FFFFFF")

    # --- NEUE FELDER ---
    firmenname = db.Column(db.String(150))
    position = db.Column(db.String(100))
    abteilung = db.Column(db.String(100))
    email = db.Column(db.String(120))
    durchwahl = db.Column(db.String(50))

    # Firmenadresse
    firma_strasse = db.Column(db.String(200))
    firma_plz = db.Column(db.String(20))
    firma_ort = db.Column(db.String(100))

    # Beziehung zu den Kunden
    kunden = db.relationship("Kunde", backref="mitarbeiter", lazy=True)

    def __repr__(self):
        return f"<Mitarbeiter {self.vorname} {self.nachname}>"


class Kunde(db.Model):
    """
    Stellt einen Kunden in der Datenbank dar.
    Enthält alle Kontakt- und Adressinformationen.
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
    status = db.Column(db.String(20), nullable=False, default="Neu")
    mitarbeiter_id = db.Column(
        db.Integer, db.ForeignKey("mitarbeiter.id", ondelete="SET NULL"), nullable=True
    )
    weihnachtspost = db.relationship(
        "Weihnachtspost", backref="kunde", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Kunde {self.vorname} {self.nachname}>"


class Weihnachtspost(db.Model):
    """
    Speichert die Auswahl der Postart für einen bestimmten Kunden in einem bestimmten Jahr.
    """

    id = db.Column(db.Integer, primary_key=True)
    jahr = db.Column(db.Integer, nullable=False)
    postkarte = db.Column(db.Boolean, default=False)
    kalender = db.Column(db.Boolean, default=False)
    email_versand = db.Column(db.Boolean, default=False)
    speziell = db.Column(db.Boolean, default=False)
    kunde_id = db.Column(db.Integer, db.ForeignKey("kunde.id"), nullable=False)

    def __repr__(self):
        return f"<Weihnachtspost {self.kunde.nachname} ({self.jahr})>"
