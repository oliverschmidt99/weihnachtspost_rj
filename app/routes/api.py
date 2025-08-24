# app/routes/api.py
from flask import Blueprint, jsonify, send_from_directory, request
from ..models import db, Kontakt

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/attribute-suggestions")
def attribute_suggestions():
    return send_from_directory('../data', 'attribute_suggestions.json')

@bp.route("/selection-options")
def selection_options():
    return send_from_directory('../data', 'selection_options.json')

@bp.route("/kontakte-by-vorlage/<int:vorlage_id>")
def get_kontakte_by_vorlage(vorlage_id):
    kontakte = Kontakt.query.filter_by(vorlage_id=vorlage_id).all()
    result = []
    for k in kontakte:
        data = k.get_data()
        display_name = data.get('Name') or f"{data.get('Vorname', '')} {data.get('Nachname', '')}".strip() or data.get('Firmenname', f"Kontakt ID: {k.id}")
        result.append({"id": k.id, "display_name": display_name})
    return jsonify(result)

@bp.route("/kontakt/<int:kontakt_id>/update", methods=["POST"])
def update_kontakt_field(kontakt_id):
    kontakt = db.session.get(Kontakt, kontakt_id)
    if not kontakt: 
        return jsonify({"success": False, "error": "Kontakt nicht gefunden"}), 404
    
    data = request.get_json()
    field_name = data.get('field')
    new_value = data.get('value')
    if field_name is None:
        return jsonify({"success": False, "error": "Fehlende Daten"}), 400
    
    kontakt_daten = kontakt.get_data()
    kontakt_daten[field_name] = new_value
    kontakt.set_data(kontakt_daten)
    db.session.commit()
    return jsonify({"success": True, "message": "Feld aktualisiert"})
    
@bp.route("/kontakt/neu", methods=["POST"])
def create_kontakt():
    data = request.get_json()
    vorlage_id = data.get('vorlage_id')
    kontakt_daten = data.get('daten')
    if not vorlage_id or kontakt_daten is None:
        return jsonify({"success": False, "error": "Fehlende Daten"}), 400
    
    neuer_kontakt = Kontakt(vorlage_id=vorlage_id)
    neuer_kontakt.set_data(kontakt_daten)
    db.session.add(neuer_kontakt)
    db.session.commit()
    
    response_data = {"id": neuer_kontakt.id, "daten": neuer_kontakt.get_data()}
    return jsonify({"success": True, "kontakt": response_data})