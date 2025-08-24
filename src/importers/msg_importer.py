# src/importers/msg_importer.py
import os
import re
import subprocess
import tempfile
import shutil

def parse_msg_file(file_path):
    """
    Extrahiert den Inhalt einer .msg-Datei, parst ihn und gibt die strukturierten Daten zurück.
    """
    temp_dir = tempfile.mkdtemp(prefix="msg_extract_")
    
    try:
        # Führe das extract_msg-Tool aus
        subprocess.run(
            ["python", "-m", "extract_msg", "--out", temp_dir, file_path],
            capture_output=True, text=True, check=False
        )
        
        # Finde die extrahierte message.txt
        message_txt_path = os.path.join(temp_dir, 'message.txt')
        if not os.path.exists(message_txt_path):
             # Versuche es in einem Unterordner (manchmal wird einer erstellt)
            for root, _, files in os.walk(temp_dir):
                if 'message.txt' in files:
                    message_txt_path = os.path.join(root, 'message.txt')
                    break
        
        if not os.path.exists(message_txt_path):
            return {"error": "Konnte 'message.txt' nicht aus der MSG-Datei extrahieren."}

        with open(message_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        return [_parse_message_text(text)] # In eine Liste packen für Konsistenz

    finally:
        shutil.rmtree(temp_dir)


def _parse_message_text(text):
    """Parst den reinen Text aus einer .msg-Datei."""
    data = {}

    # Extrahiere die Felder mit Regex
    data['Vorname'] = _search_field(r"First Name:\s*(.*)", text)
    data['Nachname'] = _search_field(r"Last Name:\s*(.*)", text)
    data['Anrede'] = _search_field(r"Full Name:\s*(Herr|Frau)", text)
    data['Position'] = _search_field(r"Job Title:\s*(.*)", text)
    data['Firma'] = _search_field(r"Company:\s*(.*)", text)
    data['Telefon (geschäftlich)'] = _search_field(r"Business:\s*([+\d\s()/.-]+)", text)
    data['Telefon (privat)'] = _search_field(r"Home:\s*([+\d\s()/.-]+)", text)
    data['Mobilnummer'] = _search_field(r"Mobile:\s*([+\d\s()/.-]+)", text)
    data['Faxnummer'] = _search_field(r"Fax:\s*([+\d\s()/.-]+)", text)
    data['E-Mail'] = _search_field(r"Email:\s*([\w\.-]+@[\w\.-]+)", text)

    # Adress-Parsing
    business_address = _search_field(r"Business Address:\s*(.*)", text)
    if business_address:
        addr_match = re.match(r"(.+),\s*(\d{4,5})\s+(.+)", business_address)
        if addr_match:
            data['Straße'] = addr_match.group(1).strip()
            data['Postleitzahl'] = addr_match.group(2).strip()
            data['Ort'] = addr_match.group(3).strip()
        else:
            data['Straße'] = business_address

    return {k: v for k, v in data.items() if v} # Nur gefüllte Felder zurückgeben

def _search_field(pattern, text):
    """Hilfsfunktion für die Regex-Suche."""
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""