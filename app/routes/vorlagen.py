# app/routes/vorlagen.py
import json
import os
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    jsonify,
    redirect,
    current_app,
)
from werkzeug.utils import secure_filename
from ..models import db, Vorlage, Gruppe, Eigenschaft

bp = Blueprint("vorlagen", __name__, url_prefix="/vorlagen")


@bp.route("/")
def verwalten():
    vorlagen_liste = Vorlage.query.order_by(
        Vorlage.is_standard.desc(), Vorlage.name
    ).all()
    return render_template("vorlagen_verwaltung.html", vorlagen=vorlagen_liste)


@bp.route("/editor")
def editor():
    vorlage_id = request.args.get("vorlage_id", type=int)
    all_vorlagen = Vorlage.query.all()
    if vorlage_id:
        vorlage = db.session.get(Vorlage, vorlage_id)
        vorlage_data = {
            "id": vorlage.id,
            "name": vorlage.name,
            "is_standard": vorlage.is_standard,
            "gruppen": [
                {
                    "name": g.name,
                    "eigenschaften": [
                        {"name": e.name, "datentyp": e.datentyp, "optionen": e.optionen}
                        for e in g.eigenschaften
                    ],
                }
                for g in vorlage.gruppen
            ],
        }
        action_url = url_for("vorlagen.speichern", vorlage_id=vorlage.id)
    else:
        vorlage_data = {
            "name": "",
            "gruppen": [{"name": "Allgemein", "eigenschaften": []}],
            "is_standard": False,
        }
        action_url = url_for("vorlagen.speichern")

    all_vorlagen_data = [{"id": v.id, "name": v.name} for v in all_vorlagen]

    return render_template(
        "vorlage_editor.html",
        vorlage_data=json.dumps(vorlage_data),
        action_url=action_url,
        all_vorlagen_data=json.dumps(all_vorlagen_data),
    )


@bp.route("/speichern", methods=["POST"])
@bp.route("/speichern/<int:vorlage_id>", methods=["POST"])
def speichern(vorlage_id=None):
    data = request.get_json()

    existing_vorlage = Vorlage.query.filter(Vorlage.name == data["name"]).first()
    if existing_vorlage and (vorlage_id is None or existing_vorlage.id != vorlage_id):
        return (
            jsonify(
                {
                    "error": f"Eine Vorlage mit dem Namen '{data['name']}' existiert bereits."
                }
            ),
            400,
        )

    if vorlage_id:
        vorlage = db.session.get(Vorlage, vorlage_id)
        if vorlage.is_standard:
            return (
                jsonify(
                    {
                        "error": "Standard-Vorlagen können nicht direkt gespeichert werden. Bitte 'Speichern als' verwenden."
                    }
                ),
                400,
            )

        vorlage.name = data["name"]

        # KORREKTUR: Alte Gruppen werden hier zuverlässig gelöscht.
        # Wir iterieren über eine Kopie der Liste, um alle Gruppen-Objekte
        # sicher aus der Session zu entfernen. Die Kaskadierung in den Models
        # sorgt dafür, dass auch alle zugehörigen Eigenschaften gelöscht werden.
        for gruppe in list(vorlage.gruppen):
            db.session.delete(gruppe)

    else:
        vorlage = Vorlage(name=data["name"], is_standard=False)
        db.session.add(vorlage)

    db.session.flush()

    # Neue Gruppen und Eigenschaften werden hinzugefügt
    for gruppe_data in data.get("gruppen", []):
        gruppe = Gruppe(name=gruppe_data["name"], vorlage_id=vorlage.id)
        db.session.add(gruppe)
        db.session.flush()
        for eigenschaft_data in gruppe_data.get("eigenschaften", []):
            eigenschaft = Eigenschaft(
                name=eigenschaft_data["name"],
                datentyp=eigenschaft_data["datentyp"],
                optionen=eigenschaft_data.get("optionen", ""),
                gruppe_id=gruppe.id,
            )
            db.session.add(eigenschaft)

    if not vorlage.is_standard:
        try:
            user_vorlagen_path = os.path.join(
                current_app.root_path, "..", "data", "user_vorlagen"
            )
            os.makedirs(user_vorlagen_path, exist_ok=True)

            filename = f"user_{secure_filename(vorlage.name).lower()}.json"
            filepath = os.path.join(user_vorlagen_path, filename)

            json_data = {"name": vorlage.name, "gruppen": data.get("gruppen", [])}

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            current_app.logger.error(
                f"Konnte JSON für Vorlage '{vorlage.name}' nicht speichern: {e}"
            )

    db.session.commit()
    return jsonify({"redirect_url": url_for("vorlagen.verwalten")})


@bp.route("/loeschen/<int:vorlage_id>", methods=["POST"])
def loeschen(vorlage_id):
    vorlage = db.session.get(Vorlage, vorlage_id)
    if vorlage:
        if vorlage.is_standard:
            return redirect(url_for("vorlagen.verwalten"))

        try:
            user_vorlagen_path = os.path.join(
                current_app.root_path, "..", "data", "user_vorlagen"
            )
            filename = f"user_{secure_filename(vorlage.name).lower()}.json"
            filepath = os.path.join(user_vorlagen_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            current_app.logger.error(
                f"Konnte JSON-Datei für Vorlage '{vorlage.name}' nicht löschen: {e}"
            )

        db.session.delete(vorlage)
        db.session.commit()

    return redirect(url_for("vorlagen.verwalten"))
