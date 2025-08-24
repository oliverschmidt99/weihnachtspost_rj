# src/importers/xlsx_importer.py
import openpyxl

def parse_xlsx(file_path):
    """Liest eine .xlsx-Datei und gibt eine Liste von Dictionaries zurück."""
    records = []
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    # Lese die Kopfzeile
    headers = [cell.value for cell in sheet[1]]
    
    # Lese die Datenzeilen
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if any(row): # Ignoriere komplett leere Zeilen
            records.append(dict(zip(headers, row)))
            
    return records