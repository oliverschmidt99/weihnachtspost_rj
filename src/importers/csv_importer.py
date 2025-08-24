# src/importers/csv_importer.py
import csv

def parse_csv_txt(file_path, delimiter=','):
    """Liest CSV- oder TXT-Dateien und gibt eine Liste von Dictionaries zurück."""
    records = []
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                records.append(row)
    except Exception as e:
        # Fallback für andere Kodierungen, falls UTF-8 fehlschlägt
        with open(file_path, mode='r', encoding='latin-1', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                records.append(row)
    return records