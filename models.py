# models.py
from flask_sqlalchemy import SQLAlchemy

# Initialisiert die SQLAlchemy-Erweiterung. Dies ist das zentrale Objekt für die Datenbank.
db = SQLAlchemy()


class Mitarbeiter(db.Model):
    """
    Stellt einen Mitarbeiter in der Datenbank dar.
    Jeder Mitarbeiter hat persönliche Daten und eine ihm zugewiesene Farbe.
    """

    id = db.Column(db.Integer, primary_key=True)
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)  # Nachname ist ein Pflichtfeld
    abteilung = db.Column(db.String(100))
    position = db.Column(db.String(100))
    telefon = db.Column(db.String(50))
    # NEU: Ein Farbfeld, um Mitarbeiter in der UI visuell zu unterscheiden.
    # Der Standardwert ist Weiß (#FFFFFF).
    farbe = db.Column(db.String(7), default="#FFFFFF")

    # Beziehung zu den Kunden.
    # Wenn ein Mitarbeiter gelöscht wird, werden die Kunden NICHT mitgelöscht.
    # Ihre `mitarbeiter_id` wird stattdessen auf NULL gesetzt (siehe Kunde.mitarbeiter_id).
    kunden = db.relationship("Kunde", backref="mitarbeiter", lazy=True)

    def __repr__(self):
        # Definiert, wie ein Mitarbeiter-Objekt in der Konsole ausgegeben wird (nützlich für Debugging).
        return f"<Mitarbeiter {self.vorname} {self.nachname}>"


class Kunde(db.Model):
    """
    Stellt einen Kunden in der Datenbank dar.
    Enthält alle Kontakt- und Adressinformationen.
    """

    id = db.Column(
        db.Integer, primary_key=True
    )  # Eindeutige ID, wird automatisch vergeben
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
    email = db.Column(
        db.String(120), unique=True
    )  # E-Mail-Adressen müssen einzigartig sein
    telefon_beruflich = db.Column(db.String(50))
    durchwahl_buero = db.Column(db.String(50))
    mobil_telefon = db.Column(db.String(50))
    faxnummer = db.Column(db.String(50))
    telefon_privat = db.Column(db.String(50))
    anmerkungen = db.Column(db.Text)  # Textfeld für längere Notizen

    # Statusfeld zur Nachverfolgung der Datenqualität. Standardwert ist 'Neu'.
    status = db.Column(db.String(20), nullable=False, default="Neu")

    # Fremdschlüssel, der den Kunden mit einem Mitarbeiter verknüpft.
    # `ondelete='SET NULL'` sorgt dafür, dass dieses Feld leer wird, wenn der zugehörige Mitarbeiter gelöscht wird.
    mitarbeiter_id = db.Column(
        db.Integer, db.ForeignKey("mitarbeiter.id", ondelete="SET NULL"), nullable=True
    )

    # Beziehung zur Weihnachtspost-Tabelle.
    # `cascade="all, delete-orphan"` bedeutet: Wenn ein Kunde gelöscht wird, werden alle seine Weihnachtspost-Einträge mitgelöscht.
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
    jahr = db.Column(
        db.Integer, nullable=False
    )  # Für welches Jahr gilt dieser Eintrag?

    # Boolean-Felder (True/False) für die verschiedenen Postarten.
    postkarte = db.Column(db.Boolean, default=False)
    kalender = db.Column(db.Boolean, default=False)
    email_versand = db.Column(db.Boolean, default=False)
    speziell = db.Column(db.Boolean, default=False)

    # Verknüpfung zum Kunden.
    kunde_id = db.Column(db.Integer, db.ForeignKey("kunde.id"), nullable=False)

    def __repr__(self):
        return f"<Weihnachtspost {self.kunde.nachname} ({self.jahr})>"
