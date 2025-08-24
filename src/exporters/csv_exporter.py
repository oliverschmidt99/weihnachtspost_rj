# src/exporters/csv_exporter.py
import csv
import io

def generate_csv(kontakte, eigenschaften):
    """Erstellt eine CSV-Datei im Speicher."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [e['name'] for e in eigenschaften]
    writer.writerow(headers)
    
    for kontakt in kontakte:
        row = [str(kontakt['daten'].get(h, '')) for h in headers]
        writer.writerow(row)
        
    output.seek(0)
    return output.getvalue()