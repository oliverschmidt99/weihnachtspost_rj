# src/importer.py
import os
import csv
import vobject
import openpyxl
from werkzeug.utils import secure_filename
from flask import current_app

def parse_vcf(file_path):
    """Liest eine .vcf-Datei und extrahiert Kontaktinformationen."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        vcard = vobject.readOne(f.read())
    
    data = {}
    if hasattr(vcard, 'n'):
        data['Vorname'] = vcard.n.value.given
        data['Nachname'] = vcard.n.value.family
    if hasattr(vcard, 'fn'):
        data['Name'] = vcard.fn.value
    if hasattr(vcard, 'org'):
        data['Firma'] = vcard.org.value[0] if vcard.org.value else ''
    if hasattr(vcard, 'title'):
        data['Position'] = vcard.title.value
    if hasattr(vcard, 'tel'):
        for tel in vcard.tel_list:
            if 'WORK' in tel.type_param:
                data['Telefon (geschäftlich)'] = tel.value
            elif 'HOME' in tel.type_param:
                data['Telefon (privat)'] = tel.value
            elif 'CELL' in tel.type_param:
                data['Mobilnummer'] = tel.value
    if hasattr(vcard, 'email'):
        data['E-Mail'] = vcard.email.value
    if hasattr(vcard, 'url'):
        data['Website'] = vcard.url.value
    if hasattr(vcard, 'adr'):
        addr = vcard.adr.value
        data['Straße'] = addr.street
        data['Ort'] = addr.city
        data['Postleitzahl'] = addr.code
        data['Land'] = addr.country
    return [data]

def parse_csv_txt(file_path, delimiter=','):
    """Liest CSV- oder TXT-Dateien."""
    records = []
    with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            records.append(row)
    return records

def parse_xlsx(file_path):
    """Liest .xlsx-Dateien (Excel)."""
    records = []
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]
    for row in sheet.iter_rows(min_row=2, values_only=True):
        records.append(dict(zip(headers, row)))
    return records

def import_file(file_storage):
    """Hauptfunktion, die den Dateityp erkennt und den passenden Parser aufruft."""
    filename = secure_filename(file_storage.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Speichere die Datei temporär
    temp_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, filename)
    file_storage.save(file_path)

    try:
        if file_ext == '.vcf':
            return parse_vcf(file_path)
        elif file_ext == '.csv':
            return parse_csv_txt(file_path, delimiter=',')
        elif file_ext == '.txt':
            return parse_csv_txt(file_path, delimiter='\t') # Annahme: Tabulator als Trennzeichen
        elif file_ext == '.xlsx':
            return parse_xlsx(file_path)
        # Hier können bei Bedarf weitere Parser für .msg, .oft, .rtf integriert werden
        else:
            return {"error": f"Dateityp {file_ext} wird für den Import noch nicht unterstützt."}
    finally:
        # Lösche die temporäre Datei
        if os.path.exists(file_path):
            os.remove(file_path)