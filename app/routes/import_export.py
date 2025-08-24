# app/routes/import_export.py
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, flash, url_for, Response
from ..models import db, Vorlage, Kontakt
from ..services import importer_service, exporter_service

bp = Blueprint('import_export', __name__)
ALLOWED_EXTENSIONS = {"csv", "msg", "oft", "txt", "vcf", "xlsx"}

@bp.route("/import/upload", methods=["POST"])
def upload_import_file():
    if 'file' not in request.files: 
        return jsonify({"error": "Keine Datei im Request gefunden."}), 400
    file = request.files['file']
    if file.filename == '': 
        return jsonify({"error": "Keine Datei ausgewählt."}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Dateityp nicht erlaubt."}), 400

    try:
        data = importer_service.import_file(file)
        if isinstance(data, dict) and "error" in data:
            return jsonify(data), 400
        
        headers = list(data[0].keys()) if data else []
        preview_data = data[:5]
        return jsonify({"headers": headers, "preview_data": preview_data, "original_data": data})
    except Exception as e:
        return jsonify({"error": f"Fehler beim Verarbeiten der Datei: {str(e)}"}), 500

@bp.route("/import/finalize", methods=["POST"])
def finalize_import():
    data = request.get_json()
    vorlage_id = data.get('vorlage_id')
    mappings = data.get('mappings')
    original_data = data.get('original_data')

    if not all([vorlage_id, mappings, original_data]):
        return jsonify({"success": False, "error": "Fehlende Daten für den Import."}), 400
    
    vorlage = db.session.get(Vorlage, vorlage_id)
    if not vorlage: 
        return jsonify({"success": False, "error": "Vorlage nicht gefunden."}), 404

    count = 0
    for row in original_data:
        new_kontakt_data = {
            vorlage_prop: row.get(import_header) 
            for import_header, vorlage_prop in mappings.items() 
            if vorlage_prop
        }
        if new_kontakt_data:
            kontakt = Kontakt(vorlage_id=vorlage_id)
            kontakt.set_data(new_kontakt_data)
            db.session.add(kontakt)
            count += 1
            
    db.session.commit()
    flash(f"{count} Kontakte wurden erfolgreich importiert.", "success")
    return jsonify({"success": True, "redirect_url": url_for('kontakte.auflisten')})

@bp.route("/export/<int:vorlage_id>/<string:file_format>")
def export_data(vorlage_id, file_format):
    vorlage_model = db.session.get(Vorlage, vorlage_id)
    if not vorlage_model:
        return "Vorlage nicht gefunden", 404
    
    kontakte_data = [{"id": k.id, "daten": k.get_data()} for k in vorlage_model.kontakte]
    vorlage_struktur = {
        "name": vorlage_model.name,
        "gruppen": [
            {
                "name": g.name,
                "eigenschaften": [{"name": e.name} for e in g.eigenschaften]
            } for g in vorlage_model.gruppen
        ]
    }
    
    content, mimetype = exporter_service.export_data(file_format, kontakte_data, vorlage_struktur)
    
    if not content:
        return "Ungültiges Export-Format", 400
        
    filename = f"{vorlage_model.name}_export_{datetime.now().strftime('%Y-%m-%d')}.{file_format}"
        
    return Response(
        content,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )