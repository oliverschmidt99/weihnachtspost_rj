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
    if 'files' not in request.files:
        return jsonify({"error": "Keine Dateien im Request gefunden."}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({"error": "Keine Dateien ausgewählt."}), 400
    
    all_records = []
    
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Dateityp '{file_ext}' nicht erlaubt."}), 400

        try:
            # Wichtig: Dateiobjekt zurück zum Anfang setzen, falls es mehrfach gelesen wird
            file.seek(0)
            data = importer_service.import_file(file)
            if isinstance(data, dict) and "error" in data:
                return jsonify(data), 400
            all_records.extend(data)
        except Exception as e:
            return jsonify({"error": f"Fehler beim Verarbeiten der Datei '{file.filename}': {str(e)}"}), 500

    if not all_records:
        return jsonify({"error": "Keine Daten in den Dateien gefunden."}), 400

    # Sammle alle eindeutigen Spaltennamen aus allen Dateien
    all_headers = set()
    for record in all_records:
        all_headers.update(record.keys())
        
    preview_data = all_records[:5]
    return jsonify({"headers": list(all_headers), "preview_data": preview_data, "original_data": all_records})

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
            {"name": g.name, "eigenschaften": [{"name": e.name} for e in g.eigenschaften]} 
            for g in vorlage_model.gruppen
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