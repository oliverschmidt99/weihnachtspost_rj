# app/routes/api.py
import json
import os
from flask import Blueprint, jsonify, send_from_directory, request, current_app
from ..models import db, Kontakt

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/attribute-suggestions")
def attribute_suggestions():
    return send_from_directory("../data", "attribute_suggestions.json")


@bp.route("/selection-options")
def selection_options():
    # Stellt sicher, dass die Datei existiert, und erstellt sie ggf.
    options_path = os.path.join(
        current_app.root_path, "..", "data", "selection_options.json"
    )
    if not os.path.exists(options_path):
        with open(options_path, "w", encoding="utf-8") as f:
            json.dump({"options": []}, f)
    return send_from_directory("../data", "selection_options.json")


@bp.route("/selection-options", methods=["POST"])
def save_selection_options():
    """Speichert die übergebenen Daten in die selection_options.json."""
    data = request.get_json()
    if not data or "options" not in data:
        return jsonify({"success": False, "error": "Ungültige Daten"}), 400

    try:
        options_path = os.path.join(
            current_app.root_path, "..", "data", "selection_options.json"
        )
        with open(options_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify(
            {"success": True, "message": "Auswahllisten erfolgreich gespeichert."}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/kontakte-by-vorlage/<int:vorlage_id>")
def get_kontakte_by_vorlage(vorlage_id):
    kontakte = Kontakt.query.filter_by(vorlage_id=vorlage_id).all()
    result = []
    for k in kontakte:
        data = k.get_data()
        display_name = (
            data.get("Name")
            or f"{data.get('Vorname', '')} {data.get('Nachname', '')}".strip()
            or data.get("Firmenname", f"Kontakt ID: {k.id}")
        )
        result.append({"id": k.id, "display_name": display_name})
    return jsonify(result)


@bp.route("/kontakt/<int:kontakt_id>/update", methods=["POST"])
def update_kontakt_field(kontakt_id):
    kontakt = db.session.get(Kontakt, kontakt_id)
    if not kontakt:
        return jsonify({"success": False, "error": "Kontakt nicht gefunden"}), 404

    data = request.get_json()
    field_name = data.get("field")
    new_value = data.get("value")
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
    vorlage_id = data.get("vorlage_id")
    kontakt_daten = data.get("daten")
    if not vorlage_id or kontakt_daten is None:
        return jsonify({"success": False, "error": "Fehlende Daten"}), 400

    neuer_kontakt = Kontakt(vorlage_id=vorlage_id)
    neuer_kontakt.set_data(kontakt_daten)
    db.session.add(neuer_kontakt)
    db.session.commit()

    response_data = {"id": neuer_kontakt.id, "daten": neuer_kontakt.get_data()}
    return jsonify({"success": True, "kontakt": response_data})


@bp.route("/kontakte/bulk-delete", methods=["POST"])
def bulk_delete_kontakte():
    data = request.get_json()
    kontakt_ids = data.get("ids")

    if not kontakt_ids:
        return jsonify({"success": False, "error": "Keine IDs angegeben."}), 400

    try:
        Kontakt.query.filter(Kontakt.id.in_(kontakt_ids)).delete(
            synchronize_session=False
        )
        db.session.commit()
        return jsonify(
            {"success": True, "message": f"{len(kontakt_ids)} Kontakte gelöscht."}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
