# app/routes/kontakte.py
import json
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import joinedload, subqueryload
from ..models import db, Vorlage, Kontakt, Gruppe, Eigenschaft

bp = Blueprint('kontakte', __name__, url_prefix='/kontakte')

@bp.route("/")
def auflisten():
    # KORRIGIERTE UND OPTIMIERTE DATENBANKABFRAGE
    vorlagen_query = Vorlage.query.options(
        subqueryload(Vorlage.kontakte),
        subqueryload(Vorlage.gruppen).subqueryload(Gruppe.eigenschaften)
    ).order_by(Vorlage.name).all()
    
    vorlagen_data = []
    for v in vorlagen_query:
        vorlage_dict = {
            "id": v.id,
            "name": v.name,
            "eigenschaften": [{"id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for g in v.gruppen for e in g.eigenschaften],
            "kontakte": [{"id": k.id, "daten": k.get_data()} for k in v.kontakte],
            "gruppen": [{"id": g.id, "name": g.name, "eigenschaften": [{"id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]} for g in v.gruppen]
        }
        vorlagen_data.append(vorlage_dict)

    return render_template("kontakte_liste.html", vorlagen_for_json=json.dumps(vorlagen_data))

@bp.route("/editor", methods=["GET", "POST"])
def editor():
    kontakt_id = request.args.get('kontakt_id', type=int)
    vorlage_id = request.args.get('vorlage_id', type=int)
    
    if kontakt_id:
        kontakt = db.session.get(Kontakt, kontakt_id)
        vorlage = kontakt.vorlage
        action_url = url_for('kontakte.editor', kontakt_id=kontakt.id)
    elif vorlage_id:
        kontakt = None
        vorlage = db.session.get(Vorlage, vorlage_id)
        action_url = url_for('kontakte.editor', vorlage_id=vorlage.id)
    else:
        return redirect(url_for('vorlagen.verwalten'))

    if request.method == "POST":
        form_daten = request.form.to_dict()
        if kontakt:
            kontakt.set_data(form_daten)
        else:
            neuer_kontakt = Kontakt(vorlage_id=vorlage.id)
            neuer_kontakt.set_data(form_daten)
            db.session.add(neuer_kontakt)
        db.session.commit()
        return redirect(url_for('kontakte.auflisten'))
        
    vorlage_for_json = {"id": vorlage.id, "name": vorlage.name, "gruppen": [{"id": g.id, "name": g.name, "eigenschaften": [{"id": e.id, "name": e.name, "datentyp": e.datentyp, "optionen": e.optionen} for e in g.eigenschaften]} for g in vorlage.gruppen]}
    kontakt_daten_for_json = kontakt.get_data() if kontakt else {}
    
    return render_template("kontakt_editor.html", 
                           action_url=action_url,
                           kontakt=kontakt,
                           vorlage_for_json=json.dumps(vorlage_for_json), 
                           kontakt_daten_for_json=json.dumps(kontakt_daten_for_json))

@bp.route("/loeschen/<int:kontakt_id>", methods=["POST"])
def loeschen(kontakt_id):
    kontakt = db.session.get(Kontakt, kontakt_id)
    if kontakt:
        db.session.delete(kontakt)
        db.session.commit()
    return redirect(url_for("kontakte.auflisten"))