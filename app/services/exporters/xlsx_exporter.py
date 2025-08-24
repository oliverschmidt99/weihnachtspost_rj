# src/exporters/xlsx_exporter.py
import openpyxl
import io

def generate_xlsx(kontakte, eigenschaften):
    """Erstellt eine Excel-Datei (.xlsx) im Speicher."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    headers = [e['name'] for e in eigenschaften]
    sheet.append(headers)
    
    for kontakt in kontakte:
        row = [kontakt['daten'].get(h, '') for h in headers]
        sheet.append(row)
        
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()