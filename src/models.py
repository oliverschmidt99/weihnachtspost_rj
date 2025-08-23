# src/models.py
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Vorlage(db.Model):
    __tablename__ = 'vorlage'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    gruppen = db.relationship('Gruppe', backref='vorlage', lazy=True, cascade="all, delete-orphan")
    kontakte = db.relationship('Kontakt', backref='vorlage', lazy=True, cascade="all, delete-orphan")
    
    @property
    def eigenschaften(self):
        """Gibt eine flache Liste aller Eigenschaften dieser Vorlage zurück."""
        props = []
        for gruppe in self.gruppen:
            props.extend(gruppe.eigenschaften)
        return props

class Gruppe(db.Model):
    __tablename__ = 'gruppe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vorlage_id = db.Column(db.Integer, db.ForeignKey('vorlage.id'), nullable=False)
    eigenschaften = db.relationship('Eigenschaft', backref='gruppe', lazy=True, cascade="all, delete-orphan")

class Eigenschaft(db.Model):
    __tablename__ = 'eigenschaft'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    datentyp = db.Column(db.String(50), nullable=False) # z.B. Text, Zahl, Datum, Boolean, Auswahl
    optionen = db.Column(db.Text) # z.B. für Auswahl: "Option1,Option2,Option3"
    gruppe_id = db.Column(db.Integer, db.ForeignKey('gruppe.id'), nullable=False)

class Kontakt(db.Model):
    __tablename__ = 'kontakt'
    id = db.Column(db.Integer, primary_key=True)
    vorlage_id = db.Column(db.Integer, db.ForeignKey('vorlage.id'), nullable=False)
    # Speichert die dynamischen Daten als JSON-formatierter String
    daten = db.Column(db.Text, nullable=False, default='{}')

    def get_data(self):
        """Lädt die JSON-Daten als Python-Dictionary."""
        return json.loads(self.daten or '{}')

    def set_data(self, data_dict):
        """Speichert ein Python-Dictionary als JSON-String."""
        self.daten = json.dumps(data_dict)