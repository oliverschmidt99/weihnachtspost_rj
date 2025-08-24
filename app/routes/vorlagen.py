# app/routes/vorlagen.py
import json
from flask import Blueprint, render_template, request, url_for, jsonify, redirect
from ..models import db, Vorlage, Gruppe, Eigenschaft

bp = Blueprint('vorlagen', __name__, url_prefix='/vorlagen')

@bp.route("/")
def verwalten():
    vorlagen_liste = Vorlage.query.order_by(Vorlage.name).all()
    return render_template("vorlagen_verwaltung.html", vorlagen=vorlagen_liste)

@bp.route("/editor")
def editor():
    vorlage_id = request.args.get('vorlage_id', type=int)
    all_vorlagen = Vorlage.query.all()
    if vorlage_id:
        vorlage = db.session.get(Vorlage, vorlage_id)
        vorlage_data = {
            "name": vorlage.name,
            "gruppen": [
                {"name": g.name, "eigenschaften": [{"name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]} 
                for g in vorlage.gruppen
            ]
        }
        action_url = url_for('vorlagen.speichern', vorlage_id=vorlage.id)
    else:
        vorlage_data = {"name": "", "gruppen": [{"name": "Allgemein", "eigenschaften": []}]}
        action_url = url_for('vorlagen.speichern')
    
    all_vorlagen_data = [{"id": v.id, "name": v.name} for v in all_vorlagen]
    
    return render_template("vorlage_editor.html", 
                           vorlage_data=json.dumps(vorlage_data), 
                           action_url=action_url, 
                           all_vorlagen_data=json.dumps(all_vorlagen_data))

@bp.route("/speichern", methods=["POST"])
@bp.route("/speichern/<int:vorlage_id>", methods=["POST"])
def speichern(vorlage_id=None):
    data = request.get_json()
    if vorlage_id:
        vorlage = db.session.get(Vorlage, vorlage_id)
        vorlage.name = data['name']
        Gruppe.query.filter_by(vorlage_id=vorlage_id).delete()
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
    return jsonify({"redirect_url": url_for('vorlagen.verwalten')})

@bp.route("/loeschen/<int:vorlage_id>", methods=["POST"])
def loeschen(vorlage_id):
    vorlage = db.session.get(Vorlage, vorlage_id)
    if vorlage:
        db.session.delete(vorlage)
        db.session.commit()
    return redirect(url_for("vorlagen.verwalten"))