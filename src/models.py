# src/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Mitarbeiter(db.Model):
    __tablename__ = 'mitarbeiter'
    id = db.Column(db.Integer, primary_key=True)
    
    # Angepasste Felder für mehrere Einträge
    tag = db.Column(db.Text)
    titel = db.Column(db.Text)
    
    # Neue Felder
    geburtsdatum = db.Column(db.Date)
    notizen = db.Column(db.Text)
    farbe = db.Column(db.String(7), default="#A0C4FF") # Farbfeld hinzugefügt
    
    # Personalisierung
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)
    
    # Position & Kontakt
    firma = db.Column(db.String(150))
    position = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefon = db.Column(db.String(50))
    
    # Adresse
    strasse = db.Column(db.String(200))
    hausnummer = db.Column(db.String(20))
    plz = db.Column(db.String(20))
    ort = db.Column(db.String(100))
    land = db.Column(db.String(100), default="Deutschland")
    
    kunden = db.relationship("Kunde", backref="mitarbeiter", lazy=True)

    __table_args__ = ( db.UniqueConstraint('email', name='uq_mitarbeiter_email'), )

class Kunde(db.Model):
    __tablename__ = 'kunde'
    id = db.Column(db.Integer, primary_key=True)

    # Angepasste Felder
    tag = db.Column(db.Text)
    titel = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default="Neu") # Zustand/Status zusammengefasst

    # Neue Felder
    geburtsdatum = db.Column(db.Date)
    notizen = db.Column(db.Text)
    
    # Personalisierung
    anrede = db.Column(db.String(20))
    vorname = db.Column(db.String(100))
    nachname = db.Column(db.String(100), nullable=False)
    
    # Firma & Kontakt
    firma = db.Column(db.String(150))
    position = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefon = db.Column(db.String(50))
    
    # Adresse
    strasse = db.Column(db.String(200))
    hausnummer = db.Column(db.String(20))
    plz = db.Column(db.String(20))
    ort = db.Column(db.String(100))
    land = db.Column(db.String(100), default="Deutschland")
    
    # Kundenspezifische Felder
    bevorzugter_kontaktweg = db.Column(db.String(100))
    mitarbeiter_id = db.Column(db.Integer, db.ForeignKey("mitarbeiter.id", ondelete="SET NULL"), nullable=True)
    benachrichtigungen = db.relationship("Benachrichtigung", backref="kunde", lazy=True, cascade="all, delete-orphan")

    __table_args__ = ( db.UniqueConstraint('email', name='uq_kunde_email'), )

class Benachrichtigung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jahr = db.Column(db.Integer, nullable=False)
    brief = db.Column(db.Boolean, default=False)
    kalender = db.Column(db.Boolean, default=False)
    email_versand = db.Column(db.Boolean, default=False)
    speziell = db.Column(db.Boolean, default=False)
    kunde_id = db.Column(db.Integer, db.ForeignKey("kunde.id"), nullable=False)